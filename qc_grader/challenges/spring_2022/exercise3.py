from pathlib import Path
from typing import Any
from typeguard import typechecked

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex3a(answer: Any) -> None:
    grade(answer, 9, challenge_id)  # 3a


@typechecked
def grade_ex3b(answer: Any) -> None:
    grade(answer, 10, challenge_id)  # 3b


@typechecked
def grade_ex3c(answer: Any) -> None:
    grade(answer, 11, challenge_id)  # 3c
