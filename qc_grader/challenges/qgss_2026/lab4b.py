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
QGSS 2026 Lab 4b - Grading Functions
"""

from typing import Any, Callable
import warnings
from dataclasses import asdict

from typeguard import typechecked, check_type

import numpy as np
import networkx as nx
from qiskit.quantum_info import SparsePauliOp
from qiskit import QuantumCircuit
from qiskit_ibm_runtime.options import SamplerOptions
from qiskit_ibm_runtime import RuntimeJobV2
from qiskit_ibm_runtime.fake_provider.local_runtime_job import LocalRuntimeJob

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab4b"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


def _dict_contains(full_dict, subset_dict):
    """Check if full_dict contains all key-value pairs from subset_dict (recursively)."""
    for key, value in subset_dict.items():
        if key not in full_dict:
            return False
        if isinstance(value, dict) and isinstance(full_dict[key], dict):
            if not _dict_contains(full_dict[key], value):
                return False
        elif full_dict[key] != value:
            return False
    return True


@typechecked
def grade_lab4b_ex1a(partition_graph: nx.Graph) -> None:
    """
    Grade Exercise 1a: Create the partition graph.
    """
    _grade(partition_graph, "ex1a")


@typechecked
def grade_lab4b_ex1b(
    partition_hamiltonian: SparsePauliOp, circuit: QuantumCircuit
) -> None:
    """
    Grade Exercise 1b: From graph to Hamiltonian and quantum circuit.
    """
    answer_dict = {"partition_hamiltonian": partition_hamiltonian, "circuit": circuit}
    _grade(answer_dict, "ex1b")


@typechecked
def grade_lab4b_ex2(
    options_list: list[SamplerOptions],
    counts_list: list[dict[str, int]],
    m3_quasis_v3: dict[str, float | np.floating],
    m3_quasis_v4: dict[str, float | np.floating],
    job_list: list[RuntimeJobV2 | LocalRuntimeJob],
):
    """
    Grade Exercise 2: Error suppression techniques
    """

    # Compare job options with expected options
    for i, (job, expected) in enumerate(zip(job_list, options_list), start=1):
        if isinstance(job, RuntimeJobV2):
            job_opts = asdict(job.inputs.get("options", {}))
            exp_opts = asdict(expected)

            if not _dict_contains(exp_opts, job_opts):
                raise ValueError(f"job_v{i} options do not match expected options")
        else:
            warnings.warn(
                f"job_v{i} is not a RuntimeJobV2 instance. You appear to be using a simulator, but this exercise is supposed to use a real hardware backend.",
                UserWarning,
            )
    # Go through these values m3_quasis_v3 and m3_quasis_v4 and convert np.floating into float
    m3_quasis_v3 = {k: float(v) for k, v in m3_quasis_v3.items()}
    m3_quasis_v4 = {k: float(v) for k, v in m3_quasis_v4.items()}
    # Transform options_list elements into a dictionary
    options_dicts = [asdict(options) for options in options_list]

    answer_dict = {
        "options_list": options_dicts,
        "counts_list": counts_list,
        "m3_quasis_v3": m3_quasis_v3,
        "m3_quasis_v4": m3_quasis_v4,
    }
    _grade(answer_dict, "ex2")


# Type alias for reduce_qubits_with_pce callable
ReduceQubitsWithPCE = Callable[[int], int]


@typechecked
def grade_lab4b_ex3a(
    reduce_qubits_with_pce: ReduceQubitsWithPCE,
    node_x: list[int],
    node_y: list[int],
    node_z: list[int],
) -> None:
    """
    Grade Exercise 3a: Implement Pauli Correlation Encoding: Qubit reduction
    """
    initial_qubits = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]

    def _validate_and_reduce(qubit: int) -> int:
        result = reduce_qubits_with_pce(qubit)
        check_type(result, int)
        return result

    final_qubits = [_validate_and_reduce(qubit) for qubit in initial_qubits]

    answer_dict = {
        "initial_qubits": initial_qubits,
        "final_qubits": final_qubits,
        "node_x": node_x,
        "node_y": node_y,
        "node_z": node_z,
    }

    _grade(answer_dict, "ex3a")


@typechecked
def grade_lab4b_ex3b(
    pauli_correlation_encoding_x: list[SparsePauliOp],
    pauli_correlation_encoding_y: list[SparsePauliOp],
    pauli_correlation_encoding_z: list[SparsePauliOp],
) -> None:
    """
    Grade Exercise 3b: Implement Pauli Correlation Encoding: Hamiltonian construction
    """

    answer_dict = {
        "pauli_correlation_encoding_x": pauli_correlation_encoding_x,
        "pauli_correlation_encoding_y": pauli_correlation_encoding_y,
        "pauli_correlation_encoding_z": pauli_correlation_encoding_z,
    }

    _grade(answer_dict, "ex3b")
