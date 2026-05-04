# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Any

from qiskit import QuantumCircuit
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE_ID = "test_individual"
_LAB_ID = "test"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB_ID, exercise=exercise, challenge=_CHALLENGE_ID)


@typechecked
def grade_success(answer: str) -> None:
    _grade(answer, "pass")


@typechecked
def grade_fail(answer: str) -> None:
    _grade(answer, "fail")


@typechecked
def grade_prime(answer: int) -> None:
    _grade(answer, "prime")


@typechecked
def grade_vowels(answer: str) -> None:
    _grade(answer, "vowels")


@typechecked
def grade_circuit(qc: QuantumCircuit) -> None:
    _grade(qc, "circuit")
