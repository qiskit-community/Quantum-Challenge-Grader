from typing import List
from typeguard import typechecked


from qiskit import QuantumCircuit

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
def grade_lab3_ex2(answer: str) -> None:
    grade(answer, 'lab3-ex2', _challenge_id)


@typechecked
def grade_lab3_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab3-ex3', _challenge_id)
