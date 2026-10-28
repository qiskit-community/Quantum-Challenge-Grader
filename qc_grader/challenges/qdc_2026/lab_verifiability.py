"""QDC 2026, "Verifiable quantum advantage" (lab ``lab_verifiability``): the grading functions.

One ``grade_lab_verifiability_exN`` function per step of the notebook
``challenge_verifiability_2026.ipynb`` (``exN`` = Step N). Each function packs the notebook
variables it receives into one JSON-serialisable answer and sends it with ``grade_answer``;
the server validator of the same exercise grades it.

- The backend, the qiskit-paulice ``NoiseModel`` and ``CheckedCircuit`` objects and the
  ``QuantumProgram`` cannot cross the JSON boundary, and the server has neither paulice nor
  samplomatic. They are read here and reduced to plain data: calibration records from
  ``backend.target`` (Steps 1 and 2), the fields of the noise model (Step 2), per-circuit
  summaries of the checked circuits (Steps 3 and 7) and a description of one program item
  (Step 6). This module imports neither package: the objects are read by their attributes.
- The hardware numbers (post-selection rates, fidelities, bounds) are self-reported: the
  server cannot reach IBM Quantum and checks them for internal consistency only.
- The thresholds of the notebook-side prototype (``threshold``, ``tolerance``, ...) are
  server constants and are not arguments here.

Ids (proposed until the maintainer confirms them): challenge ``qdc_2026``, lab
``lab_verifiability``, exercises ``ex1`` ... ``ex10``.
"""

# The client contract raises ValueError, with the fix first, for every bad input, type
# problems included (spec section 4.2), so ruff's TypeError preference does not apply.
# ruff: noqa: TRY004

import itertools
import math
from collections.abc import Sequence
from typing import Any, SupportsFloat, SupportsInt

import numpy as np
from qiskit import QuantumCircuit
from qiskit.providers import BackendV2
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"  # the id the maintainer assigns; identical on the server
_LAB = "lab_verifiability"  # the lab id; identical on the server


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


# The interface of a CheckedCircuit that Step 3 checks (identical on the server).
_CC_ATTRS = (
    "circuit",
    "target_qubits",
    "check_qubits",
    "check_support",
    "cost",
    "cost_metric",
)
_CC_METHODS = ("get_postselection_method", "dope", "estimate_fault_rates")
TWO_Q_CANDIDATES = ("cz", "ecr", "cx")  # the native 2Q gate is the first one present
MAX_QUBIT_LIST = 1_000  # longest qubit list the server accepts
MAX_SERIES = 1_000  # longest rate curve the server accepts

QubitList = Sequence[SupportsInt] | np.ndarray
FloatList = Sequence[SupportsFloat] | np.ndarray


# ------------------------------------------------------------------------------------------
# Conversions: every value leaves as a plain int, float, str, list or dict
# ------------------------------------------------------------------------------------------
def _kind(x: object) -> str:
    """A short description of a value for a message."""
    if isinstance(x, np.ndarray):
        return f"an array of shape {x.shape}"
    return type(x).__name__


def _int(x: object, name: str) -> int:
    """``x`` as an int when it is a whole number (Python or NumPy), else ValueError."""
    if isinstance(x, (bool, np.bool_)):
        raise ValueError(f"Pass a whole number for {name}, not a bool.")
    if isinstance(x, np.ndarray) and x.size == 1:
        x = x.item()  # ty: ignore[no-matching-overload]
    if isinstance(x, (int, np.integer)):
        return int(x)
    if (
        isinstance(x, (float, np.floating))
        and math.isfinite(x)
        and float(x).is_integer()
    ):
        return int(x)
    raise ValueError(f"Pass a whole number for {name}; got {x!r}.")


def _real(x: object, name: str) -> float:
    """``x`` as a float when it is one real number (NaN allowed), else ValueError."""
    if isinstance(x, (bool, np.bool_)):
        raise ValueError(f"Pass a number for {name}, not a bool.")
    if isinstance(x, np.ndarray) and x.size == 1:
        x = x.item()  # ty: ignore[no-matching-overload]
    if isinstance(x, (int, float, np.integer, np.floating)):
        return float(x)
    raise ValueError(f"Pass a number for {name}; got {_kind(x)}.")


