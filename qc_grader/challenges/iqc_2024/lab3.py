from typing import List
from typeguard import typechecked

from scipy.optimize._optimize import OptimizeResult

from qiskit import QuantumCircuit
from qiskit.providers import BackendV2

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab3_ex1(list_coefficients: List[List[complex]], list_labels: List[int]) -> None:

    answer = {
        'list_coefficients': list_coefficients,
        'list_labels': list_labels,
    }

    grade(answer, 'lab3-ex1', _challenge_id)


@typechecked
def grade_lab3_ex2(
    num_qubits: int,
    reps: int,
    entanglement: str
) -> None:
    answer = {
        'num_qubits': num_qubits,
        'reps': reps
        'entanglement': entanglement
    }
    grade(answer, 'lab3-ex2', _challenge_id)


@typechecked
def grade_lab3_ex3(optimize_result: OptimizeResult) -> None:
    grade(optimize_result, 'lab3-ex3', _challenge_id)


@typechecked
def grade_lab3_ex4(backend: BackendV2) -> None:
    grade(backend.coupling_map, 'lab3-ex4', _challenge_id)
