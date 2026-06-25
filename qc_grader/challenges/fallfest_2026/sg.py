'''
Fall Fest 2026 Lab 10 - Stern-Gerlach Measurements - Grading Functions
'''
from typing import Any
from typeguard import typechecked
from qc_grader.grader.grade import grade_answer
_CHALLENGE = 'fallfest_2026'
_LAB = 'sg'


def _grade(answer: Any = None, exercise: str = None) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_sg_ex1(answer: bool) -> None:
    _grade(answer, 'ex1')


@typechecked
def grade_sg_ex2(answer: bool) -> None:
    _grade(answer, 'ex2')


@typechecked
def grade_sg_ex3(answer: bool) -> None:
    _grade(answer, 'ex3')


@typechecked
def grade_sg_ex4(answer: bool) -> None:
    _grade(answer, 'ex4')


@typechecked
def grade_sg_ex5(answer: bool) -> None:
    _grade(answer, 'ex5')


@typechecked
def grade_sg_ex6(answer: str) -> None:
    _grade(answer, 'ex6')


@typechecked
def grade_sg_ex7(answer: str) -> None:
    _grade(answer, 'ex7')


@typechecked
def grade_sg_ex8(answer: str) -> None:
    _grade(answer, 'ex8')


@typechecked
def grade_sg_ex9(answer: str) -> None:
    _grade(answer, 'ex9')


@typechecked
def grade_sg_ex10(answer: str) -> None:
    _grade(answer, 'ex10')


@typechecked
def grade_sg_ex11(answer: str) -> None:
    _grade(answer, 'ex11')