def _qubits(x: object, name: str) -> list[int]:
    """A list of qubit indices (Python or NumPy ints) as a list of ints."""
    if isinstance(x, (str, bytes, set, frozenset, dict)):
        raise ValueError(
            f"Pass {name} as a list of qubit indices in order; got {_kind(x)}."
        )
    values = np.asarray(x).ravel().tolist() if isinstance(x, np.ndarray) else list(x)  # ty: ignore[invalid-argument-type] - checked above
    if len(values) > MAX_QUBIT_LIST:
        raise ValueError(
            f"Pass the {name} of this challenge: it has {len(values)} entries, at most "
            f"{MAX_QUBIT_LIST} are accepted."
        )
    return [_int(q, f"each entry of {name}") for q in values]


def _floats(x: object, name: str) -> list[float]:
    """A flat sequence of numbers (NaN allowed) as a list of floats."""
    if isinstance(x, (str, bytes, set, frozenset, dict)):
        raise ValueError(f"Pass {name} as a list or array of numbers; got {_kind(x)}.")
    try:
        arr = np.asarray(x, dtype=float)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"Pass {name} as a list or array of numbers; it holds something else ({err})."
        ) from err
    if arr.ndim != 1:
        raise ValueError(
            f"Pass {name} as a 1-D list or array (one value per entry); got {_kind(arr)}."
        )
    if arr.size > MAX_SERIES:
        raise ValueError(
            f"Pass the {name} of this challenge: it has {arr.size} entries, at most "
            f"{MAX_SERIES} are accepted."
        )
    return [float(v) for v in arr]


def _grid(
    x: object, name: str, allow_1d: bool = False
) -> list[list[float]] | list[float]:
    """A 2-D array of numbers (NaN allowed) as a list of rows of floats."""
    try:
        arr = np.asarray(x, dtype=float)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"Pass {name} as the 2-D array the notebook builds, shape (3, "
            f"len(reduced_checks)); its rows are ragged or hold something else ({err})."
        ) from err
    if arr.ndim == 1 and allow_1d:
        return _floats(arr, name)
    if arr.ndim != 2:
        raise ValueError(
            f"Pass {name} as the 2-D array the notebook builds, shape (3, "
            f"len(reduced_checks)); got {_kind(arr)}."
        )
    if arr.size > 3 * MAX_SERIES:
        raise ValueError(
            f"Pass the {name} of this challenge: it has {arr.size} entries, at most "
            f"{3 * MAX_SERIES} are accepted."
        )
    return [[float(v) for v in row] for row in arr]


def _error(props: object) -> float | None:
    """The ``error`` of an InstructionProperties, None when absent or uncalibrated."""
    err = getattr(props, "error", None)
    return None if err is None else float(err)


# ------------------------------------------------------------------------------------------
# Calibration records (Steps 1 and 2), read from backend.target
# ------------------------------------------------------------------------------------------
def _native_two_qubit_gate(backend: BackendV2) -> str | None:
    names = set(backend.target.operation_names)
    return next((g for g in TWO_Q_CANDIDATES if g in names), None)


def _edge_error(backend: BackendV2, two_q: str | None, a: int, b: int) -> float | None:
    """2Q gate error on the coupler (a, b) in either orientation, None if uncalibrated."""
    if two_q is None:
        return None
    props = backend.target[two_q]
    for key in ((a, b), (b, a)):
        if key in props:
            return _error(props[key])
    return None


def _readout_error(backend: BackendV2, q: int) -> float | None:
    if "measure" not in backend.target.operation_names:
        return None
    return _error(backend.target["measure"].get((q,)))


def _qubit_records(backend: BackendV2, qubits: Sequence[int]) -> list[dict[str, Any]]:
    return [{"qubit": q, "readout": _readout_error(backend, q)} for q in qubits]


