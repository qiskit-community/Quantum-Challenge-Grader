from typeguard import typechecked
from typing import List

from qiskit import transpile, QuantumCircuit, generate_preset_pass_manager
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.circuit.library import QuantumVolume, QAOAAnsatz
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.fake_provider import FakeBrisbane
import rustworkx
import rustworkx as rx
import numpy as np
from qiskit_aer import AerSimulator
from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2025'

# TODO!!!! 

@typechecked
def grade_lab2_ex1(
    find_best_metrics: callable
) -> None:
    service = QiskitRuntimeService()
    backend = service.backend("ibm_brisbane")
    properties = backend.properties()
    num_qubits = backend.num_qubits
    coupling_map = backend.coupling_map
    index_t1_max, max_t1 = max(
        ((i, properties.t1(i)) for i in range(num_qubits)), key=lambda x: x[1]
    )
    index_t2_max, max_t2 = max(
        ((i, properties.t2(i)) for i in range(num_qubits)), key=lambda x: x[1]
    )
    index_min_x_error, min_x_error = min(
        ((i, properties.gate_error(qubits=i, gate="x")) for i in range(num_qubits)),
        key=lambda x: x[1],
    )
    index_min_readout, min_readout = min(
        ((i, properties.readout_error(i)) for i in range(num_qubits)),
        key=lambda x: x[1],
    )
    min_ecr_pair, min_ecr_error = min(
        ((pair, properties.gate_error(gate="ecr", qubits=pair)) for pair in coupling_map),
        key=lambda x: x[1],
    )
    key_values = [
        [index_t1_max, max_t1],
        [index_t2_max, max_t2],
        [index_min_x_error, min_x_error],
        [index_min_readout, min_readout],
        [min_ecr_pair, min_ecr_error],
    ]
    solutions=find_best_metrics(backend)
    grade({
        'solutions': solutions,
        'key_values': key_values,
    }, 'lab2-ex1', _challenge_id)


def prepare_list_from_graph(graph) -> list[tuple[str, float]]:
    # Convert the graph to Pauli list.
    pauli_list = []
    for edge in list(graph.edge_list()):
        paulis = ["I"] * len(graph)
        paulis[edge[0]], paulis[edge[1]] = "Z", "Z"
        weight = graph.get_edge_data(edge[0], edge[1])
        pauli_list.append(("".join(paulis)[::-1], weight))
    return pauli_list


@typechecked
def grade_lab2_ex2(
    graph_to_Pauli: callable
) -> None:
    # Define the graph:
    seed = 43
    n = 5
    graph = rx.PyGraph()
    graph.add_nodes_from(np.arange(0, n, 1))
    generic_backend = GenericBackendV2(n, seed=seed)
    weights = 1
    graph.add_edges_from([(edge[0], edge[1], weights) for edge in generic_backend.coupling_map][:-1])
    prepared_list = prepare_list_from_graph(graph)
    max_cut_paulis = graph_to_Pauli(graph)
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    grade({
        'cost_hamiltonian': cost_hamiltonian,
        'prepared_list': prepared_list,
    }, 'lab2-ex2', _challenge_id)


#TODO obscuse
def prepare_backend(backend, circuit):
    properties = backend.properties()
    n = len({circuit.qubits.index(q) for instr in circuit.data for q in instr.qubits})
    qubit_layout = list(circuit.layout.initial_layout.get_physical_bits().keys())[:n]
    # We define various lists of metrics for all the qubits of the backend
    # Readout error
    readout_error = []
    for i in qubit_layout:
        readout_error.append(properties.readout_error(i))
    acc_readout_error = sum(readout_error)
    # Defining two qubit gates
    if "ecr" in (backend.configuration().basis_gates):
        two_qubit_gate = "ecr"
    elif "cz" in (backend.configuration().basis_gates):
        two_qubit_gate = "cz"
    # Initializing quantities
    acc_single_qubit_error = 0
    acc_two_qubit_error = 0
    single_qubit_gate_count = 0
    two_qubit_gate_count = 0
    # Looping over the instructions to account for the errors
    for instruction in circuit.data:
        if instruction.operation.num_qubits == 1 and instruction.name !='measure':
            index = instruction.qubits[0]._index
            acc_single_qubit_error += properties.gate_error(gate=instruction.name, qubits=index)
            single_qubit_gate_count += 1
        elif instruction.operation.num_qubits == 2:
            pair = [instruction.qubits[0]._index, instruction.qubits[1]._index]
            acc_two_qubit_error += properties.gate_error(gate=two_qubit_gate, qubits=pair)
            two_qubit_gate_count += 1
    acc_total_error = acc_two_qubit_error + acc_single_qubit_error + acc_readout_error
    backend = [
        acc_total_error,
        acc_two_qubit_error,
        acc_single_qubit_error,
        acc_readout_error,
        single_qubit_gate_count,
        two_qubit_gate_count,
    ]
    return backend


