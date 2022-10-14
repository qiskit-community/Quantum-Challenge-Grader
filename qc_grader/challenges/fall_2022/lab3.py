from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit
from qiskit.result import QuasiDistribution
from qc_grader.grader.grade import grade, get_problem_set


_challenge_id = 'fall_2022'

@typechecked
def grade_lab3_ex1(attempt_qc: QuantumCircuit) -> None:
    grade(QuantumCircuit, 'ex3-1', _challenge_id)

@typechecked
def grade_lab3_ex2(attempt: QuasiDistribution) -> None:
    grade(QuasiDistribution, 'ex3-2', _challenge_id)

@typechecked
def grade_lab3_ex3(attempt_etgl: callable) -> None:
    grade(function, 'ex3-3', _challenge_id)
