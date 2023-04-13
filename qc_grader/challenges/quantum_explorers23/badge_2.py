from typeguard import typechecked

from qc_grader.grader.grade import grade


_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge2_ex1(answer: str) -> None:
    status, _, message = grade(
        answer,
        'badge2_ex1',
        _challenge_id, 
        return_response=True
    )
    print('Thank you for submitting your answer')
