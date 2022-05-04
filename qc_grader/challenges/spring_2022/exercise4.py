from pathlib import Path
from typing import List, Tuple, Union
from typeguard import typechecked

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex4a(**kwargs: Union[int, float]) -> None:
    answer = kwargs
    grade(answer, 10, challenge_id)  # 4a


@typechecked
def grade_ex4b(
    list_operator: List[Tuple[str, Union[complex, float]]],
    register_length: int
) -> None:
    answer = {
        'list_operator': list_operator,
        'register_length': register_length
    }
    grade(answer, 11, challenge_id)  # 4b
