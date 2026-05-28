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
QGSS 2026 Lab 1 - Grading Functions
"""

from typing import Any, TypedDict

from qiskit import QuantumCircuit
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab1"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab1_ex1(qc: QuantumCircuit) -> None:
    """Grade Exercise 1: Bell state (|01⟩ + |10⟩) / √2."""
    _grade(qc, "ex1")


Ex2Input = TypedDict("Ex2Input", {"a": int, "b": int})


@typechecked
def grade_lab1_ex2(predictions: Ex2Input) -> None:
    """Grade Exercise 2: predicted depths of Circuit A and Circuit B.

    Example:
        grade_lab1_ex2({"a": your_answer_a, "b": your_answer_b})
    """
    _grade(predictions, "ex2")


@typechecked
def grade_lab1_ex3(qc: QuantumCircuit) -> None:
    """Grade Exercise 3: depth-5 16-qubit GHZ via recursive fan-out."""
    _grade(qc, "ex3")


@typechecked
def grade_lab1_ex4(qc: QuantumCircuit) -> None:
    """Grade Exercise 4: 3-qubit GHZ using only nearest-neighbor CX gates."""
    _grade(qc, "ex4")


@typechecked
def grade_lab1_ex5(qc: QuantumCircuit) -> None:
    """Grade Exercise 5: depth-4 5-qubit GHZ from the middle."""
    _grade(qc, "ex5")


@typechecked
def grade_lab1_ex6(qc: QuantumCircuit) -> None:
    """Grade Exercise 6: 7-qubit GHZ on the T-shape heavy-hex subgraph."""
    _grade(qc, "ex6")


@typechecked
def grade_lab1_ex7(qc: QuantumCircuit) -> None:
    """Grade Exercise 7: 64-qubit BFS spanning-tree GHZ on FakeTorino."""
    _grade(qc, "ex7")
