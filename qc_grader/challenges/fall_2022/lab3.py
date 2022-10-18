from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit
from qiskit.result import QuasiDistribution
from qc_grader.grader.grade import grade, get_problem_set
import random

_challenge_id = 'fall_2022'

@typechecked
def grade_lab3_ex1(attempt_qc: QuantumCircuit, attempt_n: int) -> None:
    answer = {
        'attempt_qc': attempt_qc,
        'attempt_n': attempt_n
    }
    grade(answer, 'ex3-1', _challenge_id)

@typechecked
def grade_lab3_ex2(attempt_ising: PauliSumOp) -> None:
    grade(attempt_ising, 'ex3-2', _challenge_id)


@typechecked
def grade_lab3_ex3(attempt_etgl: Callable) -> None:
    n = random.randint(2,4)
    qc = attempt_etgl(n)
    answer = {
        'input': n,
        'output': qc
    }
    grade(answer, 'ex3-3', _challenge_id)
