
import random

from typeguard import typechecked
from typing import Callable

from qiskit import QuantumCircuit
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.grader.grade import grade
from qc_grader.grader.common import circuit_to_json

_challenge_id = 'fall_2022'

@typechecked
def grade_lab3_ex1(attempt_qc: QuantumCircuit, attempt_n: int) -> None:
    answer = {
        'attempt_n': attempt_n,
        'attempt_qc': circuit_to_json(attempt_qc)
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
