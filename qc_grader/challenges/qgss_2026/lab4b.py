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

from typeguard import typechecked, check_type
from typing import Any, Callable, TypedDict, cast
from dataclasses import asdict
import json

import numpy as np
import networkx as nx
from qiskit.quantum_info import SparsePauliOp
from qiskit import QuantumCircuit
from qiskit_ibm_runtime.options import SamplerOptions, EstimatorOptions
from qiskit_ibm_runtime import RuntimeJobV2
from qiskit_ibm_runtime.fake_provider.local_runtime_job import LocalRuntimeJob

# Redefined UnrollBoxes from qopt_best_practices.transpilation
from qiskit.dagcircuit import DAGCircuit
from qiskit.transpiler import TransformationPass
from qiskit.converters import circuit_to_dag

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab4b"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


def _dict_contains(full_dict: dict[str, Any], subset_dict: dict[str, Any]) -> bool:
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


class UnrollBoxes(TransformationPass):
    """Remove Boxes."""

    def run(self, dag: DAGCircuit):

        for node in dag.topological_op_nodes():
            if node.op.name != "box":
                continue

            box_circuit = node.op.params[0]
            box_dag = circuit_to_dag(box_circuit)
            dag.substitute_node_with_dag(node, box_dag)
        return dag


@typechecked
def grade_lab4b_ex1b(
    partition_hamiltonian: SparsePauliOp, circuit: QuantumCircuit
) -> None:
    """
    Grade Exercise 1b: From graph to Hamiltonian and quantum circuit.
    """
    # Check for any Box, since annotated_qaoa_ansatz (as suggested in the lab) introduces it
    if any(instr.operation.name == "box" for instr in circuit.data):
        circuit = UnrollBoxes()(circuit)
    answer_dict = {"partition_hamiltonian": partition_hamiltonian, "circuit": circuit}
    _grade(answer_dict, "ex1b")


def sanitize_for_json(value: Any) -> Any:
    """
    Recursively sanitize a value to ensure it's JSON serializable.
    Converts non-serializable items to None while preserving dictionary keys.

    Args:
        value: The value to sanitize (can be dict, list, or any other type)

    Returns:
        A JSON-serializable version of the value
    """
    # Handle None explicitly
    if value is None:
        return None

    # Check for Unset types (backward compatibility)
    type_name = type(value).__name__
    if type_name == "UnsetType" or repr(value) == "Unset":
        return None

    # Handle dictionaries recursively
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}

    # Handle lists and tuples recursively
    if isinstance(value, (list, tuple)):
        sanitized = [sanitize_for_json(item) for item in value]
        return sanitized if isinstance(value, list) else tuple(sanitized)

    # Try to serialize the value to check if it's JSON-serializable
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError, OverflowError):
        # If not serializable, return None
        return None


@typechecked
def grade_lab4b_ex2a(
    options_v1: SamplerOptions,
):
    """
    Grade Exercise 2a: Error suppression techniques
    """

    options_dict = sanitize_for_json(asdict(options_v1))
    answer_dict = {
        "options_v1": options_dict,
    }
    _grade(answer_dict, "ex2a")


@typechecked
def grade_lab4b_ex2b(
    options_v2: SamplerOptions,
):
    """
    Grade Exercise 2b: Error suppression techniques
    """

    options_dict = sanitize_for_json(asdict(options_v2))
    answer_dict = {
        "options_v2": options_dict,
    }
    _grade(answer_dict, "ex2b")


@typechecked
def grade_lab4b_ex2c(
    options_v3: SamplerOptions,
    optimized_circuit: QuantumCircuit,
    meas_map_v3: dict[int, int] | list,
    m3_quasis_v3: dict[str, float | np.floating],
    counts_bin_v3: dict[str | int, int],
):
    """
    Grade Exercise 2c: Error suppression techniques
    """

    options_dict = sanitize_for_json(asdict(options_v3))
    m3_quasis_v3 = {k: float(v) for k, v in m3_quasis_v3.items()}
    answer_dict = {
        "options": options_dict,
        "optimized_circuit": optimized_circuit,
        "meas_map": meas_map_v3,
        "m3_quasis": m3_quasis_v3,
        "counts_bin": counts_bin_v3,
    }
    _grade(answer_dict, "ex2c")


@typechecked
def grade_lab4b_ex2d(
    options_v4: SamplerOptions,
    optimized_circuit: QuantumCircuit,
    meas_map_v4: dict[int, int] | list,
    m3_quasis_v4: dict[str, float | np.floating],
    counts_bin_v4: dict[str | int, int],
):
    """
    Grade Exercise 2c: Error suppression techniques
    """

    options_dict = sanitize_for_json(asdict(options_v4))
    m3_quasis_v4 = {k: float(v) for k, v in m3_quasis_v4.items()}
    answer_dict = {
        "options": options_dict,
        "optimized_circuit": optimized_circuit,
        "meas_map": meas_map_v4,
        "m3_quasis": m3_quasis_v4,
        "counts_bin": counts_bin_v4,
    }
    _grade(answer_dict, "ex2d")