@typechecked
def grade_lab2_ex3(
    accumulated_errors: callable
) -> None:
    service=QiskitRuntimeService()
    real_backends = [
    service.backend("ibm_brisbane"),
    service.backend("ibm_sherbrooke"),
    service.backend("ibm_torino")]
    seed=43
    noisy_fake_backends = []
    for backend in real_backends:
        noisy_fake_backends.append(AerSimulator.from_backend(backend, seed_simulator=seed))
    max_cut_paulis = [
        ('IIIZZ', 1),
        ('IIIZZ', 1),
        ('IIZIZ', 1),
        ('IIZIZ', 1),
        ('IZIIZ', 1),
        ('IZIIZ', 1),
        ('ZIIIZ', 1),
        ('ZIIIZ', 1),
        ('IIZZI', 1),
        ('IIZZI', 1),
        ('IZIZI', 1),
        ('IZIZI', 1),
        ('ZIIZI', 1),
        ('ZIIZI', 1),
        ('IZZII', 1),
        ('IZZII', 1),
        ('ZIZII', 1),
        ('ZIZII', 1),
        ('ZZIII', 1)
    ]
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)
    circuit.measure_all()
    backend = GenericBackendV2(5, seed=43)
    pm = generate_preset_pass_manager(optimization_level=2, backend=backend)
    qaoa_circuit = pm.run(circuit)
    prepared_backends=[]
    circuit_list=[]
    results_list=[]
    for noisy_fake_backend in noisy_fake_backends:
        pm = generate_preset_pass_manager(
            backend=noisy_fake_backend,
            optimization_level=3,
            seed_transpiler=seed,
        )
        circuit = pm.run(qaoa_circuit)
        circuit_list.append(circuit)
        results_list.append(accumulated_errors(noisy_fake_backend, circuit))
    for backend, circuit in zip(noisy_fake_backends, circuit_list):
        prepared_backend = prepare_backend(backend, circuit)
        prepared_backends.append(prepared_backend)
    grade({
        'results_list': results_list,
        'prepared_backends': prepared_backends,
    }, 'lab2-ex3', _challenge_id)


#TODO obscuse
def my_find_paths_with_weight_sum_below_threshold(
    graph, threshold, two_qubit_ops_list, logical_pair_list
):
    valid_paths = []
    valid_weights = []
    for start_node in range(graph.num_nodes()):
        paths = [[start_node]]
        weights = [0]
        for i in range(len(two_qubit_ops_list)):
            new_paths = []
            new_weights = []
            for path, weight in zip(paths, weights):
                if logical_pair_list[i][0] < logical_pair_list[i][1]:
                    important_node = path[
                        logical_pair_list[i][0]
                    ]  # we know the structure is 10, 02, 30 and 14
                    for neighbor in graph.neighbors(important_node):
                        if neighbor not in path and graph.has_edge(important_node, neighbor):
                            edge_weight = (
                                graph.get_edge_data(important_node, neighbor)
                                * two_qubit_ops_list[i]
                            )  # we multiply by the number of times each two-qubit gate is applied
                            new_paths.append(path + [neighbor])
                            new_weights.append(weight + edge_weight)

                else:
                    important_node = path[logical_pair_list[i][1]]
                    for neighbor in graph.neighbors_undirected(important_node):
                        if neighbor not in path and graph.has_edge(neighbor, important_node):
                            edge_weight = (
                                graph.get_edge_data(neighbor, important_node)
                                * two_qubit_ops_list[i]
                            )  # we multiply by the number of times each two-qubit gate is applied
                            new_paths.append(path + [neighbor])
                            new_weights.append(weight + edge_weight)
            paths = new_paths
            weights = new_weights
        # Check which paths are valid
        for path, weight in zip(paths, weights):
            if weight < threshold:
                valid_paths.append(path)
                valid_weights.append(weight)
    return valid_paths, valid_weights

