# (C) Copyright IBM 2026

"""
QGSS 2026 Lab 3 - Grading Functions
"""

from dataclasses import asdict
from typing import Any

from typeguard import typechecked

from qiskit import QuantumCircuit
from qiskit.quantum_info import PauliLindbladMap, SparsePauliOp
from qiskit_ibm_runtime.options import EstimatorOptions

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab3"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab3_ex1(options_dict: dict[str, EstimatorOptions]) -> None:
    """
    Grade Exercise 1
    """
    dd = asdict(options_dict["dd"])
    pt = asdict(options_dict["pt"])
    trex = asdict(options_dict["trex"])
    zne = asdict(options_dict["zne"])
    pec = asdict(options_dict["pec"])

    answer_dict = {
        "dd": {
            "enable": dd["dynamical_decoupling"]["enable"],
            "sequence_type": dd["dynamical_decoupling"]["sequence_type"],
        },
        "pt": {
            "enable_gates": pt["twirling"]["enable_gates"],
            "strategy": pt["twirling"]["strategy"],
            "num_randomizations": pt["twirling"]["num_randomizations"],
        },
        "trex": {
            "measure_mitigation": trex["resilience"]["measure_mitigation"],
        },
        "zne": {
            "zne_mitigation": zne["resilience"]["zne_mitigation"],
            "noise_factors": list(zne["resilience"]["zne"]["noise_factors"]),
            "amplifier": zne["resilience"]["zne"]["amplifier"],
        },
        "pec": {
            "pec_mitigation": pec["resilience"]["pec_mitigation"],
            "max_overhead": pec["resilience"]["pec"]["max_overhead"],
        },
    }

    _grade(answer_dict, "ex1")


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
