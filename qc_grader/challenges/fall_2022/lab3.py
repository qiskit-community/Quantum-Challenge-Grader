from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit
from qiskit.result import QuasiDistribution
from qc_grader.grader.grade import grade, get_problem_set
import random

_challenge_id = 'fall_2022'

@typechecked
def grade_lab3_ex1(attempt_qc: QuantumCircuit) -> None:
    grade(attempt_qc, 'ex3-1', _challenge_id)

@typechecked
def grade_lab3_ex2(attempt: QuasiDistribution) -> None:
    grade(attempt, 'ex3-2', _challenge_id)

@typechecked
def grade_lab3_ex3(attempt_etgl: Callable) -> None:
    n = random.randint(2,4)
    qc = attempt_etgl(n)
    answer = {
        'input': n,
        'output': qc
    }
    grade(answer, 'ex3-3', _challenge_id)