def _check_qubits_on(backend: BackendV2, qubits: Sequence[int], name: str) -> None:
    bad = [q for q in qubits if not 0 <= q < backend.num_qubits]
    if bad:
        raise ValueError(
            f"Use qubits of {backend.name} (0 to {backend.num_qubits - 1}) in {name}; "
            f"{bad[:5]} are not."
        )


def _layout_edge_records(
    backend: BackendV2, layout: Sequence[int]
) -> list[dict[str, Any]]:
    """The couplers inside ``layout``, once each, with the mean error over every 2Q
    instruction calibrated on them; couplers without any error are skipped. This is the
    averaging of ``NoiseModel.from_backend`` (qiskit-paulice), redone with qiskit."""
    inside = set(layout)
    two_q_names = [op.name for op in backend.target.operations if op.num_qubits == 2]
    seen: set[tuple[int, int]] = set()
    records = []
    for a, b in backend.coupling_map.get_edges():
        key = (min(a, b), max(a, b))
        if a not in inside or b not in inside or key in seen:
            continue
        seen.add(key)
        errors = []
        for name in two_q_names:
            err = _error(backend.target[name].get((a, b)))
            if err is not None:
                errors.append(err)
        if errors:
            records.append({"a": key[0], "b": key[1], "error": float(np.mean(errors))})
    return records


# ------------------------------------------------------------------------------------------
# Step 1
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_verifiability_ex1(
    backend: BackendV2,
    layout: QubitList,
    target_qubits: QubitList,
    ancilla_qubits: QubitList,
) -> None:
    """Grade Step 1, the layout:
    ``grade_lab_verifiability_ex1(backend, layout, target_qubits, ancilla_qubits)``.

    Args:
        backend: the backend you chose the layout on (``backend``).
        layout: the physical qubits of the payload, in virtual-qubit order (``layout``).
        target_qubits: the payload qubits that get a check (``target_qubits``).
        ancilla_qubits: the check ancilla of each target qubit, in the same order
            (``ancilla_qubits``).

    The 2Q and readout errors of the qubits and couplers you use are read here from
    ``backend.target`` and sent with the layout; the server checks the connectivity
    against its own copy of the device's coupling map.
    """
    layout_ = _qubits(layout, "layout")
    targets = _qubits(target_qubits, "target_qubits")
    ancillas = _qubits(ancilla_qubits, "ancilla_qubits")
    # Unequal target and ancilla counts are graded (the server explains the pairing).
    for name, qubits in (
        ("layout", layout_),
        ("target_qubits", targets),
        ("ancilla_qubits", ancillas),
    ):
        _check_qubits_on(backend, qubits, name)
    two_q = _native_two_qubit_gate(backend)
    required = list(itertools.pairwise(layout_)) + list(zip(targets, ancillas))
    answer = {
        "device": str(backend.name),
        "layout": layout_,
        "target_qubits": targets,
        "ancilla_qubits": ancillas,
        "edges": [
            {"a": a, "b": b, "error": _edge_error(backend, two_q, a, b)}
            for a, b in required
        ],
        "qubits": _qubit_records(backend, sorted(set(layout_) | set(ancillas))),
    }
    _grade(answer, "ex1")


# ------------------------------------------------------------------------------------------
# Step 2
# ------------------------------------------------------------------------------------------
def _noise_model_record(noise_model: object) -> dict[str, Any]:
    """The fields of a qiskit-paulice NoiseModel: the kind of ``gate_noise`` (a float for
    a uniform model, a dict for a gate-wise one), its value when uniform, and the readout
    and idling noise."""
    fields = ("gate_noise", "readout_noise", "idling_noise")
    if not all(hasattr(noise_model, f) for f in fields):
        raise ValueError(
            "Pass the qiskit-paulice NoiseModel of Step 2 (noise_model = "
            "NoiseModel.from_backend(backend, layout, uniform_gate_noise=True)); got "
            f"{_kind(noise_model)}."
        )
    gate = getattr(noise_model, "gate_noise", None)
    record: dict[str, Any] = {"kind": "missing", "gate_noise": None}
    if isinstance(gate, float):
        record.update(kind="uniform", gate_noise=float(gate))
    elif gate is not None:
        record["kind"] = "gatewise"
    for f in ("readout_noise", "idling_noise"):
        value = getattr(noise_model, f)
        record[f] = None if value is None else _real(value, f"noise_model.{f}")
    return record


