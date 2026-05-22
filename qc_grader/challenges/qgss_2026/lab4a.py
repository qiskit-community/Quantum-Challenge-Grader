# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
QGSS 2026 Lab 4a - Grading Functions
"""

from typing import Any

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab4a"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)

@typechecked
def grade_lab4a_ex1(criteria_1: str, criteria_2: str) -> None:
    """
    Grade Exercise 1: Two essential criteria for Quantum Advantage 
    """
    _grade([criteria_1, criteria_2], "ex1")

@typechecked
def grade_lab4a_ex2(energy: float, expectation_value: float) -> None:
    """
    Grade Exercise 2: Exploring the Quantum Advantage Tracker
    """
    _grade([energy, expectation_value], "ex2")
