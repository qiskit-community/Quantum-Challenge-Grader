from typeguard import typechecked
from typing import *
from qc_grader.grader.grade import grade


_challenge_id = 'qdc_2024'

@typechecked
def submit_feedback_3a_1(feedback: str) -> None:
    grade(feedback, 'feedback-3a-1', _challenge_id)


@typechecked
def submit_feedback_3a_2(feedback: str) -> None:
    grade(feedback, 'feedback-3a-2', _challenge_id)


@typechecked
def submit_feedback_3b_1(feedback: str) -> None:
    grade(feedback, 'feedback-3b-1', _challenge_id)


@typechecked
def submit_feedback_3b_2(feedback: str) -> None:
    grade(feedback, 'feedback-3b-2', _challenge_id)