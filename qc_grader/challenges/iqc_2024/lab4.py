from typing import List
from typeguard import typechecked

from scipy.optimize._optimize import OptimizeResult

from qiskit import QuantumCircuit
from qiskit.transpiler import InstructionProperties
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.providers import BackendV2
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import RealAmplitudes
from qiskit.primitives import StatevectorEstimator, BackendEstimator

from qiskit_aer import AerSimulator

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'

CORRECT_LIST_COEFFICIENTS = [[0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j], [0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j], [0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j], [0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0.7071067811865476+0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 1+0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j], [0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, (1+0j), 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j]]

CORRECT_LIST_LABELS = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

OBS = SparsePauliOp("ZZZZZ")

ANSATZ = RealAmplitudes(num_qubits=5, reps=1, insert_barriers=True, entanglement='full')

def create_test_backend():

    backend = GenericBackendV2(
    num_qubits=5,
    basis_gates=["id", "rz", "sx", "x", "cx"],
    control_flow=True,
    coupling_map = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]
    )

    error_rate = 5e-4

    for i in range(backend.num_qubits):
        qarg = (i,)
        backend.target.update_instruction_properties('rz', qarg, InstructionProperties(error=error_rate, duration=1e-8))
        backend.target.update_instruction_properties('x', qarg, InstructionProperties(error=error_rate, duration=1e-8))
        backend.target.update_instruction_properties('sx', qarg, InstructionProperties(error=error_rate, duration=1e-8))
        backend.target.update_instruction_properties('measure', qarg, InstructionProperties(error=error_rate, duration=1e-8))

    for edge in backend.coupling_map:
        backend.target.update_instruction_properties('cx', tuple(edge), InstructionProperties(error=error_rate, duration=1e-8))

    return backend

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
def grade_lab4_ex5(results_list: list[float]) -> None:
    grade(results_list, 'lab4-ex5', _challenge_id)

