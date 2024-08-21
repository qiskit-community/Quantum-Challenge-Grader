from typing import List
from typeguard import typechecked



from qiskit.quantum_info import SparsePauliOp

from qc_grader.grader.grade import grade


_challenge_id = 'fall_fest24'
_grade_only = True


@typechecked
def grade_lab1_welcome(answer: str) -> None:
    grade(answer, 'lab1-welcome', _challenge_id, grade_only=_grade_only)
    

@typechecked
def grade_lab1_ex1(observables: List[SparsePauliOp]) -> None:
    grade(observables, 'lab1-ex1', _challenge_id, grade_only=_grade_only)
