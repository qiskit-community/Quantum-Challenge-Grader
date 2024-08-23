from typing import List
from typeguard import typechecked

from qiskit.quantum_info import SparsePauliOp
from qc_grader.grader.grade import grade


_challenge_id = 'fall_fest24'
_grade_only = True


@typechecked
def grade_lab0_welcome(answer: str) -> None:
    grade(answer, 'lab0-welcome', _challenge_id, grade_only=_grade_only)
