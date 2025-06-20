from typeguard import typechecked
from typing import Dict
import numpy as np
import hashlib

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2025'


def robust_hash(arr):
    h = hashlib.sha256()
    h.update(arr.shape.__repr__().encode())
    h.update(str(arr.dtype).encode())
    h.update(arr.tobytes())
    return h.hexdigest()


@typechecked
def grade_lab4_ex1(answer: Dict) -> None:
    grade(answer, 'lab4-ex1', _challenge_id)


# Change variable names, syndrome_map same for others
@typechecked
def grade_lab4_ex2(answer: Dict) -> None:
    grade(answer, 'lab4-ex2', _challenge_id)


@typechecked
def grade_lab4_ex3(answer: str) -> None:
    grade(answer, 'lab4-ex3', _challenge_id)


@typechecked
def grade_lab4_ex4(ansHx: np.ndarray, ansHz: np.ndarray) -> None:
    answer = (robust_hash(ansHx), robust_hash(ansHz))
    grade(answer, 'lab4-ex4', _challenge_id)


@typechecked
def grade_lab4_ex5(ansHx: np.ndarray, ansHz: np.ndarray) -> None:
    answer = (robust_hash(ansHx), robust_hash(ansHz))
    grade(answer, 'lab4-ex5', _challenge_id)


@typechecked
def grade_lab4_ex6(k_toric: int, k_gross: int) -> None:
    answer = (k_toric, k_gross)
    grade(answer, 'lab4-ex6', _challenge_id)
