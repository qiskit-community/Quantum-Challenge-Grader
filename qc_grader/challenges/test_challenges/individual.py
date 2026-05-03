# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typeguard import typechecked
from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_CHALLENGE_ID = "test_individual"


@typechecked
def grade_success(answer: str) -> None:
    grade(answer, "test-pass", _CHALLENGE_ID)


@typechecked
def grade_fail(answer: str) -> None:
    grade(answer, "test-fail", _CHALLENGE_ID)


@typechecked
def grade_prime(answer: int) -> None:
    grade(answer, "test-prime", _CHALLENGE_ID)


@typechecked
def grade_vowels(answer: str) -> None:
    grade(answer, "test-vowels", _CHALLENGE_ID)


@typechecked
def grade_circuit(qc: QuantumCircuit) -> None:
    grade(qc, "test-circuit", _CHALLENGE_ID)
