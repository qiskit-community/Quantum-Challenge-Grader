# (C) Copyright IBM 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typeguard import typechecked, check_type

from qc_grader.grader.grade import grade

_challenge_id = "qdc_2025"


@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status is False:
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
def grade_lab6_ex2(molecule_name: str, casci_E: float) -> None:

    answer_dict = {"molecule_name": molecule_name, "casci_E": casci_E}

    grade(answer_dict, "lab6-ex2", _challenge_id)


@typechecked
def grade_lab6_ex3(molecule_name: str, sqd_E: list) -> None:

    for E in sqd_E:
        check_type(E[0], int)
        check_type(E[1], float)
        check_type(E[2], str)

    answer_dict = {"molecule_name": molecule_name, "sqd_E": sqd_E}

    grade(answer_dict, "lab6-ex3", _challenge_id)
