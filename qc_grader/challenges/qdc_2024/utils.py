from typeguard import typechecked

from qc_grader.grader.grade import grade

_challenge_id = 'qdc_2024'

@typechecked
def submit_name(name: str) -> None:
    grade(name, 'submit-name', _challenge_id)

@typechecked
def submit_feedback(feedback: str) -> None:
    grade(feedback, 'submit-feedback', _challenge_id)

@typechecked
def test_submit(answer: str) -> None:
    grade(answer, 'test', _challenge_id)
