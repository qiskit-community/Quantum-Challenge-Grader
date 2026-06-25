"""
Fall Fest 2026 Lab 4 - Quantum Teleportation - Grading Functions
"""

from typing import Any, List
from typeguard import typechecked
from qc_grader.grader.grade import grade_answer

_CHALLENGE = "fallfest_2026"
_LAB = "teleport"


def _grade(answer: Any, exercise: str):
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_teleport_ex1(answer: bool):
    _grade(answer, "ex1")


@typechecked
def grade_teleport_ex2(answer: bool):
    _grade(answer, "ex2")


@typechecked
def grade_teleport_ex3(answer: bool):
    _grade(answer, "ex3")


@typechecked
def grade_teleport_ex4(answer: str):
    _grade(answer, "ex4")


@typechecked
def grade_teleport_ex5(answer: str):
    _grade(answer, "ex5")


@typechecked
def grade_teleport_ex6(answer: List[str]):
    _grade(answer, "ex6")


@typechecked
def grade_teleport_ex7(answer: str):
    _grade(answer, "ex7")


@typechecked
def grade_teleport_ex8(answer: str):
    _grade(answer, "ex8")


@typechecked
def grade_teleport_ex9(answer: str):
    _grade(answer, "ex9")
