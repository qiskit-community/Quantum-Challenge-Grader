from typeguard import typechecked

from qc_grader.grader.grade import grade

_challenge_id = 'qdc_2024'

@typechecked
def grade_day0_ex1(answer: str) -> None:
    grade(
        answer=answer, 
        question='day0-ex1',
        challenge=_challenge_id
    )