# We define the threshold and two_qubit_ops_list
def two_qubit_gate_errors_per_circuit_layout(
    circuit: QuantumCircuit, backend: QiskitRuntimeService.backend
) -> tuple:
    """Calculate accumulated two-qubit gate errors and related metrics for a given circuit layout."""
    pair_list = []
    error_pair_list = []
    error_acc_pair_list = []
    two_qubit_gate_count = 0
    properties = backend.properties()
    if "ecr" in (backend.configuration().basis_gates):
        two_qubit_gate = "ecr"
    elif "cz" in (backend.configuration().basis_gates):
        two_qubit_gate = "cz"
    for instruction in circuit.data:
        if instruction.operation.num_qubits == 2:
            two_qubit_gate_count += 1
            pair = [instruction.qubits[0]._index, instruction.qubits[1]._index]
            error_pair = properties.gate_error(gate=two_qubit_gate, qubits=pair)
            if pair not in (pair_list):
                pair_list.append(pair)
                error_pair_list.append(error_pair)
                error_acc_pair_list.append(error_pair)
            else:
                pos = pair_list.index(pair)
                error_acc_pair_list[pos] += error_pair

    acc_two_qubit_error = sum(error_acc_pair_list)
    return (
        acc_two_qubit_error,
        two_qubit_gate_count,
        pair_list,
        error_pair_list,
        error_acc_pair_list,
    )

@typechecked
def grade_lab2_ex4(
    find_paths_with_weight_sum_below_threshold: callable) -> None:
    # We define the graph
    service=QiskitRuntimeService()
    seed=43
    noisy_fake_backend=AerSimulator.from_backend(service.backend("ibm_brisbane"), seed_simulator=seed)
    graph = rx.PyDiGraph()
    graph.add_nodes_from(np.arange(0, noisy_fake_backend.num_qubits, 1))
    two_qubit_gate_graph = "ecr"
    graph.add_edges_from(
        [
            (
                edge[0],
                edge[1],
                noisy_fake_backend.properties().gate_error(
                    gate=two_qubit_gate_graph, qubits=(edge[0], edge[1])
                ),
            )
            for edge in noisy_fake_backend.coupling_map
        ]
    )


    max_cut_paulis = [
        ('IIIZZ', 1),
        ('IIIZZ', 1),
        ('IIZIZ', 1),
        ('IIZIZ', 1),
        ('IZIIZ', 1),
        ('IZIIZ', 1),
        ('ZIIIZ', 1),
        ('ZIIIZ', 1),
        ('IIZZI', 1),
        ('IIZZI', 1),
        ('IZIZI', 1),
        ('IZIZI', 1),
        ('ZIIZI', 1),
        ('ZIIZI', 1),
        ('IZZII', 1),
        ('IZZII', 1),
        ('ZIZII', 1),
        ('ZIZII', 1),
        ('ZZIII', 1)
    ]
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)

    pm = generate_preset_pass_manager(
        backend=noisy_fake_backend,
        optimization_level=3,
        seed_transpiler=seed,
        layout_method="sabre",
    )
    circuit_transpiled = pm.run(circuit)
    (
        acc_two_qubit_error,
        two_qubit_gate_count,
        pair_list,
        error_pair_list,
        error_acc_pair_list,
    ) = two_qubit_gate_errors_per_circuit_layout(circuit_transpiled, noisy_fake_backend)
    two_qubit_ops_list = [int(a / b) for a, b in zip(error_acc_pair_list, error_pair_list)]
    threshold=acc_two_qubit_error
    # We define logical_pair_list
    def remap_nodes(original_labels: list, edge_list: list[list]) -> list[list[int]]:
        """Remap node labels to a new sequence starting from 0 based on their order in original_labels."""
        label_mapping = {label: idx for idx, label in enumerate(original_labels)}
        remapped = [[label_mapping[src], label_mapping[dst]] for src, dst in edge_list]
        return remapped
    layout_list = list(circuit_transpiled.layout.initial_layout.get_physical_bits().keys())[:5]
    logical_pair_list = remap_nodes(layout_list, pair_list)
    # We execute the functions
    valid_paths, valid_weights = find_paths_with_weight_sum_below_threshold(
        graph, threshold, two_qubit_ops_list, logical_pair_list
    )
    prepa, prepb = my_find_paths_with_weight_sum_below_threshold(
        graph, threshold, two_qubit_ops_list, logical_pair_list
    )

    grade({
        'valid_paths': valid_paths,
        'valid_weights': valid_weights,
        'prepa': prepa,
        'prepb': prepb,
    }, 'lab2-ex4', _challenge_id)