@typechecked
def grade_lab_verifiability_ex2(
    isa_circuit: QuantumCircuit,
    noise_model: object,  # a qiskit-paulice NoiseModel, read by its attributes
    backend: BackendV2,
    layout: QubitList | None = None,
) -> None:
    """Grade Step 2, the transpiled circuit and the noise model:
    ``grade_lab_verifiability_ex2(isa_circuit, noise_model, backend)``.

    Args:
        isa_circuit: the target circuit transpiled onto ``layout`` (``isa_circuit``).
        noise_model: the qiskit-paulice ``NoiseModel`` you built (``noise_model``).
        backend: the backend of Step 1 (``backend``).
        layout: the layout of Step 1. Leave it out to use
            ``isa_circuit.layout.final_index_layout()``.

    The calibration of the couplers and qubits inside the layout is read here from
    ``backend.target``, so the server can rebuild the reference noise model.
    """
    if layout is None:
        if isa_circuit.layout is None:
            raise ValueError(
                "Pass layout=layout, or the circuit returned by the pass manager: "
                "isa_circuit has no layout to read it from."
            )
        layout_ = [int(q) for q in isa_circuit.layout.final_index_layout()]
    else:
        layout_ = _qubits(layout, "layout")
    _check_qubits_on(backend, layout_, "layout")
    answer = {
        "device": str(backend.name),
        "isa_circuit": isa_circuit,
        "layout": layout_,
        "noise_model": _noise_model_record(noise_model),
        "edges": _layout_edge_records(backend, layout_),
        "qubits": _qubit_records(backend, layout_),
    }
    _grade(answer, "ex2")


# ------------------------------------------------------------------------------------------
# Step 3
# ------------------------------------------------------------------------------------------
def _sequence(x: object, name: str) -> list[Any]:
    if isinstance(x, (str, bytes, dict, QuantumCircuit)) or not isinstance(x, Sequence):
        raise ValueError(
            f"Pass {name} as the list the notebook builds; got {_kind(x)}."
        )
    return list(x)


def _checked_entry(cc: object) -> dict[str, Any]:
    """What Step 3 reads of one CheckedCircuit: the interface it lacks, its check
    qubits and its cost."""
    missing = [a for a in _CC_ATTRS if not hasattr(cc, a)]
    missing += [m for m in _CC_METHODS if not callable(getattr(cc, m, None))]
    check_qubits = getattr(cc, "check_qubits", None)
    try:
        qubits = None if check_qubits is None else [int(q) for q in check_qubits]
    except (TypeError, ValueError):
        qubits = None
    cost = getattr(cc, "cost", None)
    try:
        cost_value = None if cost is None else float(cost)
    except (TypeError, ValueError):
        cost_value = float("nan")  # the prototype reads an unusable cost as NaN
    return {"missing": missing, "check_qubits": qubits, "cost": cost_value}


@typechecked
def grade_lab_verifiability_ex3(
    checked_circuits: Sequence[object],  # qiskit-paulice CheckedCircuit objects
    ancilla_qubits: QubitList,
) -> None:
    """Grade Step 3, the checked circuits:
    ``grade_lab_verifiability_ex3(checked_circuits, ancilla_qubits)``.

    Args:
        checked_circuits: the list returned by ``add_pauli_checks``, from 0 checks up to
            one per ancilla (``checked_circuits``).
        ancilla_qubits: the ancillas of Step 1 (``ancilla_qubits``).

    The circuits stay here (they are about 10 MB); the server receives, per entry, the
    CheckedCircuit interface it lacks, its check qubits and its cost.
    """
    items = _sequence(checked_circuits, "checked_circuits")
    answer = {
        "ancilla_qubits": _qubits(ancilla_qubits, "ancilla_qubits"),
        "cost_metric": str(getattr(items[0], "cost_metric", "cost"))
        if items
        else "cost",
        "entries": [_checked_entry(cc) for cc in items],
    }
    _grade(answer, "ex3")


