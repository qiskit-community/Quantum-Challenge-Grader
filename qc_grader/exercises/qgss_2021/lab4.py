from typing import Tuple

import numpy as np

from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.grade import grade_and_submit
from qc_grader.util import paulisumop_to_json


criteria: dict = {}


def grade_lab4_ex1(matmult_result: complex) -> None:
    grade_and_submit(matmult_result, 'lab4', 'ex1')


def grade_lab4_ex2(shot_result: complex) -> None:
    grade_and_submit(shot_result, 'lab4', 'ex2')


def grade_lab4_ex3(H_tfi: PauliSumOp) -> None:
    answer = {
        'qubit_op': paulisumop_to_json(H_tfi)
    }
    grade_and_submit(answer, 'lab4', 'ex3')


def grade_lab4_ex4(tfi_result: float) -> None:
    grade_and_submit(tfi_result, 'lab4', 'ex4')
