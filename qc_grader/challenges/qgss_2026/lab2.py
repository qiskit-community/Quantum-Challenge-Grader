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
QGSS 2026 Lab 2 - Grading Functions
"""

from typing import Any

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab2"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab2_ex1(basis_operations: list[str],
                   coupling_map: list[list[int] | tuple[int, int]]) -> None:
    """
    Grade Exercise 1: Check FakeTorino basis operations and coupling map.
    """
    
    answer_dict = {"basis_operations": basis_operations,
                   "coupling_map": [(q1, q2) for q1, q2 in coupling_map]}
    _grade(answer_dict, "ex1")
