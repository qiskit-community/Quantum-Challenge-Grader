#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
QGSS 2026 Lab 0 - Grading Functions
"""

from typing import List

from typeguard import typechecked
from qiskit.quantum_info import Statevector
from qc_grader.grader.grade import grade


_challenge_id = "qgss_2026"


@typechecked
def grade_lab0_ex1(backends: list) -> None:
    """
    Grade Exercise 1: Verify IBM Quantum account.

    Args:
        backends: List of backend objects from service.backends()
    """
    grade(len(backends), "lab0-ex1", _challenge_id)


@typechecked
def grade_lab0_ex2(counts: dict) -> None:
    """
    Grade Exercise 2: Verify sampler result.

    Args:
        counts: Dictionary of measurement counts
    """
    grade(counts, "lab0-ex2", _challenge_id)


@typechecked
def grade_lab0_ex3(
    c_out: List[str],
    cpp_out: List[str],
    qiskit_c_out: List[str],
    qiskit_cpp_out: List[str],
) -> None:
    """
    Grade Exercise 3: Verify C/C++ toolchain outputs.

    Args:
        c_out: Shell output from hello.c
        cpp_out: Shell output from hello.cpp
        qiskit_c_out: Shell output from hello_qiskit.c
        qiskit_cpp_out: Shell output from hello_qiskit.cpp
    """
    answer_dict = {
        "c_out": " ".join(str(x) for x in c_out),
        "cpp_out": " ".join(str(x) for x in cpp_out),
        "qiskit_c_out": " ".join(str(x) for x in qiskit_c_out),
        "qiskit_cpp_out": " ".join(str(x) for x in qiskit_cpp_out),
    }
    grade(answer_dict, "lab0-ex3", _challenge_id)


@typechecked
def grade_lab0_ex4(c_out: List[str], cpp_out: List[str]) -> None:
    """
    Grade Exercise 4: Verify C/C++ circuit outputs.

    Args:
        c_out: Shell output from C circuit program
        cpp_out: Shell output from C++ circuit program
    """
    answer_dict = {
        "c_out": " ".join(str(x) for x in c_out),
        "cpp_out": " ".join(str(x) for x in cpp_out),
    }
    grade(answer_dict, "lab0-ex4", _challenge_id)


@typechecked
def grade_lab0_ex5(sv: Statevector) -> None:
    """
    Grade Exercise 5: Verify statevector.

    Args:
        sv: Statevector object to verify
    """
    grade(sv, "lab0-ex5", _challenge_id)
