from typing import List
from typeguard import typechecked

from qiskit.opflow.primitive_ops import PauliOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.grader.grade import grade
from qc_grader.grader.common import pauliop_to_json, paulisumop_to_json


_challenge_id = 'qgss_2022'


@typechecked
def grade_lab2_ex1(op_list: List[PauliOp]) -> None:
    answer = [
        pauliop_to_json(p) for p in op_list
    ]
    grade(answer, 'ex2-1', _challenge_id)


@typechecked
def grade_lab2_ex2(op_list: List[PauliSumOp]) -> None:
    answer = [
        paulisumop_to_json(p) for p in op_list
    ]
    grade(answer, 'ex2-2', _challenge_id)