# ------------------------------------------------------------------------------------------
# Steps 4 and 5
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_verifiability_ex4(
    selected_ancilla_qubits: QubitList,
    selected_postselection_rate_aer: FloatList,
    ancilla_qubits: QubitList,
    postselection_rate_aer: FloatList,
) -> None:
    """Grade Step 4, the selected checks:
    ``grade_lab_verifiability_ex4(selected_ancilla_qubits, selected_postselection_rate_aer,
    ancilla_qubits, postselection_rate_aer)``.

    Args:
        selected_ancilla_qubits: the ancillas you kept (``selected_ancilla_qubits``).
        selected_postselection_rate_aer: the simulated post-selection rate of the selected
            checked circuits (``selected_postselection_rate_aer``).
        ancilla_qubits: all ancillas of Step 1 (``ancilla_qubits``).
        postselection_rate_aer: the simulated rate of all checked circuits of Step 3
            (``postselection_rate_aer``).
    """
    answer = {
        "selected_ancilla_qubits": _qubits(
            selected_ancilla_qubits, "selected_ancilla_qubits"
        ),
        "selected_rates": _floats(
            selected_postselection_rate_aer, "selected_postselection_rate_aer"
        ),
        "ancilla_qubits": _qubits(ancilla_qubits, "ancilla_qubits"),
        "rates": _floats(postselection_rate_aer, "postselection_rate_aer"),
    }
    _grade(answer, "ex4")


@typechecked
def grade_lab_verifiability_ex5(selected_postselection_rate_qpu: FloatList) -> None:
    """Grade Step 5, the post-selection rate on hardware:
    ``grade_lab_verifiability_ex5(selected_postselection_rate_qpu)``.

    Args:
        selected_postselection_rate_qpu: the share of shots kept on the QPU, one value per
            selected checked circuit (``selected_postselection_rate_qpu``). Self-reported.
    """
    rates = _floats(selected_postselection_rate_qpu, "selected_postselection_rate_qpu")
    _grade({"rates": rates}, "ex5")


# ------------------------------------------------------------------------------------------
# Step 6
# ------------------------------------------------------------------------------------------
def _meas_mapping(
    template: QuantumCircuit, name: str = "meas"
) -> dict[int, int] | None:
    """``{position in the register: physical qubit}`` for the register ``name``, read off
    the clbit each measure writes (the non-Markovian passes reorder the measure
    instructions but keep which clbit takes which qubit). None without the register."""
    creg = next((c for c in template.cregs if c.name == name), None)
    if creg is None:
        return None
    pos = {template.find_bit(cb).index: k for k, cb in enumerate(creg)}
    out: dict[int, int] = {}
    for inst in template.data:
        if inst.operation.name != "measure" or not inst.clbits:
            continue
        g = template.find_bit(inst.clbits[0]).index
        if g in pos:
            out[pos[g]] = template.find_bit(inst.qubits[0]).index
    return out


def _template_summary(template: QuantumCircuit) -> dict[str, Any]:
    """What the server reads of the boxed template: its classical registers, which qubit
    each bit of 'meas' measures, and its operation counts."""
    mapping = _meas_mapping(template)
    return {
        "cregs": [{"name": str(c.name), "size": int(c.size)} for c in template.cregs],
        "meas_mapping": None
        if mapping is None
        else [{"bit": int(k), "qubit": int(q)} for k, q in sorted(mapping.items())],
        "count_ops": {str(k): int(v) for k, v in template.count_ops().items()},
    }


