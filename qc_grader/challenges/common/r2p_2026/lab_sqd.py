# (C) Copyright IBM 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer, submit_team_name

from typing import Any, Callable
import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp


NUM_QUBITS = 8
J = 1.0
H_X = 0.1
H_Z = 0.2
PSI = QuantumCircuit(NUM_QUBITS)
KRYLOV_D = 4
NUM_TROTTER_STEPS = 1
DT = 0.15
# Part 2
NUM_ORBS = 10
HOPPING = 1.0
ONSITE = 5
HYBRIDIZATION = 1.0
CHEMICAL_POTENTIAL = -0.5 * ONSITE
NBATH = NUM_ORBS - 1
IMPURITY_INDEX = (NBATH) // 2

_LAB = "lab_sqd"


def _create_grade_function(challenge: str):
    """Create a grade function for a specific challenge."""

    def _grade(answer: Any, exercise: str) -> None:
        grade_answer(answer, lab=_LAB, exercise=exercise, challenge=challenge)

    return _grade


def _create_submit_name_function(challenge: str):
    """Create a submit_name function for a specific challenge."""

    @typechecked
    def submit_name(name: str) -> None:
        submit_team_name(name, challenge)

    return submit_name


def _create_grade_lab_sqd_ex1(_grade):
    """Create grade_lab_sqd_ex1 function."""

    @typechecked
    def grade_lab_sqd_ex1(perturbed_tfim_hamiltonian: Callable) -> None:
        H_test = perturbed_tfim_hamiltonian(NUM_QUBITS, J, H_X, H_Z)

        answer_dict = {
            "H_test": H_test,
        }
        _grade(answer_dict, "ex1")

    return grade_lab_sqd_ex1


def _create_grade_lab_sqd_ex2(_grade):
    """Create grade_lab_sqd_ex2 function."""

    @typechecked
    def grade_lab_sqd_ex2(
        construct_krylov_circuits: Callable, perturbed_tfim_hamiltonian: Callable
    ) -> None:

        H_ref = perturbed_tfim_hamiltonian(NUM_QUBITS, J, H_X, H_Z)
        circs_test = construct_krylov_circuits(
            H_ref, PSI, KRYLOV_D, NUM_TROTTER_STEPS, DT
        )

        answer_dict = {
            "circs_test": circs_test,
            "H_ref": H_ref,
        }
        _grade(answer_dict, "ex2")

    return grade_lab_sqd_ex2


def _create_grade_lab_sqd_ex3(_grade):
    """Create grade_lab_sqd_ex3 function."""

    @typechecked
    def grade_lab_sqd_ex3(bitstrings_test: np.ndarray, H_test: SparsePauliOp) -> None:

        answer_dict = {
            "bitstrings_test": bitstrings_test,
            "H_test": H_test,
        }
        _grade(answer_dict, "ex3")

    return grade_lab_sqd_ex3


def _create_grade_lab_sqd_ex4(_grade):
    """Create grade_lab_sqd_ex4 function."""

    @typechecked
    def grade_lab_sqd_ex4(siam_hamiltonian_momentum: Callable) -> None:

        H_test = siam_hamiltonian_momentum(
            NUM_ORBS, HYBRIDIZATION, HOPPING, ONSITE, CHEMICAL_POTENTIAL
        )

        H_test = (
            np.round(np.array(H_test[0], dtype=np.float64), decimals=12),
            np.round(np.array(H_test[1], dtype=np.float64), decimals=12),
        )
        _grade((H_test[0].tolist(), H_test[1].tolist()), "ex4")

    return grade_lab_sqd_ex4


def _create_grade_lab_sqd_ex5(_grade):
    """Create grade_lab_sqd_ex5 function."""

    @typechecked
    def grade_lab_sqd_ex5(
        construct_krylov_siam: Callable, siam_hamiltonian_momentum: Callable
    ) -> None:

        H_ref = siam_hamiltonian_momentum(
            NUM_ORBS, HYBRIDIZATION, HOPPING, ONSITE, CHEMICAL_POTENTIAL
        )

        H_ref = (
            np.round(np.array(H_ref[0], dtype=np.float64), decimals=12),
            np.round(np.array(H_ref[1], dtype=np.float64), decimals=12),
        )

        circs_test = construct_krylov_siam(
            NUM_ORBS, IMPURITY_INDEX, H_ref, DT, KRYLOV_D
        )
        _grade(circs_test, "ex5")

    return grade_lab_sqd_ex5


def _create_grade_lab_sqd_ex6(_grade):
    """Create grade_lab_sqd_ex6 function."""

    @typechecked
    def grade_lab_sqd_ex6(
        result,
        num_orbs: int,
        hopping: float,
        onsite: float,
        hybridization: float,
        chemical_potential: float,
    ) -> None:

        E_skqd = min(result)

        answer_dict = {
            "num_orbs": num_orbs,
            "hopping": hopping,
            "onsite": onsite,
            "hybridization": hybridization,
            "chemical_potential": chemical_potential,
            "E_skqd": E_skqd,
        }
        _grade(answer_dict, "ex6")

    return grade_lab_sqd_ex6
