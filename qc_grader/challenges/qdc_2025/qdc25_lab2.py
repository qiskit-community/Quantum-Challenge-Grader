from typeguard import typechecked

from qiskit import QuantumCircuit
from lattice import HeavyHexLattice
from qc_grader.grader.grade import grade
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime import EstimatorV2
import numpy
from typing import List
import json

from math import pi

from collections import OrderedDict
from typing import List

import numpy as np

from qiskit import QuantumCircuit
import qiskit_ibm_runtime
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime.runtime_job_v2 import RuntimeJobV2
from qiskit_aer.primitives.estimator_v2 import EstimatorV2
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from qiskit.quantum_info import Statevector, SparsePauliOp
from qiskit.quantum_info import Operator
from qiskit.circuit.library import TwoLocal
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.primitives import StatevectorEstimator

from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKyoto
from qiskit import qpy


_challenge_id = "qdc_2025"


@typechecked
def grade_lab2_ex1(observables: List) -> None:
    grade(observables, "lab2-ex1", _challenge_id)


@typechecked
def grade_lab2_ex2(qc: QuantumCircuit) -> None:
    grade(qc, "lab2-ex2", _challenge_id)


@typechecked
def grade_lab2_ex3(qc: QuantumCircuit) -> None:
    grade(qc, "lab2-ex3", _challenge_id)


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
    grade(answer_dict, "lab2-ex4", _challenge_id)


@typechecked
def grade_lab2_ex5(backend: IBMBackend) -> None:
    if type(backend) == IBMBackend:
        answer = "true"
    else:
        answer = "false"

    grade(answer, "lab2-ex5", _challenge_id)


@typechecked
def grade_lab2_ex6(
    circuits_all_isa: List, observables_isa: List, backend: IBMBackend
) -> None:

    if type(backend) == IBMBackend:
        backend_answer = "true"
    else:
        backend_answer = "false"

    answer_dict = {
        "circuits_all_isa": circuits_all_isa,
        "observables_isa": observables_isa,
        "backend_answer": backend_answer,
    }
    grade(answer_dict, "lab2-ex6", _challenge_id)


@typechecked
def grade_lab2_ex7(estimator: EstimatorV2) -> None:
    if type(estimator) != qiskit_ibm_runtime.estimator.EstimatorV2:
        answer = "false"
    else:
        answer = "true"
    grade(answer, "lab2-ex7", _challenge_id)


@typechecked
def grade_lab2_ex8(
    pubs: list[tuple[QuantumCircuit, list[SparsePauliOp]]],
    circuits_all_isa: list[QuantumCircuit],
    observables_isa: list[SparsePauliOp],
) -> None:

    answer_dict = {
        "pubs": pubs,
        "circuits_all_isa": circuits_all_isa,
        "observables_isa": observables_isa,
    }
    grade(answer_dict, "lab2-ex8", _challenge_id)


@typechecked
def grade_lab2_ex9(job: RuntimeJobV2) -> None:
    grade(job, "lab2-ex9", _challenge_id)


@typechecked
def grade_lab2_ex10(
    chi_wave: np.ndarray,
    chi_wave_mitig: np.ndarray,
    chi_vacuum: np.ndarray,
    chi_vacuum_mitig: np.ndarray,
    results: PrimitiveResult,
) -> None:

    answer_dict = {
        "chi_wave": chi_wave,
        "chi_wave_mitig": chi_wave_mitig,
        "chi_vacuum": chi_vacuum,
        "chi_vacuum_mitig": chi_vacuum_mitig,
        "results": results,
    }

    grade(answer_dict, "lab2-ex10", _challenge_id)


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

    grade(answer_dict, "lab2-ex11", _challenge_id)


@typechecked
def grade_lab2_ex12(chi_final: np.ndarray) -> None:
    grade(chi_final, "lab2-ex12", _challenge_id)