def _program_info(
    program: object,
    circuit: QuantumCircuit,
    layout: list[int],
    stabilizers: object,
    checked_circuits: list[Any],
) -> dict[str, Any]:
    """The last item of the QuantumProgram (the one with the most checks), as plain data:
    ``collect_program_info`` of the notebook's utils, with the template summarised."""
    fix = (
        "Pass the QuantumProgram you ran in Step 6 (program), built with "
        "program.append_samplex_item(template, samplex=..., samplex_arguments=..., "
        "shape=...)"
    )
    items = getattr(program, "items", None)
    if not isinstance(items, Sequence) or not items:  # a dict has an .items method
        raise ValueError(f"{fix}; got {_kind(program)} without program items.")
    item = items[-1]
    template = getattr(item, "circuit", None)
    if not isinstance(template, QuantumCircuit):
        raise ValueError(f"{fix}; its last item carries no template circuit.")
    try:
        specs = list(item.samplex.inputs().get_specs())
        arguments = dict(item.samplex_arguments)
        shape = [int(v) for v in item.shape]
        shots = int(program.shots)  # ty: ignore[unresolved-attribute] - duck-typed
    except (AttributeError, TypeError, ValueError) as err:
        raise ValueError(f"{fix}; reading its last item failed ({err}).") from err
    if len(specs) != 1:
        raise ValueError(
            f"{fix}; the samplex of its last item has {len(specs)} inputs, expected one "
            "(the measurement bases)."
        )
    if not checked_circuits:
        raise ValueError(
            "Pass the checked circuits the program items were built from "
            "(reduced_checked_circuits); the list is empty."
        )
    cc = checked_circuits[-1]
    check_qubits = getattr(cc, "check_qubits", None)
    if check_qubits is None:
        raise ValueError(
            "Pass the CheckedCircuit objects the program items were built from "
            "(reduced_checked_circuits); the last one has no check_qubits."
        )
    if isinstance(stabilizers, str):
        raise ValueError(
            "Pass the stabilizers as the PauliList (or list of Pauli labels) of Step 6, "
            "not one string."
        )
    try:
        labels = [str(g) for g in stabilizers]  # ty: ignore[not-iterable] - duck-typed
    except TypeError as err:
        raise ValueError(
            "Pass the stabilizers as the PauliList (or list of Pauli labels) of Step 6; "
            f"got {_kind(stabilizers)}."
        ) from err
    key = next(iter(arguments)) if len(arguments) == 1 else None
    basis_array = None
    if key is not None:
        basis_array = np.asarray(arguments[key])
        if basis_array.dtype.kind not in "biu":
            raise ValueError(
                f"{fix}; the array in samplex_arguments has dtype {basis_array.dtype}, "
                "expected the integer basis codes of stabilizer_bases."
            )
    return {
        "template": _template_summary(template),
        "circuit": circuit,
        "layout": layout,
        "check_qubits": [int(q) for q in check_qubits],
        "stabilizers": labels,
        "basis_array": basis_array,
        "input_name": str(specs[0].name),
        "argument_key": None if key is None else str(key),
        "shape": shape,
        "shots": shots,
    }


