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

from qc_grader.grader.grade import grade_answer, submit_team_name

_CHALLENGE_ID = "qdc_2025"
_LAB_ID = "lab2"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB_ID, exercise=exercise, challenge=_CHALLENGE_ID)


@typechecked
def submit_name(name: str) -> None:
    submit_team_name(name, _CHALLENGE_ID)


@typechecked
def grade_lab2_ex1(observables: List) -> None:
    _grade(observables, "ex1")


@typechecked
def grade_lab2_ex2(qc: QuantumCircuit) -> None:
    _grade(qc, "ex2")


@typechecked
def grade_lab2_ex3(qc: QuantumCircuit) -> None:
    _grade(qc, "ex3")


@typechecked
def grade_lab2_ex4(
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


@typechecked
def grade_lab2_ex5(backend: IBMBackend) -> None:
    if isinstance(backend, IBMBackend):
        answer = "true"
    else:
        answer = "false"

    _grade(answer, "ex5")


@typechecked
def grade_lab2_ex7(estimator: EstimatorV2) -> None:
    if not isinstance(estimator, qiskit_ibm_runtime.estimator.EstimatorV2):
        answer = "false"
    else:
        answer = "true"
    _grade(answer, "ex7")


@typechecked
def grade_lab2_ex8(
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


@typechecked
def grade_lab2_ex9(job: RuntimeJobV2) -> None:

    answer_dict = {
        "job_primitive_id": job.primitive_id,
        "job_status": job.status(),
        "job_inputs": len(job.inputs["pubs"]),
    }

    _grade(answer_dict, "ex9")


@typechecked
def grade_lab2_ex10(
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


@typechecked
def grade_lab2_ex11(
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


@typechecked
def grade_lab2_ex12(chi_final: np.ndarray) -> None:
    _grade(chi_final, "ex12")
