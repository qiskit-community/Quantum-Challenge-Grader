from typing import List
from typeguard import typechecked

from qc_grader.grader.grade import grade


_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge1_ex1(answer: List[int]) -> None:
    status, _, message = grade(
        answer,
        'badge1_ex1',
        _challenge_id, 
        return_response=True
    )
    print('Thank you for submitting your answer')
    
    
@typechecked
def grade_badge1_ex2(answer: List[int]) -> None:
    status, _, message = grade(
        answer,
        'badge1_ex2',
        _challenge_id, 
        return_response=True
    )
    print('Thank you for submitting your answer')
    

@typechecked
def grade_badge1_ex3(answer: List[int]) -> None:
    status, _, message = grade(
        answer,
        'badge1_ex3',
        _challenge_id, 
        return_response=True
    )
    print('Thank you for submitting your answer')