@typechecked
def grade_lab_verifiability_ex6(
    qpu_fid: np.ndarray | Sequence[Sequence[SupportsFloat]],
    qpu_err: np.ndarray | Sequence[Sequence[SupportsFloat]],
    qpu_keep: np.ndarray | Sequence[Sequence[SupportsFloat]],
    reduced_checks: QubitList,
    qpu_shots_per_basis: FloatList | None,
    program: object,  # the qiskit-ibm-runtime QuantumProgram, read by its attributes
    circuit: QuantumCircuit,
    layout: QubitList,
    stabilizers: object,  # a PauliList or a list of Pauli labels
    reduced_checked_circuits: Sequence[object],
) -> None:
    """Grade Step 6, direct fidelity estimation on hardware:
    ``grade_lab_verifiability_ex6(qpu_fid, qpu_err, qpu_keep, reduced_checks,
    qpu_shots_per_basis, program, circuit, layout, stabilizers, reduced_checked_circuits)``.

    Args:
        qpu_fid: the fidelities, shape (3, len(reduced_checks)), one row per stage
            (``qpu_fid``). NaN for a stage you did not run.
        qpu_err: their uncertainties, same shape (``qpu_err``).
        qpu_keep: the share of shots kept, same shape (``qpu_keep``).
        reduced_checks: the check counts run on hardware (``reduced_checks``).
        qpu_shots_per_basis: the kept shots in the thinnest basis, per check count
            (``qpu_shots_per_basis``), or None.
        program: the ``QuantumProgram`` you ran (``program``).
        circuit: the target circuit of Step 1, untranspiled (``circuit``).
        layout: the layout of Step 1 (``layout``).
        stabilizers: the sampled stabilizers, in the order of the program (``stabilizers``).
        reduced_checked_circuits: the checked circuits the program items were built from
            (``reduced_checked_circuits``).

    The program stays here: its last item (the most checks) is described by its template's
    registers, measurement mapping and operation counts, its basis array, shape and shots.
    The server verifies that the stabilizers stabilize ``circuit`` and re-derives the
    bases; the fidelities are self-reported.
    """
    layout_ = _qubits(layout, "layout")
    answer = {
        "fid": _grid(qpu_fid, "qpu_fid"),
        "err": _grid(qpu_err, "qpu_err"),
        "keep": _grid(qpu_keep, "qpu_keep"),
        "reduced_checks": _qubits(reduced_checks, "reduced_checks"),
        "shots_per_basis": None
        if qpu_shots_per_basis is None
        else _floats(qpu_shots_per_basis, "qpu_shots_per_basis"),
        "program": _program_info(
            program,
            circuit,
            layout_,
            stabilizers,
            _sequence(reduced_checked_circuits, "reduced_checked_circuits"),
        ),
    }
    _grade(answer, "ex6")


# ------------------------------------------------------------------------------------------
# Step 7
# ------------------------------------------------------------------------------------------
def _two_q_counts(circuit: QuantumCircuit) -> dict[str, int]:
    ops = circuit.count_ops()
    return {g: int(ops.get(g, 0)) for g in TWO_Q_CANDIDATES}


def _circuit_of(cc: object) -> QuantumCircuit | None:
    qc = getattr(cc, "circuit", None)
    return qc if isinstance(qc, QuantumCircuit) else None


@typechecked
def grade_lab_verifiability_ex7(
    doped_checked_circuits: Sequence[object],  # CheckedCircuit objects
    selected_checked_circuits: Sequence[object],
) -> None:
    """Grade Step 7, the doped circuits:
    ``grade_lab_verifiability_ex7(doped_checked_circuits, selected_checked_circuits)``.

    Args:
        doped_checked_circuits: the doped CheckedCircuit objects
            (``doped_checked_circuits``).
        selected_checked_circuits: the Clifford ones they were doped from, in the same
            order (``selected_checked_circuits``).

    The circuits stay here; per pair the server receives whether the doped entry is still
    a CheckedCircuit, and the rz and 2Q gate counts of both circuits.
    """
    doped = _sequence(doped_checked_circuits, "doped_checked_circuits")
    undoped = _sequence(selected_checked_circuits, "selected_checked_circuits")
    pairs = []
    for d, u in zip(doped, undoped):
        dc, uc = _circuit_of(d), _circuit_of(u)
        pairs.append(
            {
                "doped_wrapped": hasattr(d, "circuit") and hasattr(d, "cost"),
                "doped_rz": None if dc is None else int(dc.count_ops().get("rz", 0)),
                "undoped_rz": None if uc is None else int(uc.count_ops().get("rz", 0)),
                "doped_2q": None if dc is None else _two_q_counts(dc),
                "undoped_2q": None if uc is None else _two_q_counts(uc),
            }
        )
    answer = {"num_doped": len(doped), "num_undoped": len(undoped), "pairs": pairs}
    _grade(answer, "ex7")


# ------------------------------------------------------------------------------------------
# Steps 8 and 9
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_verifiability_ex8(
    doped_postselection_rate_qpu: FloatList,
    selected_postselection_rate_qpu: FloatList,
) -> None:
    """Grade Step 8, the doped post-selection rate:
    ``grade_lab_verifiability_ex8(doped_postselection_rate_qpu,
    selected_postselection_rate_qpu)``.

    Args:
        doped_postselection_rate_qpu: the share of shots kept on the QPU for the doped
            circuits (``doped_postselection_rate_qpu``). Self-reported.
        selected_postselection_rate_qpu: the same for the Clifford circuits of Step 5
            (``selected_postselection_rate_qpu``).
    """
    answer = {
        "doped_rates": _floats(
            doped_postselection_rate_qpu, "doped_postselection_rate_qpu"
        ),
        "clifford_rates": _floats(
            selected_postselection_rate_qpu, "selected_postselection_rate_qpu"
        ),
    }
    _grade(answer, "ex8")


