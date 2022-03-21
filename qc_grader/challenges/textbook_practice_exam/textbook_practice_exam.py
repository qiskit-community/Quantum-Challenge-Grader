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
from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade

challenge_id = Path(__file__).parent.name


@typechecked
def grade_problem1c(answer: QuantumCircuit) -> None:
    grade(answer, 1, challenge_id)  # 1c


@typechecked
def grade_problem2a(answer: QuantumCircuit) -> None:
    grade(answer, 2, challenge_id)  # 2a


@typechecked
def grade_problem2b(answer: QuantumCircuit) -> None:
    grade(answer, 3, challenge_id)  # 2b


@typechecked
def grade_problem2c(answer: QuantumCircuit) -> None:
    grade(answer, 4, challenge_id)  # 2c
