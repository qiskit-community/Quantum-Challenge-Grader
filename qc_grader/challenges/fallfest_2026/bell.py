"""
Fall Fest 2026 Lab 8 - Bell Inequality - Grading Functions
"""

from typing import Any, List
from typeguard import typechecked
from qc_grader.grader.grade import grade_answer

_CHALLENGE = "fallfest_2026"
_LAB = "bell"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_bell_ex1(answer: bool) -> None:
    _grade(answer, "ex1")


@typechecked
def grade_bell_ex2(answer: bool) -> None:
    _grade(answer, "ex2")


@typechecked
def grade_bell_ex3(answer: bool) -> None:
    _grade(answer, "ex3")


@typechecked
def grade_bell_ex4(answer: bool) -> None:
    _grade(answer, "ex4")


@typechecked
def grade_bell_ex5(answer: bool) -> None:
    _grade(answer, "ex5")


@typechecked
def grade_bell_ex6(answer: bool) -> None:
    _grade(answer, "ex6")


@typechecked
def grade_bell_ex7(answer: bool) -> None:
    _grade(answer, "ex7")


@typechecked
def grade_bell_ex8(answer: str) -> None:
    _grade(answer, "ex8")


@typechecked
def grade_bell_ex9(answer: List[str]) -> None:
    _grade(answer, "ex9")


@typechecked
def grade_bell_ex10(answer: str) -> None:
    _grade(answer, "ex10")


@typechecked
def grade_bell_ex11(answer: List[str]) -> None:
    _grade(answer, "ex11")


@typechecked
def grade_bell_ex12(answer: List[str]) -> None:
    _grade(answer, "ex12")


@typechecked
def grade_bell_ex13(answer: str) -> None:
    _grade(answer, "ex13")


@typechecked
def grade_bell_ex14(answer: str) -> None:
    _grade(answer, "ex14")


@typechecked
def grade_bell_ex15(answer: str) -> None:
    _grade(answer, "ex15")


@typechecked
def grade_bell_ex16(answer: str) -> None:
    _grade(answer, "ex16")


@typechecked
def grade_bell_ex17(answer: str) -> None:
    _grade(answer, "ex17")


@typechecked
def grade_bell_ex18(answer: str) -> None:
    _grade(answer, "ex18")
