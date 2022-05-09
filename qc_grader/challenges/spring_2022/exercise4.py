from typing import List, Tuple, Union
from typeguard import typechecked

from qc_grader.grader.grade import grade


_challenge_id = 'spring-2022'


@typechecked
def grade_ex4a(**kwargs: Union[int, float]) -> None:
    answer = kwargs
    grade(answer, '4a', _challenge_id)


@typechecked
def grade_ex4b(
    list_operator: List[Tuple[str, Union[complex, float]]],
    register_length: int
) -> None:
    answer = {
        'list_operator': list_operator,
        'register_length': register_length
    }
    grade(answer, '4b', _challenge_id)
