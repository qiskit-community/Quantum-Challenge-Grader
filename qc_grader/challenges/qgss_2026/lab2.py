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
QGSS 2026 Lab 2 - Grading Functions
"""

from typing import Any, Callable, TypedDict
from typeguard import typechecked
import numpy as np

from qc_grader.grader.grade import grade_answer

from qiskit import QuantumCircuit

_CHALLENGE = "qgss_2026"
_LAB = "lab2"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab2_ex1(
    basis_operations: list[str], coupling_map: list[list[int] | tuple[int, int]]
) -> None:
    """
    Grade Exercise 1: Check FakeTorino basis operations and coupling map.
    """

    answer_dict = {"basis_operations": basis_operations, "coupling_map": coupling_map}
    _grade(answer_dict, "ex1")


def _too_large_circuit(
    circuit: QuantumCircuit, max_qubits: int = 20, max_depth: int = 100
) -> bool:
    return circuit.num_qubits > max_qubits or circuit.depth() > max_depth


@typechecked
def grade_lab2_ex2(repeated_x_circuit: Callable[[int], QuantumCircuit]) -> None:
    """
    Grade Exercise 2: Check the repeated X circuit.
    """
    test_ns = [0, 1, 2, 3, 5, 10]
    repeated_x_dict = dict()
    for n in test_ns:
        circuit = repeated_x_circuit(n)
        if _too_large_circuit(circuit):
            raise ValueError(
                f"Circuit for n={n} is too large (num_qubits={circuit.num_qubits}, depth={circuit.depth()}). Please optimize your circuit."
            )
        repeated_x_dict[n] = circuit

    answer_dict = {"repeated_x_circuit": repeated_x_dict}
    _grade(answer_dict, "ex2")


Ex3InputCase = TypedDict(
    "Ex3InputCase",
    {
        "true lambda": np.float64 | float,
        "fitted lambda": np.float64 | float,
        "fit std": np.float64 | float,
    },
)

Ex3InputCaseWithoutNp = TypedDict(
    "Ex3InputCaseWithoutNp",
    {
        "true lambda": float,
        "fitted lambda": float,
        "fit std": float,
    },
)


@typechecked
def grade_lab2_ex3(lambda_fitting: list[Ex3InputCase]) -> None:
    """
    Grade Exercise 3: Check the estimated lambda vs true lambda
    """
    answer_dict = {
        "lambda_fitting_cases": [
            {
                "true lambda": float(case["true lambda"]),
                "fitted lambda": float(case["fitted lambda"]),
                "fit std": float(case["fit std"]),
            }
            for case in lambda_fitting
        ]
    }
    _grade(answer_dict, "ex3")


@typechecked
def grade_lab2_ex4(repeated_x_meas_x_circuit: Callable[[int], QuantumCircuit]) -> None:
    """
    Grade Exercise 4: Check the repeated X circuit on X basis.
    """
    test_ns = [0, 1, 2, 3, 5, 10]
    repeated_x_meas_x_dict = dict()
    for n in test_ns:
        circuit = repeated_x_meas_x_circuit(n)
        if _too_large_circuit(circuit):
            raise ValueError(
                f"Circuit for n={n} is too large (num_qubits={circuit.num_qubits}, depth={circuit.depth()}). Please optimize your circuit."
            )
        repeated_x_meas_x_dict[n] = circuit

    answer_dict = {"repeated_x_meas_x_circuit": repeated_x_meas_x_dict}
    _grade(answer_dict, "ex4")


def build_test_circuits() -> list[QuantumCircuit]:
    c1 = QuantumCircuit(2)
    c1.swap(0, 1)

    c2 = QuantumCircuit(3)
    c2.swap(0, 1)
    c2.swap(1, 2)

    c3 = QuantumCircuit(4)
    c3.swap(0, 1)
    c3.swap(1, 2)
    c3.swap(2, 3)

    c4 = QuantumCircuit(2)
    c4.h(0)
    c4.cx(0, 1)

    c5 = QuantumCircuit(3)
    c5.h(0)
    c5.cx(0, 1)
    c5.swap(1, 2)

    return [c1, c2, c3, c4, c5]


@typechecked
def grade_lab2_ex5(
    initial_layout: list[int],
    basis_gates: list[str],
    count_swap_gates: Callable[[QuantumCircuit], int],
) -> None:
    """
    Grade Exercise 5: Check the initial_layout, basis_gates and count_swap_gates function.
    """

    answer_dict = {
        "initial_layout": initial_layout,
        "basis_gates": basis_gates,
        "count_swap_gates": [
            count_swap_gates(c)
            for c in build_test_circuits()
            # (c, count_swap_gates(c)) for c in build_test_circuits()
        ],
    }
    _grade(answer_dict, "ex5")


@typechecked
def grade_lab2_ex6(build_circuit: Callable[[int], QuantumCircuit]) -> None:
    """
    Grade Exercise 6: Check the full dynamic circuit construction.
    """
    test_num_qubits = [4, 6, 8, 10, 12, 20]
    answer_dict = {"build_circuit": {str(n): build_circuit(n) for n in test_num_qubits}}
    _grade(answer_dict, "ex6")


CircuitParams = TypedDict(
    "CircuitParams",
    {
        "Number of qubits": int,
        "Depth": int,
        "2-qubit depth": int,
        "Gates": int,
        "Multi-qubit gates": int,
        "Number of ancillas": int,
    },
)


@typechecked
def grade_lab2_ex7(
    quantum_circuit_params: Callable[[QuantumCircuit], CircuitParams],
    build_circuit: Callable[[int], QuantumCircuit],
) -> None:
    """
    Grade Exercise 7: Check the quantum circuit parameters.
    """
    test_num_qubits = [4, 6, 8]

    answer_dict = {
        "circuit_params": {
            str(n): quantum_circuit_params(build_circuit(n)) for n in test_num_qubits
        }
    }
    _grade(answer_dict, "ex7")
