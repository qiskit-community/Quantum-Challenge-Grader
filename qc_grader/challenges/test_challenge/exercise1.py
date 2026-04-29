# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from pathlib import Path
from typeguard import typechecked

from qc_grader.grader.grade import grade, submit_team_name


_CHALLENGE_ID = Path(__file__).parent.name


@typechecked
def submit_name(name: str) -> None:
    submit_team_name(name, _CHALLENGE_ID)


@typechecked
def grade_ex1a(answer: str) -> None:
    grade(answer, "test-pass", _CHALLENGE_ID)


@typechecked
def grade_ex1b(answer: str) -> None:
    grade(answer, "test-fail", _CHALLENGE_ID)


@typechecked
def grade_ex1c(answer: int) -> None:
    grade(answer, "test-prime", _CHALLENGE_ID)


@typechecked
def grade_ex1d(answer: str) -> None:
    grade(answer, "test-vowels", _CHALLENGE_ID)
