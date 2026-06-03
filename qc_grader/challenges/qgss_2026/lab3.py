# (C) Copyright IBM 2026

"""
QGSS 2026 Lab 3 - Grading Functions
"""

from typing import Any

from typeguard import typechecked

from qiskit import QuantumCircuit
from qiskit.quantum_info import PauliLindbladMap, SparsePauliOp

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab3"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab3_ex5(
    circuit_ising: QuantumCircuit,
    mirrored_circuit: QuantumCircuit,
    boxed: QuantumCircuit,
    obs_list: list[SparsePauliOp],
    forward_list: list[dict[str, PauliLindbladMap]],
    backward_bound: dict[str, PauliLindbladMap],
) -> None:
    """
    Grade Exercise 5: Investigate the locality of 3 observables for 15 qubits
    """
    # convert PauliLindbladMap to sparse lists
    for key in backward_bound:
        backward_bound[key] = backward_bound[key].to_sparse_list()

    for i, d in enumerate(forward_list):
        for key, pl_map in d.items():
            forward_list[i][key] = pl_map.to_sparse_list()

    answer_dict = {
        "circuit_ising": circuit_ising,
        "mirrored_circuit": mirrored_circuit,
        "boxed": boxed,
        "obs_list": obs_list,
        "forward_list": forward_list,
        "backward_bound": backward_bound,
    }

    _grade(answer_dict, "ex5")
