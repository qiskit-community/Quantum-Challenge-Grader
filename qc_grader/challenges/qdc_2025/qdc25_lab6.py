from typeguard import typechecked, check_type

from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade
import numpy

_challenge_id = "qdc_2025"

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
def grade_lab6_ex1(molecule_name: str, hartree_fock_E: float) -> None:

    answer_dict = {
        "molecule_name": molecule_name,
        "hartree_fock_E": hartree_fock_E,
    }

    grade(answer_dict, "lab6-ex1", _challenge_id)


@typechecked
def grade_lab6_ex2(molecule_name: str, hartree_fock_E: float, casci_E: float) -> None:

    answer_dict = {
        "molecule_name": molecule_name,
        "hartree_fock_E": hartree_fock_E,
        "casci_E": casci_E
    }

    grade(answer_dict, "lab6-ex2", _challenge_id)

@typechecked
def grade_lab6_ex3(molecule_name: str, hartree_fock: float, casci_E: float, sqd_E: list) -> None:

    check_type(sqd_E[0], int)
    check_type(sqd_E[1], float)
    check_type(sqd_E[2], )

    answer_dict = {
        "molecule_name": molecule_name,
        "hartree_fock": hartree_fock,
        "casci_E": casci_E,
        "sqd_E": sqd_E
    }

    grade(answer_dict, "lab6-ex3", _challenge_id)