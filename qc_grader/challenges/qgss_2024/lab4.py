from typing import List
from typeguard import typechecked


from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2024'


@typechecked
def grade_lab4_ex1(answer: List[int]) -> None:
    grade(answer, 'lab4-ex1', _challenge_id)


@typechecked
def grade_lab4_ex2(answer: str) -> None:
    grade(answer, 'lab4-ex2', _challenge_id)


@typechecked
def grade_lab4_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab4-ex3', _challenge_id)
