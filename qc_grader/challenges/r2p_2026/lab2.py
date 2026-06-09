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

_CHALLENGE = "r2p_2026"
_LAB = "lab4b"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def submit_name(name: str) -> None:
    submit_team_name(name, _CHALLENGE)


@typechecked
def grade_lab2_ex1(perturbed_tfim_hamiltonian: Callable) -> None:
    H_test = perturbed_tfim_hamiltonian(NUM_QUBITS, J, H_X, H_Z)

    answer_dict = {
        "H_test": H_test,
    }
    _grade(answer_dict, "ex1")


@typechecked
def grade_lab2_ex2(
    construct_krylov_circuits: Callable, perturbed_tfim_hamiltonian: Callable
) -> None:

    H_ref = perturbed_tfim_hamiltonian(NUM_QUBITS, J, H_X, H_Z)
    circs_test = construct_krylov_circuits(H_ref, PSI, KRYLOV_D, NUM_TROTTER_STEPS, DT)

    answer_dict = {
        "circs_test": circs_test,
        "H_ref": H_ref,
    }
    _grade(answer_dict, "ex2")


@typechecked
def grade_lab2_ex3(bitstrings_test: np.ndarray, H_test: SparsePauliOp) -> None:

    answer_dict = {
        "bitstrings_test": bitstrings_test,
        "H_test": H_test,
    }
    _grade(answer_dict, "ex3")


@typechecked
def grade_lab2_ex4(siam_hamiltonian_momentum: Callable) -> None:

    H_test = siam_hamiltonian_momentum(
        NUM_ORBS, HYBRIDIZATION, HOPPING, ONSITE, CHEMICAL_POTENTIAL
    )

    H_test = (
        np.round(np.array(H_test[0], dtype=np.float64), decimals=12),
        np.round(np.array(H_test[1], dtype=np.float64), decimals=12),
    )
    _grade((H_test[0].tolist(), H_test[1].tolist()), "ex4")


@typechecked
def grade_lab2_ex5(
    construct_krylov_siam: Callable, siam_hamiltonian_momentum: Callable
) -> None:

    H_ref = siam_hamiltonian_momentum(
        NUM_ORBS, HYBRIDIZATION, HOPPING, ONSITE, CHEMICAL_POTENTIAL
    )

    H_ref = (
        np.round(np.array(H_ref[0], dtype=np.float64), decimals=12),
        np.round(np.array(H_ref[1], dtype=np.float64), decimals=12),
    )

    circs_test = construct_krylov_siam(NUM_ORBS, IMPURITY_INDEX, H_ref, DT, KRYLOV_D)
    _grade(circs_test, "ex5")


@typechecked
def grade_lab2_ex6(
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