@typechecked
def grade_lab_verifiability_ex9(
    harmless_rates: FloatList,
    F_lower_qpu: FloatList,
    qpu_fid: np.ndarray | Sequence[Sequence[SupportsFloat]] | FloatList,
    reduced_checks: QubitList | None = None,
) -> None:
    """Grade Step 9, the fidelity bound:
    ``grade_lab_verifiability_ex9(harmless_rates, F_lower_qpu, qpu_fid, reduced_checks)``.

    Args:
        harmless_rates: Pr(H | A) per selected checked circuit, from
            ``estimate_fault_rates`` (``harmless_rates``).
        F_lower_qpu: your bound per check count run on hardware (``F_lower_qpu``).
        qpu_fid: the fidelities of Step 6 (``qpu_fid``, shape (3, n)), or the row of the
            check-post-selected stage.
        reduced_checks: the check counts run on hardware (``reduced_checks``).
    """
    answer = {
        "harmless_rates": _floats(harmless_rates, "harmless_rates"),
        "F_lower": _floats(F_lower_qpu, "F_lower_qpu"),
        "fid": _grid(qpu_fid, "qpu_fid", allow_1d=True),
        "reduced_checks": None
        if reduced_checks is None
        else _qubits(reduced_checks, "reduced_checks"),
    }
    _grade(answer, "ex9")


# ------------------------------------------------------------------------------------------
# Step 10
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_verifiability_ex10(
    clifford_backbone: QuantumCircuit,
    num_checks: SupportsInt,
    F_1: SupportsFloat,
    F_1_err: SupportsFloat,
    harmless_rate: SupportsFloat,
    F_lower: SupportsFloat,
    num_stabilizers: SupportsInt,
    shots_per_basis: SupportsInt,
    postselection_rate: SupportsFloat | None = None,
) -> None:
    """Grade Step 10, the advanced instance:
    ``grade_lab_verifiability_ex10(clifford_backbone, num_checks, F_1, F_1_err,
    harmless_rate, F_lower, num_stabilizers, shots_per_basis)``.

    Args:
        clifford_backbone: the QASM circuit with its rz(pi/4) gates removed, untranspiled
            (``clifford_backbone``).
        num_checks: how many checks you kept (``num_checks``).
        F_1: the post-selected Clifford fidelity from the QPU (``F_1``).
        F_1_err: its uncertainty (``F_1_err``).
        harmless_rate: Pr(H | A), from ``estimate_fault_rates`` (``harmless_rate``).
        F_lower: your bound, F_1 - Pr(H | A) (``F_lower``).
        num_stabilizers: the stabilizers sampled for the DFE (``num_stabilizers``).
        shots_per_basis: the kept shots in the thinnest measurement basis
            (``shots_per_basis``).
        postselection_rate: optionally, the share of shots kept.

    The server compares the backbone to a fingerprint of the tracker instance; the numbers
    are self-reported.
    """
    answer: dict[str, Any] = {
        "clifford_backbone": clifford_backbone,
        "num_checks": _int(num_checks, "num_checks"),
        "F_1": _real(F_1, "F_1"),
        "F_1_err": _real(F_1_err, "F_1_err"),
        "harmless_rate": _real(harmless_rate, "harmless_rate"),
        "F_lower": _real(F_lower, "F_lower"),
        "num_stabilizers": _int(num_stabilizers, "num_stabilizers"),
        "shots_per_basis": _int(shots_per_basis, "shots_per_basis"),
    }
    if postselection_rate is not None:
        answer["postselection_rate"] = _real(postselection_rate, "postselection_rate")
    _grade(answer, "ex10")
