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

from typeguard import typechecked
from qiskit.quantum_info import Statevector
from qc_grader.grader.grade import grade


_challenge_id = "qgss_2026"


@typechecked
def grade_lab0_ex1(service) -> None:
    """
    Grade Exercise 1
    
    Args:
        service: QiskitRuntimeService object
    """
    # QiskitRuntimeService cannot be serialized, so we extract validity
    # and send as a simple string
    try:
        if service is not None and hasattr(service, "backends"):
            # Try to actually call backends() to verify it's functional
            _ = service.backends()
            answer = "valid"
        else:
            answer = "invalid"
    except Exception:
        answer = "invalid"
    
    grade(answer, "lab0-ex1", _challenge_id)


@typechecked
def grade_lab0_ex2(counts: dict) -> None:
    """
    Grade Exercise 2:
    
    Args:
        counts: Dictionary of measurement counts
    """
    # counts is already a dict, which is JSON-native
    # Server will verify the ratio is close to 50/50
    grade(counts, "lab0-ex2", _challenge_id)


@typechecked
def grade_lab0_ex3(c_out, cpp_out, qiskit_c_out, qiskit_cpp_out) -> None:
    """
    Grade Exercise 3
    
    Args:
        c_out: Shell output from C hello world
        cpp_out: Shell output from C++ hello world
        qiskit_c_out: Shell output from Qiskit C hello world
        qiskit_cpp_out: Shell output from Qiskit C++ hello world
    """
    # Shell output objects (SList) cannot be serialized
    # Convert to strings and bundle in a dict
    answer_dict = {
        "c_out": " ".join(str(x) for x in c_out),
        "cpp_out": " ".join(str(x) for x in cpp_out),
        "qiskit_c_out": " ".join(str(x) for x in qiskit_c_out),
        "qiskit_cpp_out": " ".join(str(x) for x in qiskit_cpp_out),
    }
    grade(answer_dict, "lab0-ex3", _challenge_id)


@typechecked
def grade_lab0_ex4(c_out, cpp_out) -> None:
    """
    Grade Exercise 4
    
    Args:
        c_out: Shell output from C  circuit
        cpp_out: Shell output from C++  circuit
    """
    # Convert shell outputs to strings and bundle in a dict
    answer_dict = {
        "c_out": " ".join(str(x) for x in c_out),
        "cpp_out": " ".join(str(x) for x in cpp_out),
    }
    grade(answer_dict, "lab0-ex4", _challenge_id)


@typechecked
def grade_lab0_ex5(sv: Statevector) -> None:
    """
    Grade Exercise 5
    
    Args:
        sv: Statevector object to verify
    """
    # Statevector is supported by the serializer (dump_state_vector)
    # Server will reconstruct and compare using state_fidelity
    grade(sv, "lab0-ex5", _challenge_id)

# Made with Bob
