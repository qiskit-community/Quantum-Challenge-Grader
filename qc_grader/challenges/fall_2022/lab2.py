from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit
import numpy as np
from qc_grader.grader.grade import grade

_challenge_id = 'fall_2022'


@typechecked
def grade_lab2_ex1(qc:QuantumCircuit) -> None:
    grade(qc, 'ex2-1', _challenge_id)


@typechecked
def grade_lab2_ex2(
    q1_answer: str, q2_answer: str, q3_answer: str, q4_answer: str
) -> None:
    answer = {
        'q1_answer': q1_answer,
        'q2_answer': q2_answer,
        'q3_answer': q3_answer,
        'q4_answer': q4_answer
    }
    grade(answer, 'ex2-2', _challenge_id)


@typechecked
def grade_lab2_ex3(
    answer_sim: List[float],
    answer_noise: List[float],
    answer_zne: List[float]
) -> None:
    answer = {
        'sim': answer_sim,
        'noise': answer_noise,
        'zne': answer_zne
    }
    grade(answer, 'ex2-3', _challenge_id)


@typechecked
def grade_lab2_ex4(answer_kernel: List[float]) -> None:
    grade(answer_kernel, 'ex2-4', _challenge_id)


@typechecked
def grade_lab2_ex5(
    answer_predict: np.ndarray,
    answer_kernel: List[float]
) -> None:
    answer = {
        'predict': answer_predict,
        'kernel': answer_kernel
    }
    grade(answer, 'ex2-5', _challenge_id)
