# (C) Copyright IBM 2026

"""
QGSS 2026 Lab 3 - Grading Functions
"""

from typing import Any

from qiskit import QuantumCircuit
from typeguard import typechecked

from qiskit.circuit import BoxOp
from qiskit.quantum_info import PauliLindbladMap, SparsePauliOp

from qc_grader.grader.grade import grade_answer

QuantumProgram = Any

_CHALLENGE = "qgss_2026"
_LAB = "lab3"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab3_ex5(
    circuit_ising: QuantumCircuit,
    mirrored_circuit: QuantumCircuit,
    boxed: QuantumCircuit,  # ← Keep this parameter (no API change)
    obs_list: list[SparsePauliOp],
    forward_list: list[dict[str, PauliLindbladMap]],
    backward_bound: dict[str, PauliLindbladMap],
) -> None:
    """
    Grade Exercise 5: Investigate the locality of 3 observables for 15 qubits
    """

    # Extract metrics from boxed circuit (avoids annotation serialization issues)
    boxed_num_qubits = int(boxed.num_qubits)
    boxed_num_boxes = sum(1 for inst in boxed if isinstance(inst.operation, BoxOp))

    # Convert PauliLindbladMap to sparse lists
    backward_dict_sparse = {
        key: pl_map.to_sparse_list() for key, pl_map in backward_bound.items()
    }

    forward_list_sparse = [
        {key: pl_map.to_sparse_list() for key, pl_map in d.items()}
        for d in forward_list
    ]

    answer_dict = {
        "circuit_ising": circuit_ising,
        "mirrored_circuit": mirrored_circuit,
        "boxed_num_qubits": boxed_num_qubits,  # ← Send metrics instead
        "boxed_num_boxes": boxed_num_boxes,  # ← Send metrics instead
        "obs_list": obs_list,
        "forward_list": forward_list_sparse,
        "backward_dict": backward_dict_sparse,
    }

    _grade(answer_dict, "ex5")
