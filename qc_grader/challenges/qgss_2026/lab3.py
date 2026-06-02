# (C) Copyright IBM 2026

"""
QGSS 2026 Lab 3 - Grading Functions
"""

from typing import Any

from typeguard import typechecked

from qiskit import QuantumCircuit
from qiskit.circuit import BoxOp
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime.options import EstimatorOptions

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab3"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


def _serialize_observable(obs: SparsePauliOp) -> dict:
    sparse = [(p, list(q), complex(c).real) for p, q, c in obs.to_sparse_list()]
    return {"num_qubits": obs.num_qubits, "sparse_list": sparse}


def _serialize_plmap(pl_map: Any) -> Any:
    if hasattr(pl_map, "to_sparse_list"):
        return [(p, list(q), float(r)) for p, q, r in pl_map.to_sparse_list()]
    return pl_map


def _box_wraps_measure(inst) -> bool:
    return any(sub.operation.name == "measure" for sub in inst.operation.body.data)


@typechecked
def grade_lab3_ex1(my_options: EstimatorOptions) -> None:
    """Grade Exercise 1."""

    def _get(path: str):
        obj = my_options
        for p in path.split("."):
            obj = getattr(obj, p)
        return obj

    nf = _get("resilience.zne.noise_factors")
    payload = {
        "dd_enable": bool(_get("dynamical_decoupling.enable")),
        "dd_sequence_type": _get("dynamical_decoupling.sequence_type"),
        "pt_enable_gates": bool(_get("twirling.enable_gates")),
        "pt_strategy": _get("twirling.strategy"),
        "pt_num_randomizations": _get("twirling.num_randomizations"),
        "trex_measure_mitigation": bool(_get("resilience.measure_mitigation")),
        "zne_mitigation": bool(_get("resilience.zne_mitigation")),
        "zne_noise_factors": list(nf) if nf is not None else None,
        "zne_amplifier": _get("resilience.zne.amplifier"),
    }
    _grade(payload, "ex1")



@typechecked
def grade_lab3_ex2(
    ising_ex2: QuantumCircuit,
    mirror_ex2: QuantumCircuit,
    boxed_circuit_ex2: QuantumCircuit,
) -> None:
    """Grade Exercise 2."""
    from samplomatic import Twirl, InjectNoise, build

    box_insts = [i for i in boxed_circuit_ex2 if isinstance(i.operation, BoxOp)]
    gate_boxes = [b for b in box_insts if not _box_wraps_measure(b)]
    twirled = sum(
        1 for b in gate_boxes if any(isinstance(a, Twirl) for a in b.operation.annotations)
    )
    injected = sum(
        1
        for b in gate_boxes
        if any(isinstance(a, InjectNoise) for a in b.operation.annotations)
    )
    try:
        build(boxed_circuit_ex2)
        build_ok = True
    except Exception:
        build_ok = False

    payload = {
        "ising_ex2": ising_ex2,
        "mirror_ex2": mirror_ex2,
        "boxed_num_qubits": boxed_circuit_ex2.num_qubits,
        "boxed_gate_box_count": len(gate_boxes),
        "boxed_gate_boxes_twirled": twirled,
        "boxed_gate_boxes_inject_noise": injected,
        "boxed_build_ok": build_ok,
    }
    _grade(payload, "ex2")


@typechecked
def grade_lab3_ex3a(unique_layers: list) -> None:
    """Grade Exercise 3a."""
    has_boxes = len(unique_layers) > 0 and all(
        isinstance(getattr(inst, "operation", None), BoxOp) for inst in unique_layers
    )
    payload = {"num_layers": len(unique_layers), "has_boxes": has_boxes}
    _grade(payload, "ex3a")

@typechecked
def grade_lab3_ex3b(
    second_layer_noise: Any,
    mean_1q_rate: float,
    top_2q_generator: tuple,
) -> None:
    """Grade Exercise 3b."""
    pauli, qubits = top_2q_generator
    payload = {
        "noise_sparse_list": _serialize_plmap(second_layer_noise),
        "mean_1q_rate": float(mean_1q_rate),
        "top_2q_generator": (pauli, list(qubits)),
    }
    _grade(payload, "ex3b")


@typechecked
def grade_lab3_ex4(
    target_observable_ex4: SparsePauliOp,
    target_observable_ex4_isa: SparsePauliOp,
    obs_tilde_ex4: SparsePauliOp,
    top_5_terms_ex4: list,
) -> None:
    """Grade Exercise 4."""
    payload = {
        "target": _serialize_observable(target_observable_ex4),
        "target_isa": _serialize_observable(target_observable_ex4_isa),
        "obs_tilde": _serialize_observable(obs_tilde_ex4),
        "top_5_terms": [(str(p), complex(c).real) for p, c in top_5_terms_ex4],
    }
    _grade(payload, "ex4")


@typechecked
def grade_lab3_ex5(
    circuit_ising_ex5: QuantumCircuit,
    mirrored_circuit_ex5: QuantumCircuit,
    boxed_circuit_ex5: QuantumCircuit,
    obs_list: list,
    forward_bounds_list: list,
    backward_bounds_list: list,
) -> None:
    """Grade Exercise 5."""

    def _serialize_bound(b: Any) -> Any:
        if hasattr(b, "to_sparse_list"):
            return [(p, list(q), float(r)) for p, q, r in b.to_sparse_list()]
        if isinstance(b, dict):
            return {k: _serialize_bound(v) for k, v in b.items()}
        if isinstance(b, (list, tuple)):
            return [_serialize_bound(v) for v in b]
        return b

    box_insts = [i for i in boxed_circuit_ex5 if isinstance(i.operation, BoxOp)]

    payload = {
        "circuit_ising_ex5": circuit_ising_ex5,
        "mirrored_circuit_ex5": mirrored_circuit_ex5,
        "boxed_num_qubits": boxed_circuit_ex5.num_qubits,
        "boxed_box_count": len(box_insts),
        "obs_list": [
            _serialize_observable(o) if isinstance(o, SparsePauliOp) else o
            for o in obs_list
        ],
        "obs_all_distinct": len({id(o) for o in obs_list}) == len(obs_list),
        "forward_list": [_serialize_bound(f) for f in forward_bounds_list],
        "backward_list": [_serialize_bound(b) for b in backward_bounds_list],
    }
    _grade(payload, "ex5")
