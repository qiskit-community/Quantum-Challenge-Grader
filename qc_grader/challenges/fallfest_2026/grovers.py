"""
Fall Fest 2026 Lab - Grover's Algorithm - Grading Functions
"""
from typing import Any
from typeguard import typechecked
from qc_grader.grader.grade import grade_answer
_CHALLENGE = 'fallfest_2026'
_LAB = 'grovers'


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_grovers_ex1(answer: bool) -> None:
    _grade(answer, 'ex1')


@typechecked
def grade_grovers_ex2(answer: bool) -> None:
    _grade(answer, 'ex2')


@typechecked
def grade_grovers_ex3(answer: bool) -> None:
    _grade(answer, 'ex3')


@typechecked
def grade_grovers_ex4(answer: str) -> None:
    _grade(answer, 'ex4')


@typechecked
def grade_grovers_ex5(answer: str) -> None:
    _grade(answer, 'ex5')


@typechecked
def grade_grovers_ex6(answer: str) -> None:
    _grade(answer, 'ex6')


@typechecked
def grade_grovers_ex7(answer: str) -> None:
    _grade(answer, 'ex7')


@typechecked
def grade_grovers_ex8(answer: str) -> None:
    _grade(answer, 'ex8')
