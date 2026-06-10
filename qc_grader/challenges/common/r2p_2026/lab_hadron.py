# (C) Copyright IBM 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Any, List

import numpy as np
import qiskit_ibm_runtime
from qiskit import QuantumCircuit
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime.runtime_job_v2 import RuntimeJobV2
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer, join_team as _join_team


_LAB = "lab_hadron"


def _create_grade_function(challenge: str):
    """Create a grade function for a specific challenge."""

    def _grade(answer: Any, exercise: str) -> None:
        grade_answer(answer, lab=_LAB, exercise=exercise, challenge=challenge)

    return _grade


def _create_join_team_function(challenge: str):
    """Create a join_team function for a specific challenge."""

    @typechecked
    def join_team(name: str) -> None:
        _join_team(name, challenge)

    return join_team


def _create_grade_lab_hadron_ex1(_grade):
    """Create grade_lab_hadron_ex1 function."""

    @typechecked
    def grade_lab_hadron_ex1(observables: List) -> None:
        _grade(observables, "ex1")

    return grade_lab_hadron_ex1


def _create_grade_lab_hadron_ex2(_grade):
    """Create grade_lab_hadron_ex2 function."""

    @typechecked
    def grade_lab_hadron_ex2(qc: QuantumCircuit) -> None:
        _grade(qc, "ex2")

    return grade_lab_hadron_ex2


def _create_grade_lab_hadron_ex3(_grade):
    """Create grade_lab_hadron_ex3 function."""

    @typechecked
    def grade_lab_hadron_ex3(qc: QuantumCircuit) -> None:
        _grade(qc, "ex3")

    return grade_lab_hadron_ex3


def _create_grade_lab_hadron_ex4(_grade):
    """Create grade_lab_hadron_ex4 function."""

    @typechecked
    def grade_lab_hadron_ex4(
        qc_wave_test: QuantumCircuit,
        qc_wave_mitig_test: QuantumCircuit,
        qc_vacuum_test: QuantumCircuit,
        qc_vacuum_mitig_test: QuantumCircuit,
    ) -> None:

        answer_dict = {
            "qc_wave_test": qc_wave_test,
            "qc_wave_mitig_test": qc_wave_mitig_test,
            "qc_vacuum_test": qc_vacuum_test,
            "qc_vacuum_mitig_test": qc_vacuum_mitig_test,
        }
        _grade(answer_dict, "ex4")

    return grade_lab_hadron_ex4


def _create_grade_lab_hadron_ex5(_grade):
    """Create grade_lab_hadron_ex5 function."""

    @typechecked
    def grade_lab_hadron_ex5(backend: IBMBackend) -> None:
        if isinstance(backend, IBMBackend):
            answer = "true"
        else:
            answer = "false"

        _grade(answer, "ex5")

    return grade_lab_hadron_ex5


def _create_grade_lab_hadron_ex7(_grade):
    """Create grade_lab_hadron_ex7 function."""

    @typechecked
    def grade_lab_hadron_ex7(estimator: EstimatorV2) -> None:
        if not isinstance(estimator, qiskit_ibm_runtime.estimator.EstimatorV2):
            answer = "false"
        else:
            answer = "true"
        _grade(answer, "ex7")

    return grade_lab_hadron_ex7


def _create_grade_lab_hadron_ex8(_grade):
    """Create grade_lab_hadron_ex8 function."""

    @typechecked
    def grade_lab_hadron_ex8(
        pubs: list[tuple[QuantumCircuit, list[SparsePauliOp]]],
        circuits_all_isa: list[QuantumCircuit],
        observables_isa: list[SparsePauliOp],
    ) -> None:

        answer_dict = {
            "pubs": pubs[:1],
            "circuits_all_isa": circuits_all_isa[:1],
            "observables_isa": observables_isa,
        }
        _grade(answer_dict, "ex8")

    return grade_lab_hadron_ex8


def _create_grade_lab_hadron_ex9(_grade):
    """Create grade_lab_hadron_ex9 function."""

    @typechecked
    def grade_lab_hadron_ex9(job: RuntimeJobV2) -> None:

        answer_dict = {
            "job_primitive_id": job.primitive_id,
            "job_status": job.status(),
            "job_inputs": len(job.inputs["pubs"]),
        }

        _grade(answer_dict, "ex9")

    return grade_lab_hadron_ex9


def _create_grade_lab_hadron_ex10(_grade):
    """Create grade_lab_hadron_ex10 function."""

    @typechecked
    def grade_lab_hadron_ex10(
        chi_wave: np.ndarray,
        chi_wave_mitig: np.ndarray,
        chi_vacuum: np.ndarray,
        chi_vacuum_mitig: np.ndarray,
        results: PrimitiveResult,
    ) -> None:

        results_list = np.array(
            [
                results[0].data.evs,
                results[1].data.evs,
                results[2].data.evs,
                results[3].data.evs,
            ]
        )

        answer_dict = {
            "chi_wave": chi_wave,
            "chi_wave_mitig": chi_wave_mitig,
            "chi_vacuum": chi_vacuum,
            "chi_vacuum_mitig": chi_vacuum_mitig,
            "results": results_list,
        }

        _grade(answer_dict, "ex10")

    return grade_lab_hadron_ex10


def _create_grade_lab_hadron_ex11(_grade):
    """Create grade_lab_hadron_ex11 function."""

    @typechecked
    def grade_lab_hadron_ex11(
        chi_wave_cp: np.ndarray,
        chi_wave: np.ndarray,
        chi_vacuum_cp: np.ndarray,
        chi_vacuum: np.ndarray,
    ) -> None:

        answer_dict = {
            "chi_wave_cp": chi_wave_cp,
            "chi_wave": chi_wave,
            "chi_vacuum_cp": chi_vacuum_cp,
            "chi_vacuum": chi_vacuum,
        }

        _grade(answer_dict, "ex11")

    return grade_lab_hadron_ex11


def _create_grade_lab_hadron_ex12(_grade):
    """Create grade_lab_hadron_ex12 function."""

    @typechecked
    def grade_lab_hadron_ex12(chi_final: np.ndarray) -> None:
        _grade(chi_final, "ex12")

    return grade_lab_hadron_ex12
