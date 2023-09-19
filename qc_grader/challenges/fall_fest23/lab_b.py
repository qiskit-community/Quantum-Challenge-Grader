from typing import List
from typeguard import typechecked

from qiskit.circuit import QuantumCircuit
from qiskit.result.counts import Counts

from qc_grader.grader.grade import grade


_challenge_id = 'fall_fest23'


@typechecked
def grade_ex2a(answer1: QuantumCircuit) -> None:
    grade(answer1, 'ex2a', _challenge_id)


@typechecked
def grade_ex2b(answer2: QuantumCircuit) -> None:
    grade(answer2, 'ex2b', _challenge_id)


@typechecked
def grade_ex2c(answer3: bool) -> None:
    grade(answer3, 'ex2c', _challenge_id)


@typechecked
def grade_ex2d(answer4: List[int]) -> None:
    grade(answer4, 'ex2d', _challenge_id)


@typechecked
def grade_ex2e(answer5: QuantumCircuit) -> None:
    grade(answer5, 'ex2e', _challenge_id)
