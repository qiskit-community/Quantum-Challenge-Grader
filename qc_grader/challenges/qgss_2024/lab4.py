import json
import random
import importlib.resources

from typeguard import typechecked

from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.primitives import PrimitiveResult
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import RuntimeDecoder

from qc_grader.grader.grade import get_problem_set, grade


_challenge_id = 'qgss_2024'


@typechecked
def grade_lab4_ex1(
    generating_function,
) -> None:
    # Use the function to generate a hamiltonian with a known set of parameters
    anisotropy = 1.
    num_spins = 12
    h = 1.
    # First check is to make sure the generating_function is callable...

    hamiltonian = generating_function(num_spins, anisotropy, h)
    paulis = [ pauli.to_label() for pauli in list(hamiltonian.paulis) ]
    re_coeffs = [coeff.real for coeff in list(hamiltonian.coeffs)]
    im_coeffs = [coeff.imag for coeff in list(hamiltonian.coeffs)]

    grade({'paulis': paulis,
           'real coeffs': re_coeffs, 
           'imag coeffs': im_coeffs}, 'lab4-ex1', _challenge_id)


@typechecked
def grade_lab4_ex2(generating_function) -> None:
    anisotropy = 1.
    num_spins = 12
    h = 1.

    hamiltonian = generating_function(num_spins, anisotropy, h)
    paulis = [ pauli.to_label() for pauli in list(hamiltonian.paulis) ]
    re_coeffs = [coeff.real for coeff in list(hamiltonian.coeffs)]
    im_coeffs = [coeff.imag for coeff in list(hamiltonian.coeffs)]

    grade({'paulis':paulis,
           'real coeffs':re_coeffs, 
           'imag coeffs':im_coeffs}, 'lab4-ex2', _challenge_id)


@typechecked
def grade_lab4_ex3(backend, isa_circuit, isa_observables) -> None:
    # Grader for exercise 3 
    backend_num_qubits = backend.num_qubits
    isa_circuit_num_qubits = isa_circuit.num_qubits
    observables_num_qubits = [ len(observable.paulis[0].to_label()) for observable in isa_observables ]

    grade({
        "backend_qubits": backend_num_qubits,
        "isa_circuit_num_qubits": isa_circuit_num_qubits,
        "observable_qubits": observables_num_qubits
    }, 'lab4-ex3', _challenge_id)


@typechecked
def grade_lab4_ex4(hamiltonians: dict, 
                  time_evolution_operators: dict,
                  isa_circuits: dict,
                  isa_z_observables: dict) -> None:
    # Grader for exercise lab4-ex2
    # Each dictionary entry should contain a list with num_spins=50 entries,
    #  we'll just check for the correct shape and object type.
    # Get num keys, type, and length for hamiltonians dict
    hamiltonians_keys = list(hamiltonians.keys())
    random_key = random.choice(hamiltonians_keys)
    random_hamiltonian = list(random.choice(hamiltonians[random_key]).paulis)
    system_size = len(random.choice(random_hamiltonian))


    time_evolution_keys = list(time_evolution_operators.keys())
    random_key = random.choice(time_evolution_keys)
    is_pauli_evolution_gate = isinstance( random.choice(time_evolution_operators[random_key]),
                                         PauliEvolutionGate)

    isa_circuit_keys = list(isa_circuits.keys())
    random_key = random.choice(isa_circuit_keys)
    num_qubits = random.choice(isa_circuits[random_key]).num_qubits
    num_circuits = len(isa_circuits[random_key])

    isa_z_observables_keys = list(isa_z_observables.keys())
    random_key = random.choice(isa_z_observables_keys)

    # Select a random set observables which were enumerated by each h_val 
    random_observable_set = random.choice(isa_z_observables[random_key])
    # Among the set of 50 observables, select a random one
    random_observable = random.choice(random_observable_set)
    observable_length = len(random_observable.paulis[0])
    num_observables = len(random.choice(isa_z_observables[random_key]))

    key_list = {'hamiltonian_keys': hamiltonians_keys, 
                'time_evolution_keys': time_evolution_keys, 
                'isa_circuit_keys': isa_circuit_keys, 
                'isa_z_observables_keys': isa_z_observables_keys}

    grade({
        "system_size": system_size,
        "key_list": key_list,
        "is_pauli_evolution_gate": is_pauli_evolution_gate,
        "num_qubits": num_qubits,
        "num_circuits": num_circuits,
        "observable_length": observable_length,
        "num_observables": num_observables
    }, 'lab4-ex4', _challenge_id)

@typechecked
def grade_lab4_ex5(pub_dict: dict) -> None:
    # Grader for exercise 5.
    # Here we're just going to check and make sure that the dictionary of pubs
    #  are in the correct format. They should have two keys (one for each phase),
    #  where each key contains a list of the correct object type.
    random_key = random.choice(list(pub_dict.keys()))
    random_pub = random.choice(pub_dict[random_key])

    is_circuit = isinstance(random_pub[0], QuantumCircuit)
    num_observables = len(random_pub[1])
    is_pauli_op = isinstance(random.choice(random_pub[1]), SparsePauliOp)
    time_param = random_pub[2][0]
    num_circuits = len(pub_dict[random_key])
    
    grade({
        "is_circuit":is_circuit,
        "num_observables":num_observables,
        "is_pauli_op":is_pauli_op,
        "time_param":time_param,
        "num_circuits":num_circuits
    }, 'lab4-ex5', _challenge_id)


@typechecked
def grade_lab4_ex6(fname: str) -> None:
    # For this exercise, just check if the file can be loaded using the json module
    correct_format = False
    if fname == "skip-question":
        correct_format = True
    else:
        with open(fname,'r') as ofile:
            try:
                answer = json.load(ofile)
                correct_format = True
            except json.JSONDecodeError:
                pass

    grade(correct_format, 'lab4-ex6', _challenge_id)

@typechecked
def lab4_ex7_get_data() -> dict:
    """
    This function will load the pre-baked results for the students to use in ex 7 and 8
    """
    _, runtime_results = get_problem_set('lab4-ex7', _challenge_id)

    all_result_data = {}
    for phase in runtime_results.keys():
        result_data = []
        for result in runtime_results[phase]:
            result_data.append(json.loads(result, cls=RuntimeDecoder))
        all_result_data[phase] = result_data
    return all_result_data

@typechecked
def grade_lab4_ex7(result_dict: dict) -> None:
    # This exercise is just checking that you have the correct shape of PrimitiveResult objects 
    random_phase = random.choice(list(result_dict.keys()))
    random_result = random.choice(result_dict[random_phase])
    is_primitive_result = isinstance(random_result, PrimitiveResult)
    num_results = len(result_dict[random_phase])

    grade({
        'is_primitive_result': is_primitive_result,
        'num_results':num_results
    }, 'lab4-ex7', _challenge_id)

@typechecked
def grade_lab4_ex8(plotting_data: dict) -> None:
    # This exercise will be graded by examining the min and max value for the two phases
    #   and see if they reasonably agree with what is expected
    min_xxx_phase = min(plotting_data['XXX'])
    min_ferro_phase = min(plotting_data['Anisotropic'])

    grade({
        'min_xxx_phase':min_xxx_phase,
        'min_ferro_phase':min_ferro_phase
    }, 'lab4-ex8', _challenge_id)

