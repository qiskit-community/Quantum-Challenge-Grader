from typeguard import typechecked
from typing import List
from qiskit import transpile, QuantumCircuit, generate_preset_pass_manager
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.circuit.library import QuantumVolume, QAOAAnsatz
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.fake_provider import FakeBrisbane, FakeSherbrooke, FakeTorino
import rustworkx as rx
import numpy as np
from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2025'
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


@typechecked
def grade_lab2_ex1(
    find_best_metrics: callable
) -> None:
    backend = FakeBrisbane()
    solutions=find_best_metrics(backend)
    grade({
        'solutions': solutions,
    }, 'lab2-ex1', _challenge_id)


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

    max_cut_paulis = graph_to_Pauli(graph)
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    grade({
        'cost_hamiltonian': cost_hamiltonian,
    }, 'lab2-ex2', _challenge_id)


@typechecked
def grade_lab2_ex3(
    accumulated_errors: callable
) -> None:

    noisy_fake_backends = [
    FakeBrisbane(),
    FakeSherbrooke(),
    FakeTorino()]
    seed=43
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)
    circuit.measure_all()
    circuit_list=[]
    results_list=[]
    for noisy_fake_backend in noisy_fake_backends:
        pm = generate_preset_pass_manager(
            backend=noisy_fake_backend,
            optimization_level=3,
            seed_transpiler=seed,
        )
        circuit_transpiled = pm.run(circuit)
        circuit_list.append(circuit_transpiled)
        results_list.append(accumulated_errors(noisy_fake_backend, circuit_transpiled))
    grade({
        'results_list': results_list,
    }, 'lab2-ex3', _challenge_id)


def two_qubit_gate_errors_per_circuit_layout(
    circuit: QuantumCircuit, backend: QiskitRuntimeService.backend
) -> tuple:
    pair_list = []
    error_pair_list = []
    error_acc_pair_list = []
    properties = backend.properties()
    if "ecr" in (backend.configuration().basis_gates):
        two_qubit_gate = "ecr"
    elif "cz" in (backend.configuration().basis_gates):
        two_qubit_gate = "cz"
    for instruction in circuit.data:
        if instruction.operation.num_qubits == 2:
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
        pair_list,
        error_pair_list,
        error_acc_pair_list,
    )


@typechecked
def grade_lab2_ex4(
    find_paths_with_weight_sum_below_threshold: callable) -> None:
    # We define the graph
    seed=43
    noisy_fake_backend=FakeBrisbane()
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


    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)

    pm = generate_preset_pass_manager(
        backend=noisy_fake_backend,
        optimization_level=3,
        seed_transpiler=2*seed,
        layout_method="sabre",
    )
    circuit_transpiled = pm.run(circuit)
    (
        acc_two_qubit_error,
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

    grade({
        'valid_paths': valid_paths,
        'valid_weights': valid_weights,
    }, 'lab2-ex4', _challenge_id)


@typechecked
def grade_lab2_ex5(
    finding_best_seed: callable
) -> None:

    noisy_fake_backend=FakeBrisbane()
    cost_hamiltonian = SparsePauliOp.from_list(max_cut_paulis)
    circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)
    circuit_seed, best_seed_transpiler, min_err_acc_seed, best_two_qubit_gate_count = (
        finding_best_seed(circuit, noisy_fake_backend)
)
    grade({
        'best_seed_transpiler': best_seed_transpiler,
        'min_err_acc_seed': min_err_acc_seed,
    }, 'lab2-ex5', _challenge_id)


@typechecked
def grade_lab2_ex6a(
    fold_circuit: callable
) -> None:    
    circuit = QuantumVolume(5)
    circuit.measure_all()    
    folded_circuit = fold_circuit(circuit, scale_factor=5)
    grade(folded_circuit, 'lab2-ex6a', _challenge_id)


@typechecked
def grade_lab2_ex6b(
    fold_circuit: callable
) -> None:    
    circuit = QuantumVolume(5,seed=43)
    circuit.measure_all()
    pm = generate_preset_pass_manager(optimization_level=2, backend=FakeBrisbane(),seed_transpiler=43)
    transpiled_circuit = pm.run(circuit)
    folded_circuit = fold_circuit(transpiled_circuit, scale_factor=5)
    grade(folded_circuit, 'lab2-ex6b', _challenge_id)
