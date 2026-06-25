'''
Fall Fest 2026 Lab 1 - Get Started with Qiskit - Grading Functions
'''
from typing import Any
from typeguard import typechecked
from qc_grader.grader.grade import grade_answer
_CHALLENGE = 'fallfest_2026'
_LAB = 'intro'


def _grade(answer: Any = None, exercise: str = None) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_intro_ex1(answer: bool = None) -> None:
    _grade(answer, 'ex1')


@typechecked
def grade_intro_ex2(answer: bool = None) -> None:
    _grade(answer, 'ex2')


@typechecked
def grade_intro_ex3(answer: bool = None) -> None:
    _grade(answer, 'ex3')


@typechecked
def grade_intro_ex4(answer: bool = None) -> None:
    _grade(answer, 'ex4')


@typechecked
def grade_intro_ex5(answer: bool = None) -> None:
    _grade(answer, 'ex5')


@typechecked
def grade_intro_ex6(answer: bool = None) -> None:
    _grade(answer, 'ex6')


@typechecked
def grade_intro_ex7(answer: bool = None) -> None:
    _grade(answer, 'ex7')


@typechecked
def grade_intro_ex8(answer: bool = None) -> None:
    _grade(answer, 'ex8')


@typechecked
def grade_intro_ex9(answer: bool = None) -> None:
    _grade(answer, 'ex9')


@typechecked
def grade_intro_ex10(answer: str = None) -> None:
    _grade(answer, 'ex10')


@typechecked
def grade_intro_ex11(answer: str = None) -> None:
    _grade(answer, 'ex11')


@typechecked
def grade_intro_ex12(answer: str = None) -> None:
    _grade(answer, 'ex12')


@typechecked
def grade_intro_ex13(answer: str = None) -> None:
    _grade(answer, 'ex13')


@typechecked
def grade_intro_ex14(answer: str = None) -> None:
    _grade(answer, 'ex14')
