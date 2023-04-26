from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit


from qc_grader.grader.grade import grade


_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge1_ex1(answer1: List[int]) -> None:
    status, _, message = grade(
        answer1,
        'badge1_ex1',
        _challenge_id, 
        return_response=True
    )
    print('Thank you for submitting your answer')
