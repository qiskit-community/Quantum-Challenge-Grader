# (C) Copyright IBM 2026

"""
QGSS 2026 Lab 3 - Grading Functions
"""

from dataclasses import asdict
import math
from typing import Any, TypedDict, cast

from qiskit import QuantumCircuit
from samplomatic.samplex import Samplex
from samplomatic.tensor_interface import TensorInterface
from typeguard import typechecked

from qiskit.circuit import BoxOp
from qiskit.quantum_info import (
    PauliLindbladMap,
    SparsePauliOp,
    Statevector,
    state_fidelity,
)
from qiskit_ibm_runtime.options import EstimatorOptions

from qc_grader.grader.grade import grade_answer

# Only exported in newer runtime versions; fall back to Any otherwise.
try:
    from qiskit_ibm_runtime import QuantumProgram  # ty: ignore[unresolved-import]
except Exception:
    QuantumProgram = Any

_CHALLENGE = "qgss_2026"
_LAB = "lab3"
_PI_8 = math.pi / 8


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


class Lab3Ex1OptionsDict(TypedDict):
    dd: EstimatorOptions
    pt: EstimatorOptions
    trex: EstimatorOptions
    zne: EstimatorOptions
    pec: EstimatorOptions


@typechecked
def grade_lab3_ex1(options_dict: Lab3Ex1OptionsDict) -> None:
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
def grade_lab3_ex2(
    ising_ex2: QuantumCircuit,
    mirror_ex2: QuantumCircuit,
    boxed_circuit_ex2: QuantumCircuit,
) -> None:
    """
    Grade Exercise 2
    """
    op_counts: dict[str, int] = {}
    rx_angles: list[float] = []
    has_barriers = False
    for inst in ising_ex2.data:
        name = inst.operation.name
        op_counts[name] = op_counts.get(name, 0) + 1
        if name == "rx":
            rx_angles.append(float(inst.operation.params[0]))
        elif name == "barrier":
            has_barriers = True

    has_measure = any(inst.operation.name == "measure" for inst in mirror_ex2.data)
    try:
        mirror_no_meas = cast(
            QuantumCircuit, mirror_ex2.remove_final_measurements(inplace=False)
        )
        sv = Statevector(mirror_no_meas)
        zero = Statevector.from_label("0" * mirror_ex2.num_qubits)
        fidelity = float(state_fidelity(sv, zero))
    except Exception:
        fidelity = 0.0

    box_insts = [
        inst for inst in boxed_circuit_ex2 if isinstance(inst.operation, BoxOp)
    ]

    def _has_measure(inst: Any) -> bool:
        return any(sub.operation.name == "measure" for sub in inst.operation.body.data)

    gate_boxes = [b for b in box_insts if not _has_measure(b)]
    twirl = sum(
        1
        for b in gate_boxes
        if any(
            type(annotation).__name__ == "Twirl"
            for annotation in b.operation.annotations
        )
    )
    inject = sum(
        1
        for b in gate_boxes
        if any(
            type(annotation).__name__ == "InjectNoise"
            for annotation in b.operation.annotations
        )
    )

    build_ok = False
    build_err = None
    if box_insts:
        try:
            import importlib

            samplomatic = importlib.import_module("samplomatic")
            samplomatic.build(boxed_circuit_ex2)
            build_ok = True
        except Exception as exc:
            build_err = f"{type(exc).__name__}: {exc}"

    facts = {
        "ising_num_qubits": int(ising_ex2.num_qubits),
        "ising_op_counts": op_counts,
        "ising_rx_all_pi8": bool(
            rx_angles and all(abs(angle - _PI_8) < 1e-9 for angle in rx_angles)
        ),
        "ising_has_barriers": has_barriers,
        "mirror_has_measure": has_measure,
        "mirror_zero_state_fidelity": fidelity,
        "boxed_num_qubits": int(boxed_circuit_ex2.num_qubits),
        "num_boxes": len(box_insts),
        "num_gate_boxes": len(gate_boxes),
        "num_gate_boxes_twirl": twirl,
        "num_gate_boxes_inject": inject,
        "build_ok": build_ok,
        "build_err": build_err,
    }

    _grade(facts, "ex2")


@typechecked
def grade_lab3_ex3(
    template_ex3: QuantumCircuit,
    samplex_ex3: Samplex,
    samplex_args_ex3: TensorInterface,
    program_ex3: QuantumProgram,
    refs_to_noise_models_ex3: dict[str, PauliLindbladMap],
) -> None:
    """
    Grade Exercise 3
    """
    template_params = int(template_ex3.num_parameters)

    specs = samplex_ex3.inputs().get_specs()
    samplex_refs = sorted(str(spec.name) for spec in specs)

    noise_keys = sorted(
        f"pauli_lindblad_maps.{key}" for key in refs_to_noise_models_ex3.keys()
    )

    args_fully_bound = bool(samplex_args_ex3.fully_bound)

    # Guards the case where QuantumProgram fell back to Any (no @typechecked).
    if type(program_ex3).__name__ != "QuantumProgram":
        raise TypeError(
            "`program_ex3` should be a QuantumProgram, "
            f"but got {type(program_ex3).__name__}."
        )

    items = program_ex3.items
    num_items = len(items)
    item = items[0] if num_items > 0 else None
    item_circuit_matches = bool(item is not None and item.circuit is template_ex3)
    item_samplex_matches = bool(item is not None and item.samplex is samplex_ex3)

    facts = {
        "template_params": template_params,
        "samplex_refs": samplex_refs,
        "noise_keys": noise_keys,
        "args_fully_bound": args_fully_bound,
        "num_items": num_items,
        "item_circuit_matches": item_circuit_matches,
        "item_samplex_matches": item_samplex_matches,
    }

    _grade(facts, "ex3")


@typechecked
def grade_lab3_ex4(
    target_observable_ex4: SparsePauliOp,
    target_observable_ex4_isa: SparsePauliOp,
    obs_tilde_ex4: SparsePauliOp,
) -> None:
    """
    Grade Exercise 4
    """
    facts = {
        "target": target_observable_ex4,
        "target_isa": target_observable_ex4_isa,
        "obs_tilde": obs_tilde_ex4,
    }

    _grade(facts, "ex4")


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

    boxed_num_qubits = int(boxed.num_qubits)
    boxed_num_boxes = sum(1 for inst in boxed if isinstance(inst.operation, BoxOp))

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
        "boxed_num_qubits": boxed_num_qubits,
        "boxed_num_boxes": boxed_num_boxes,
        "obs_list": obs_list,
        "forward_list": forward_list_sparse,
        "backward_dict": backward_dict_sparse,
    }

    _grade(answer_dict, "ex5")
