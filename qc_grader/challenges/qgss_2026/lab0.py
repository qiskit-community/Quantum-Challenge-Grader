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
from qiskit_ibm_runtime.ibm_backend import IBMBackend

_CHALLENGE_ID = "qgss_2026"


def grade_lab0_ex1() -> None:
    """
    Grade Exercise 1: Test your IBM Quantum account connection.

    This is a simple "Hello World" exercise to verify that:
    - Your IBM Quantum account is properly configured
    - You can successfully submit answers to the grading server
    - The grading system is working correctly

    Simply call this function with no arguments:
        grade_lab0_ex1()
    """
    grade("hello", "lab0-ex1", _CHALLENGE_ID)


@typechecked
def grade_lab0_ex2(counts: dict[str, int]) -> None:
    """
    Grade Exercise 2: Verify sampler result.

    Args:
        counts: Dictionary of measurement counts
    """
    grade(counts, "lab0-ex2", _CHALLENGE_ID)


@typechecked
def grade_lab0_ex3(exp_val: float) -> None:
    """
    Grade Exercise 3: Verify Estimator result.

    Args:
        exp_val: Expectation value from Estimator
    """
    grade(exp_val, "lab0-ex3", _CHALLENGE_ID)


@typechecked
def grade_lab0_ex4(c_out: list[str], cpp_out: list[str]) -> None:
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
    grade(answer_dict, "lab0-ex4", _CHALLENGE_ID)


@typechecked
def grade_lab0_ex5(sv: Statevector) -> None:
    """
    Grade Exercise 5: Verify statevector.

    Args:
        sv: Statevector object to verify
    """
    grade(sv, "lab0-ex5", _CHALLENGE_ID)

