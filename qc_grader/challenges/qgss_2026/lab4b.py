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

from typing import Any
import warnings

from typeguard import typechecked

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

    def _dict_to_sampler_options(options_dict):
        sampler_options = SamplerOptions()
        for key, value in options_dict.items():
            if isinstance(value, dict):
                target = getattr(sampler_options, key, None)
                if target is None:
                    setattr(sampler_options, key, value)
                    continue
                for subkey, subvalue in value.items():
                    setattr(target, subkey, subvalue)
            else:
                setattr(sampler_options, key, value)
        return sampler_options

    def _normalize_option_value(value):
        if isinstance(value, dict):
            return {
                key: _normalize_option_value(subvalue)
                for key, subvalue in value.items()
                if subvalue is not None
            }
        if isinstance(value, (list, tuple)):
            return [_normalize_option_value(item) for item in value]
        if hasattr(value, "__dict__"):
            return {
                key: _normalize_option_value(subvalue)
                for key, subvalue in vars(value).items()
                if not key.startswith("_") and subvalue is not None
            }
        return value

    def _extract_defined_sampler_fields(options):
        normalized = _normalize_option_value(options)
        if not isinstance(normalized, dict):
            return normalized
        candidate_keys = (
            "default_shots",
            "dynamical_decoupling",
            "twirling",
        )
        return {
            key: normalized[key]
            for key in candidate_keys
            if key in normalized and normalized[key] not in ({}, [], None)
        }

    if len(options_list) != 4:
        raise ValueError(
            f"options_list should contain 4 entries, got {len(options_list)}"
        )

    if len(job_list) != 4:
        raise ValueError(f"job_list should contain 4 entries, got {len(job_list)}")
    if len(counts_list) != 4:
        raise ValueError(
            f"counts_list should contain 4 entries, got {len(counts_list)}"
        )

    for index, (job, expected_options) in enumerate(
        zip(job_list, options_list), start=1
    ):
        if isinstance(job, RuntimeJobV2):
            job_inputs = getattr(job, "inputs", None)
            if not isinstance(job_inputs, dict):
                raise ValueError(
                    f"job_v{index} should expose runtime inputs when using real hardware"
                )

            job_options = job_inputs.get("options")
            if job_options is None:
                raise ValueError(
                    f"job_v{index} is missing runtime options in its submitted inputs"
                )

            if isinstance(job_options, dict):
                try:
                    job_options = _dict_to_sampler_options(job_options)
                except Exception as exc:
                    raise ValueError(
                        f"job_v{index} runtime options dict could not be converted to SamplerOptions: {exc}"
                    )

            if not isinstance(job_options, SamplerOptions):
                raise ValueError(
                    f"job_v{index} runtime options should be a SamplerOptions object or dict"
                )

            normalized_job_options = _extract_defined_sampler_fields(job_options)
            normalized_expected_options = _extract_defined_sampler_fields(
                expected_options
            )

            # Get expected shots from options
            expected_default_shots = normalized_expected_options.get("default_shots")
            if expected_default_shots is None:
                expected_default_shots = 10000
            # Get job shots - try multiple locations
            job_default_shots = normalized_job_options.get("default_shots")

            # If not found in normalized options, try fallback locations
            if job_default_shots is None:
                # Try direct from inputs
                job_default_shots = job.inputs.get("shots")
                # Use expected as fallback
                if job_default_shots is None:
                    job_default_shots = expected_default_shots
            if job_default_shots != expected_default_shots:
                raise ValueError(
                    f"job_v{index} runtime options do not match the corresponding options_list entry"
                )

            expected_dd_enable = False
            if isinstance(
                normalized_expected_options.get("dynamical_decoupling"), dict
            ):
                expected_dd_enable = bool(
                    normalized_expected_options["dynamical_decoupling"].get(
                        "enable", False
                    )
                )

            job_dd_enable = False
            if isinstance(normalized_job_options.get("dynamical_decoupling"), dict):
                job_dd_enable = bool(
                    normalized_job_options["dynamical_decoupling"].get("enable", False)
                )

            if job_dd_enable != expected_dd_enable:
                raise ValueError(
                    f"job_v{index} runtime options do not match the corresponding options_list entry"
                )

            expected_twirling_gates = False
            if isinstance(normalized_expected_options.get("twirling"), dict):
                expected_twirling_gates = bool(
                    normalized_expected_options["twirling"].get("enable_gates", False)
                )

            job_twirling_gates = False
            if isinstance(normalized_job_options.get("twirling"), dict):
                job_twirling_gates = bool(
                    normalized_job_options["twirling"].get("enable_gates", False)
                )

            if job_twirling_gates != expected_twirling_gates:
                raise ValueError(
                    f"job_v{index} runtime options do not match the corresponding options_list entry"
                )
            expected_twirling_measure = False
            if isinstance(normalized_expected_options.get("twirling"), dict):
                expected_twirling_measure = bool(
                    normalized_expected_options["twirling"].get("enable_measure", False)
                )

            job_twirling_measure = False
            if isinstance(normalized_job_options.get("twirling"), dict):
                job_twirling_measure = bool(
                    normalized_job_options["twirling"].get("enable_measure", False)
                )

            if job_twirling_measure != expected_twirling_measure:
                raise ValueError(
                    f"job_v{index} runtime options do not match the corresponding options_list entry"
                )
        else:
            warnings.warn(
                f"job_v{index} is not a RuntimeJobV2 instance. You appear to be using a simulator, but this exercise is supposed to use a real hardware backend.",
                UserWarning,
            )
    # Go through these values m3_quasis_v3 and m3_quasis_v4 and convert np.floating into float
    m3_quasis_v3 = {k: float(v) if isinstance(v, np.floating) else v for k, v in m3_quasis_v3.items()}
    m3_quasis_v4 = {k: float(v) if isinstance(v, np.floating) else v for k, v in m3_quasis_v4.items()}

    answer_dict = {
        "options_list": options_list,
        "counts_list": counts_list,
        "m3_quasis_v3": m3_quasis_v3,
        "m3_quasis_v4": m3_quasis_v4,
    }
    _grade(answer_dict, "ex2")
