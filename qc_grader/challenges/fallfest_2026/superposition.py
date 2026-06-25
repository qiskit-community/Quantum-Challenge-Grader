"""
Fall Fest 2026 Lab 11 - Superposition Homework - Grading Functions
"""

from typing import Any, List
from typeguard import typechecked
from qc_grader.grader.grade import grade_answer

_CHALLENGE = "fallfest_2026"
_LAB = "superposition"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_superposition_ex1(answer: bool) -> None:
    _grade(answer, "ex1")


@typechecked
def grade_superposition_ex2(answer: bool) -> None:
    _grade(answer, "ex2")


@typechecked
def grade_superposition_ex3(answer: bool) -> None:
    _grade(answer, "ex3")


@typechecked
def grade_superposition_ex4(answer: str) -> None:
    _grade(answer, "ex4")


@typechecked
def grade_superposition_ex5(answer: List[str]) -> None:
    _grade(answer, "ex5")


@typechecked
def grade_superposition_ex6(answer: str) -> None:
    _grade(answer, "ex6")


@typechecked
def grade_superposition_ex7(answer: str) -> None:
    _grade(answer, "ex7")


@typechecked
def grade_superposition_ex8(answer: str) -> None:
    _grade(answer, "ex8")
