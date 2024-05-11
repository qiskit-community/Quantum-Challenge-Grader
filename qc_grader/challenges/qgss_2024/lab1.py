from typing import List
from typeguard import typechecked


from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2024'


@typechecked
def grade_lab1_ex1(answer: List[int]) -> None:
    grade(answer, 'lab1-ex1', _challenge_id)


@typechecked
def grade_lab1_ex2(answer: str) -> None:
    grade(answer, 'lab1-ex2', _challenge_id)


@typechecked
def grade_lab1_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex3', _challenge_id)