#TODO obscuse
@typechecked
def grade_lab2_ex5(
    finding_best_seed: callable
) -> None:
    
    #TODO obfuscate
    def prepare_submission(circuit, backend):
        min_err_acc_seed = 100
        for seed_transpiler in range(0, 500):
            pm = generate_preset_pass_manager(
                backend=backend,
                optimization_level=3,
                seed_transpiler=seed_transpiler,
                layout_method="sabre",
            )
            circuit_opt_seed = pm.run(circuit)
            acc_total_error_seed, *_ = two_qubit_gate_errors_per_circuit_layout(
                circuit_opt_seed, backend
            )

            if min_err_acc_seed > acc_total_error_seed:
                min_err_acc_seed = acc_total_error_seed
                best_seed_transpiler = seed_transpiler
        return best_seed_transpiler, min_err_acc_seed
    # Define noisy_fake_backend
    service=QiskitRuntimeService()
    seed=43
    noisy_fake_backend=AerSimulator.from_backend(service.backend("ibm_brisbane"), seed_simulator=seed)
    # Define circuit trivial
    max_cut_paulis = [
        ('IIIZZ', 1),
        ('IIIZZ', 1),
        ('IIZIZ', 1),
        ('IIZIZ', 1),
        ('IZIIZ', 1),
        ('IZIIZ', 1),
        ('ZIIIZ', 1),
        ('ZIIIZ', 1),
        ('IIZZI', 1),
        ('IIZZI', 1),
        ('IZIZI', 1),
        ('IZIZI', 1),
        ('ZIIZI', 1),
        ('ZIIZI', 1),
        ('IZZII', 1),
        ('IZZII', 1),
        ('ZIZII', 1),
        ('ZIZII', 1),
        ('ZZIII', 1)
    ]
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)

    pm = generate_preset_pass_manager(
        backend=noisy_fake_backend,
        optimization_level=3,
        seed_transpiler=seed,
        layout_method="sabre",
    )
    circuit_trivial = pm.run(circuit)    
    prepa, prepb = prepare_submission(circuit_trivial, noisy_fake_backend)
    circuit_seed, best_seed_transpiler, min_err_acc_seed, best_two_qubit_gate_count = (
        finding_best_seed(circuit, noisy_fake_backend)

)
    grade({
        'best_seed_transpiler': best_seed_transpiler,
        'min_err_acc_seed': min_err_acc_seed,
        'prepa': prepa,
        'prepb': prepb,
    }, 'lab2-ex5', _challenge_id)



@typechecked
def grade_lab2_ex6a(
    fold_circuit: callable
) -> None:
    
    circuit = QuantumVolume(5)
    circuit.measure_all()
    
    folded_circuit = fold_circuit(circuit, scale_factor=5)

    grade({
        'folded_circuit_ops': folded_circuit.count_ops()
    }, 'lab2-ex6a', _challenge_id)


@typechecked
def grade_lab2_ex6b(
    fold_circuit: callable
) -> None:
    
    circuit = QuantumVolume(5)
    circuit.measure_all()

    pm = generate_preset_pass_manager(optimization_level=2, backend=FakeBrisbane())
    transpiled_circuit = pm.run(circuit)
    folded_circuit = fold_circuit(transpiled_circuit, scale_factor=5)

    grade({
        'transpiled_circuit_ops': transpiled_circuit.count_ops(),
        'folded_circuit_ops': folded_circuit.count_ops()
    }, 'lab2-ex6b', _challenge_id)


@typechecked
def grade_lab2_ex7(
    basic_zne: callable
) -> None:
    
    max_cut_paulis = [
        ('IIIZZ', 1),
        ('IIIZZ', 1),
        ('IIZIZ', 1),
        ('IIZIZ', 1),
        ('IZIIZ', 1),
        ('IZIIZ', 1),
        ('ZIIIZ', 1),
        ('ZIIIZ', 1),
        ('IIZZI', 1),
        ('IIZZI', 1),
        ('IZIZI', 1),
        ('IZIZI', 1),
        ('ZIIZI', 1),
        ('ZIIZI', 1),
        ('IZZII', 1),
        ('IZZII', 1),
        ('ZIZII', 1),
        ('ZIZII', 1),
        ('ZZIII', 1)
    ]
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)
    backend = GenericBackendV2(5, seed=43)
    pm = generate_preset_pass_manager(optimization_level=2, backend=backend)
    isa_circuit = pm.run(circuit)
    xdata, exp_vals, pub, folded_circuit = basic_zne(
        isa_circuit, 
        [5], 
        backend, 
        [0.90328799, 1.1925605 , 0.02658611, 0.94133493], 
        cost_hamiltonian
    )

    observables = pub[1]
    parameters = pub[2]

    grade({
        'transpiled_circuit_ops': isa_circuit.count_ops(),
        'folded_circuit_ops': folded_circuit.count_ops(),
        'observables': observables,
        'parameters': parameters,
    }, 'lab2-ex7', _challenge_id)