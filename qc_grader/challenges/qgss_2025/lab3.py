from typeguard import typechecked

from qc_grader.grader.grade import grade

_challenge_id = 'qgss_2025'


@typechecked
def grade_lab3_ex1(answer: int) -> None:
    grade(answer, 'lab3-ex1', _challenge_id)


@typechecked
def grade_lab3_ex2(answer: list[int]) -> None:
    grade(answer, 'lab3-ex2', _challenge_id)


@typechecked
def grade_lab3_ex3(answer: int) -> None:
    grade(answer, 'lab3-ex3', _challenge_id)


@typechecked
def grade_lab3_ex4(answer: list[int]) -> None:
    grade(answer, 'lab3-ex4', _challenge_id)


@typechecked
def grade_lab3_ex5(answer: list[tuple[int, int]]) -> None:
    grade(answer, 'lab3-ex5', _challenge_id)
