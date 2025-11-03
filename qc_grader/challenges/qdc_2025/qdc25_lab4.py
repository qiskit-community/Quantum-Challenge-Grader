from typeguard import typechecked

from qc_grader.grader.grade import grade

from typing import Callable
import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import  SparsePauliOp



_challenge_id = "qdc_2025"
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

@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status == False:
        print(message)
    else:
        print("Team name submitted.")

@typechecked
def grade_lab4_ex1(perturbed_tfim_hamiltonian: Callable) -> None:
    H_test = perturbed_tfim_hamiltonian(NUM_QUBITS, J, H_X, H_Z)

    grade(H_test, "lab4-ex1", _challenge_id)


@typechecked
def grade_lab4_ex2(construct_krylov_circuits: Callable, perturbed_tfim_hamiltonian: Callable) -> None:


    H_ref = perturbed_tfim_hamiltonian(
        NUM_QUBITS, J, H_X, H_Z
    )
    circs_test = construct_krylov_circuits(H_ref, PSI, KRYLOV_D, NUM_TROTTER_STEPS, DT)

    answer_dict = {
        "circs_test": circs_test,
        "H_ref": H_ref,
    }

    grade(answer_dict, "lab4-ex2", _challenge_id)

@typechecked
def grade_lab4_ex3(bitstrings_test: np.ndarray, H_test: SparsePauliOp) -> None:

    answer_dict = {
        "bitstrings_test": bitstrings_test,
        "H_test": H_test,
    }

    grade(answer_dict, "lab4-ex3", _challenge_id)

@typechecked
def grade_lab4_ex4(siam_hamiltonian_momentum: Callable) -> None:

    H_test = siam_hamiltonian_momentum(
        NUM_ORBS, HYBRIDIZATION, HOPPING, ONSITE, CHEMICAL_POTENTIAL
    )

    answer_dict = {
        "H_test_0": H_test[0],
        "H_test_1": H_test[1]
    }

    grade(answer_dict, "lab4-ex4", _challenge_id)


@typechecked
def grade_lab4_ex5(construct_krylov_siam: Callable, siam_hamiltonian_momentum: Callable) -> None:

    H_ref = siam_hamiltonian_momentum(
        NUM_ORBS, HYBRIDIZATION, HOPPING, ONSITE, CHEMICAL_POTENTIAL
    )
    circs_test = construct_krylov_siam(NUM_ORBS, IMPURITY_INDEX, H_ref, DT, KRYLOV_D)



    grade(circs_test, "lab4-ex5", _challenge_id)

@typechecked
def grade_lab4_ex6(result, num_orbs: int, hopping: float, onsite: float, hybridization: float, chemical_potential: float) -> None:

    E_skqd = min(result)

    answer_dict = {
        "num_orbs": num_orbs,
        "hopping": hopping,
        "onsite": onsite,
        "hybridization": hybridization,
        "chemical_potential": chemical_potential,
        "E_skqd": E_skqd,
    }

    grade(answer_dict, "lab4-ex6", _challenge_id)