#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2022
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

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex1a(answer: str) -> None:
    grade(answer, 1, challenge_id)


@typechecked
def grade_ex1b(answer: str) -> None:
    grade(answer, 2, challenge_id)


@typechecked
def grade_ex1c(answer: int) -> None:
    grade(answer, 3, challenge_id)
