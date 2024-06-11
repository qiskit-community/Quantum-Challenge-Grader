from typing import List, Callable
from typeguard import typechecked

from scipy.optimize._optimize import OptimizeResult

from qiskit import QuantumCircuit
from qiskit.transpiler import InstructionProperties
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.providers import BackendV2
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.circuit.library import RealAmplitudes
from qiskit.primitives import StatevectorEstimator, BackendEstimator

from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import EstimatorOptions

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'

CORRECT_LIST_COEFFICIENTS = [[0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j], [0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j], [0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j], [0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 1+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j]]

CORRECT_LIST_LABELS = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

OBS = SparsePauliOp("ZZZZZ")

ANSATZ = RealAmplitudes(num_qubits=5, reps=1, insert_barriers=True, entanglement='full')


@typechecked
def grade_lab4_ex1(list_coefficients: List[List[complex]], list_labels: List[int]) -> None:
    answer = {
        'list_coefficients': list_coefficients,
        'list_labels': list_labels,
    }
    grade(answer, 'lab4-ex1', _challenge_id)


@typechecked
def grade_lab4_ex2(
    num_qubits: int,
    reps: int,
    entanglement: str
) -> None:
    answer = {
        'num_qubits': num_qubits,
        'reps': reps,
        'entanglement': entanglement
    }
    grade(answer, 'lab4-ex2', _challenge_id)


@typechecked
def grade_lab4_ex3(optimize_result: OptimizeResult) -> None:
    opt_params = optimize_result.x
    list_coefficients = CORRECT_LIST_COEFFICIENTS
    list_labels = CORRECT_LIST_LABELS
    result_values_list = []
    pm = generate_preset_pass_manager(backend=AerSimulator(), optimization_level=1, seed_transpiler=0)
    estimator = StatevectorEstimator()

    for amplitudes,label in zip(list_coefficients, list_labels):
        qc = QuantumCircuit(5)
        qc.initialize(amplitudes)
        classifier = qc.compose(ANSATZ.decompose(reps=6))
        transpiled_classifier = pm.run(classifier)
        pub = (transpiled_classifier, OBS, opt_params)
        job = estimator.run([pub])
        result_values_list.append(job.result()[0].data.evs)
    
    grade(result_values_list, 'lab4-ex3', _challenge_id)


@typechecked
def grade_lab4_ex4(backend: BackendV2) -> None:
    basis_gates=['rz', 'x', 'sx', 'cx', 'measure']
    gate_error_dict = {gate: next(iter(backend.target[gate].values())).error for gate in basis_gates}
    grade(gate_error_dict, 'lab4-ex4', _challenge_id)


@typechecked
def grade_lab4_ex5(amplitude_embedding: Callable) -> None:
    answer_list =[Statevector(amplitude_embedding(5,bird_index)) for bird_index in range(10)]
    grade(answer_list, 'lab4-ex5', _challenge_id)

@typechecked
def grade_lab4_ex6(results_test: list[float]) -> None:
    grade(results_test, 'lab4-ex6', _challenge_id)


@typechecked
def grade_lab4_ex7(options_0: EstimatorOptions, options_1: EstimatorOptions) -> None:
    answer_list = [
        [
            options.resilience_level,
            options.dynamical_decoupling.enable,
            options.dynamical_decoupling.sequence_type,
            options.default_shots,
            options.optimization_level,
        ]
        for options in [options_0, options_1]
    ]
    grade(answer_list, "lab4-ex7", _challenge_id)
