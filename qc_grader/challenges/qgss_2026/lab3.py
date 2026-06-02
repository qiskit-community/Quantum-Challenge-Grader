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
QGSS 2026 Lab 3 - Grading Functions
"""

from typing import Any

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab3"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab3_ex1(options: dict) -> None:
    """Grade Exercise 1"""
    _grade(options, "ex1")


@typechecked
def grade_lab3_ex2(circuit_ising: Any, mirrored_circuit: Any, boxed: Any) -> None:
    """Grade Exercise 2"""
    answer_dict = {
        "circuit_ising": circuit_ising,
        "mirrored_circuit": mirrored_circuit,
        "boxed": boxed,
    }
    _grade(answer_dict, "ex2")


@typechecked
def grade_lab3_ex3a(job_id: str) -> None:
    """Grade Exercise 3a"""
    _grade(job_id, "ex3a")


@typechecked
def grade_lab3_ex3b(learned_noise: Any) -> None:
    """Grade Exercise 3b"""
    if hasattr(learned_noise, "to_sparse_list"):
        learned_noise_serialized = learned_noise.to_sparse_list()
    else:
        learned_noise_serialized = learned_noise

    _grade(learned_noise_serialized, "ex3b")


@typechecked
def grade_lab3_ex4(obs_pna: Any) -> None:
    """Grade Exercise 4"""
    if hasattr(obs_pna, "paulis"):
        obs_pna_serialized = {
            "num_qubits": obs_pna.num_qubits,
            "sparse_list": obs_pna.to_sparse_list(),
        }
    else:
        obs_pna_serialized = obs_pna

    _grade(obs_pna_serialized, "ex4")


@typechecked
def grade_lab3_ex5(
    circuit_ising: Any,
    mirrored_circuit: Any,
    boxed: Any,
    obs_list: list,
    forward_list: list,
    backward_bound: dict,
) -> None:
    """Grade Exercise 5:"""
    obs_list_serialized = []
    for obs in obs_list:
        if hasattr(obs, "paulis"):
            obs_list_serialized.append({
                "num_qubits": obs.num_qubits,
                "sparse_list": obs.to_sparse_list(),
            })
        else:
            obs_list_serialized.append(obs)

    backward_bound_serialized = {}
    for key, pl_map in backward_bound.items():
        if hasattr(pl_map, "to_sparse_list"):
            backward_bound_serialized[key] = pl_map.to_sparse_list()
        else:
            backward_bound_serialized[key] = pl_map

    forward_list_serialized = []
    for forward_dict in forward_list:
        serialized_dict = {}
        for key, pl_map in forward_dict.items():
            if hasattr(pl_map, "to_sparse_list"):
                serialized_dict[key] = pl_map.to_sparse_list()
            else:
                serialized_dict[key] = pl_map
        forward_list_serialized.append(serialized_dict)

    answer_dict = {
        "circuit_ising": circuit_ising,
        "mirrored_circuit": mirrored_circuit,
        "boxed": boxed,
        "obs_list": obs_list_serialized,
        "forward_list": forward_list_serialized,
        "backward_bound": backward_bound_serialized,
    }

    _grade(answer_dict, "ex5")
