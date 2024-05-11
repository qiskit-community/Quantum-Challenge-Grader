from typing import List
from typeguard import typechecked


from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab5_ex1(answer: List[int]) -> None:
    grade(answer, 'lab5-ex1', _challenge_id)


@typechecked
def grade_lab5_ex2(answer: str) -> None:
    grade(answer, 'lab5-ex2', _challenge_id)


@typechecked
def grade_lab5_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab5-ex3', _challenge_id)