@typechecked
def grade_lab4b_ex2(
    options_list: list[SamplerOptions],
    counts_list: list[dict[str, int | float]],
    job_list: list[RuntimeJobV2 | LocalRuntimeJob],
):
    """
    Grade Exercise 2: Error suppression techniques
    """

    # Compare job options with expected options
    for i, (job, expected) in enumerate(zip(job_list, options_list), start=1):
        if isinstance(job, RuntimeJobV2):
            job_opts = job.inputs.get("options", {})
            if not isinstance(job_opts, dict):
                job_opts = asdict(job_opts)
            exp_opts = asdict(expected)

            if not _dict_contains(exp_opts, job_opts):
                raise ValueError(f"job_v{i} options do not match expected options")
        else:
            print(
                f"⚠️ Warning: job_v{i} is not a RuntimeJobV2 instance. "
                "You appear to be using a simulator, but this exercise is supposed to use a real hardware backend."
            )
    # Transform options_list elements into a dictionary with not UnsetType values
    options_dicts = [sanitize_for_json(asdict(options)) for options in options_list]
    answer_dict = {
        "options_list": options_dicts,
        "counts_list": counts_list,
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


@typechecked
def grade_lab4b_ex3c(
    hamiltonian_pce: SparsePauliOp,
    circuit_pce: QuantumCircuit,
) -> None:
    """
    Grade Exercise 3c: Implement Pauli Correlation Encoding: Cost Hamiltonian and QAOA ansatz
    """
    if any(instr.operation.name == "box" for instr in circuit_pce.data):
        circuit_pce = UnrollBoxes()(circuit_pce)
    answer_dict = {
        "hamiltonian_pce": hamiltonian_pce,
        "circuit_pce": circuit_pce,
    }

    _grade(answer_dict, "ex3c")


@typechecked
def grade_lab4b_ex4a(
    options_no_em: EstimatorOptions,
):
    """
    Grade Exercise 4a: Error mitigation techniques
    """

    options_dict = sanitize_for_json(asdict(options_no_em))
    answer_dict = {
        "options_no_em": options_dict,
    }
    _grade(answer_dict, "ex4a")


@typechecked
def grade_lab4b_ex4b(
    options_trex: EstimatorOptions,
):
    """
    Grade Exercise 4b: Error mitigation techniques
    """

    options_dict = sanitize_for_json(asdict(options_trex))
    answer_dict = {
        "options_trex": options_dict,
    }
    _grade(answer_dict, "ex4b")


@typechecked
def grade_lab4b_ex4c(
    options_zne: EstimatorOptions,
):
    """
    Grade Exercise 4c: Error mitigation techniques
    """

    options_dict = sanitize_for_json(asdict(options_zne))
    answer_dict = {
        "options_zne": options_dict,
    }
    _grade(answer_dict, "ex4c")


@typechecked
def grade_lab4b_ex4d(
    options_pec: EstimatorOptions,
):
    """
    Grade Exercise 4d: Error mitigation techniques
    """

    options_dict = sanitize_for_json(asdict(options_pec))
    answer_dict = {
        "options_pec": options_dict,
    }
    _grade(answer_dict, "ex4d")


def _reconstruct_exp_map(job: RuntimeJobV2 | LocalRuntimeJob) -> dict[int, np.floating]:
    result = job.result()
    node_exp_map = {}
    idx = 0
    for pub_result in result:
        evs = getattr(getattr(pub_result, "data", None), "evs", [])
        for ev in evs:
            node_exp_map[idx] = float(ev)
            idx += 1
    return node_exp_map


PartitionResult = TypedDict(
    "PartitionResult",
    {
        "loss": np.floating,
        "par0": list[int] | set[int],
        "par1": list[int] | set[int],
        "par0_size": int,
        "par1_size": int,
        "best_cut": int | np.floating,
        "best_index": int,
        "set0": list[int] | set[int],
        "set1": list[int] | set[int],
        "difference": int | float,
        "exp_map": dict[int, np.floating],
    },
)

EMResults = TypedDict(
    "EMResults",
    {
        "No EM": PartitionResult,
        "TREX": PartitionResult,
        "ZNE": PartitionResult,
        "PEC": PartitionResult,
    },
)


def _find_best_result(
    results_dict: EMResults,
) -> tuple[float, str | None, int | float | None]:
    """
    Find the best result from the results dictionary.

    Returns:
        A tuple of (best_difference, best_method, total_sum)
    """

    best_difference = float("inf")
    best_method: str | None = None
    total_sum: int | float | None = None

    for method, result in results_dict.items():
        # Type checker needs explicit cast to know result is PartitionResult
        partition_result = cast(PartitionResult, result)
        if total_sum is None:
            total_sum = sum(partition_result["set0"]) + sum(partition_result["set1"])

        if partition_result["difference"] < best_difference:
            best_difference = partition_result["difference"]
            best_method = method

    return best_difference, best_method, total_sum


@typechecked
def grade_lab4b_ex4(
    estimator_options_list: list[EstimatorOptions],
    results_dict: EMResults,
    job_list: list[RuntimeJobV2 | LocalRuntimeJob],
):
    """
    Grade Exercise 4: Error suppression mitigation techniques on the Estimator
    """
    required_keys = ["No EM", "TREX", "ZNE", "PEC"]
    # Compare job options with expected options

    for i, (job, expected, key) in enumerate(
        zip(job_list, estimator_options_list, required_keys), start=1
    ):
        reconstructed_exp_map = _reconstruct_exp_map(job)
        stored_exp_map = results_dict.get(key, {}).get("exp_map")
        if stored_exp_map != reconstructed_exp_map:
            raise ValueError(
                f"results_dict['{key}']['exp_map'] does not match the expectation map reconstructed from its estimator job"
            )

        if isinstance(job, RuntimeJobV2):
            job_opts = job.inputs.get("options", {})
            if not isinstance(job_opts, dict):
                job_opts = asdict(job_opts)
            expected = asdict(expected)

            if not _dict_contains(expected, job_opts):
                raise ValueError(f"job_{key} options do not match expected options")
        else:
            print(
                f"⚠️ Warning: job_v{key} is not a RuntimeJobV2 instance. "
                "You appear to be using a simulator, but this exercise is supposed to use a real hardware backend."
            )
    # Transform options_list elements into a dictionary with not UnsetType values
    estimator_options_dicts = [
        sanitize_for_json(asdict(options)) for options in estimator_options_list
    ]
    # Check 4: results has a best value which has a difference smaller than 5% of the total sum
    best_difference, best_method, total_sum = _find_best_result(results_dict)

    answer_dict = {
        "estimator_options_list": estimator_options_dicts,
        "best_difference": best_difference,
        "total_sum": total_sum,
        "best_method": best_method,
    }
    _grade(answer_dict, "ex4")


def _extract_qpu_usage_seconds(job: RuntimeJobV2):
    metrics = getattr(job, "metrics", None)
    if callable(metrics):
        try:
            metrics = metrics()
        except Exception:
            return None

    if not isinstance(metrics, dict):
        return None

    usage = metrics.get("usage", metrics)
    if not isinstance(usage, dict):
        return None

    value = usage.get("quantum_seconds")

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@typechecked
def grade_lab4b_exbonus(
    result_bonus: PartitionResult,
    best_bits: list[int],
    numbers_bonus: list[int] | np.ndarray,
    job_bonus: RuntimeJobV2 | LocalRuntimeJob,
):
    """
    Grade Exercise Bonus: Achieve the best possible result for the partition problem
    """
    if not isinstance(job_bonus, RuntimeJobV2):
        raise ValueError(
            "job_bonus is not a RuntimeJobV2 instance. You appear to be using a simulator, but this exercise is supposed to use a real hardware backend."
        )
    qpu_usage_seconds = _extract_qpu_usage_seconds(job_bonus)

    if qpu_usage_seconds is None or qpu_usage_seconds <= 0:
        raise ValueError("job_bonus should report QPU usage greater than 0 seconds")

    reconstructed_exp_map = _reconstruct_exp_map(job_bonus)
    stored_exp_map = result_bonus.get("exp_map")
    if stored_exp_map != reconstructed_exp_map:
        raise ValueError(
            "result_bonus['exp_map'] does not match the expectation map reconstructed from its estimator job"
        )

    # Convert refined bit assignment back to number sets
    set0 = [
        int(numbers_bonus[i]) for i in range(len(numbers_bonus)) if best_bits[i] == 1
    ]
    set1 = [
        int(numbers_bonus[i]) for i in range(len(numbers_bonus)) if best_bits[i] == 0
    ]
    # Check that these set0 and set1 match the results_bonus
    if set0 != result_bonus["set0"] or set1 != result_bonus["set1"]:
        raise ValueError(
            "best_bits does not reconstruct set0 and set1 from results_bonus"
        )
    reconstructed_exp_map = {int(k): float(v) for k, v in stored_exp_map.items()}

    answer_dict = {
        "set0": result_bonus["set0"],
        "set1": result_bonus["set1"],
        "difference": result_bonus["difference"],
        "qpu_usage_seconds": qpu_usage_seconds,
        "exp_map": reconstructed_exp_map,
        "job_id": job_bonus.job_id(),
    }

    _grade(answer_dict, "exbonus")
