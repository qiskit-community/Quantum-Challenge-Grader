#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_problem1c(answer: QuantumCircuit) -> None:
    grade(answer, 'problem1c', challenge_id)


@typechecked
def grade_problem2a(answer: QuantumCircuit) -> None:
    grade(answer, 'problem2a', challenge_id)


@typechecked
def grade_problem2b(answer: QuantumCircuit) -> None:
    grade(answer, 'problem2b', challenge_id)


@typechecked
def grade_problem2c(answer: QuantumCircuit) -> None:
    grade(answer, 'problem2c', challenge_id)
