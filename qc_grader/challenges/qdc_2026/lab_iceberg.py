"""QDC 2026 ``lab_iceberg`` grading functions: Ising with Iceberg.

One ``grade_lab_iceberg_<ex>`` per exercise. Each packs the notebook variables it receives into
one JSON-serialisable answer and sends it with ``grade_answer``.

Thirteen exercises take functions the participant wrote. The platform cannot accept a callable,
so they are evaluated **here, on the participant's machine**, at the fixed probes below, and only
the results travel: circuits as op-signatures, ORP functions as their arrays, hardware jobs as
the numbers read off them. Those hardware numbers are self-reported; the server cannot reach IBM
Quantum, and the organizers may audit the job ids afterwards.

The probe constants are duplicated in the server module, which uses its own copy and never
trusts a probe echoed back in an answer.

Challenge ``qdc_2026``, lab ``lab_iceberg``. The lattice and placement code the probes need is
vendored in ``_iceberg/`` - see that package's docstring - so grading works from the installed
package with no challenge folder on ``sys.path``.
"""

# The client contract raises ValueError, with the fix first, for every bad input, type problems
# included (AGENTS.md section 4.2), so ruff's TypeError preference does not apply.
# ruff: noqa: TRY004
#
# BLE001 likewise: every `except Exception` here immediately re-raises as a ValueError naming
# the fix (`raise ... from None`). Narrowing the catch would let an unanticipated exception type
# from a participant's object reach the notebook as a traceback instead of a diagnosis, which is
# the opposite of the contract.
# ruff: noqa: BLE001

from __future__ import annotations

import inspect
import json
import math
import types
from collections.abc import Callable, Iterable, Mapping
from typing import Any, SupportsFloat

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"  # the id the maintainer assigns; identical on the server
_LAB = "lab_iceberg"

# Annotations, and why they are what they are (CONTRIBUTING.md asks for the most specific type
# that describes what the user should submit).
#
# `@typechecked` rejects at the client boundary, before any of the helpers below can produce a
# message, so a hint that is too narrow fails correct work with typeguard's wording instead of
# ours. Three measured constraints shape the choices:
#
#   * ``np.float64`` passes ``float`` (it subclasses it) but ``np.float32``, ``np.int64`` and
#     0-d arrays do not. A participant reading a median off a numpy array can hold any of them,
#     so numbers are annotated ``SupportsFloat``, which admits all of those and still rejects a
#     str, list, dict, tuple or None; ``_num`` then casts and checks finiteness.
#   * A *parameterized* collection re-checks keys, so ``Mapping[tuple[int, int], float]`` would
#     reject the ``{(np.int64, np.int64): np.float64}`` map that iterating a numpy array
#     naturally produces. The <Zbar> maps are therefore bare ``Mapping``, with ``_zbar_map``
#     validating keys and values.
#   * typeguard only checks a collection's first item unless asked otherwise, so a parameterized
#     container buys less than it appears to; the per-element validation below is what holds.
#     ``Iterable`` rather than ``Sequence`` wherever a participant might hold an ndarray, which
#     is not a ``Sequence``.
#
# What the annotations do buy is the common confusions, caught before a request is built: a
# scalar where a map belongs, a string where a number belongs, a dict where a list belongs.
#
# The remaining ``Any`` parameters are deliberate, and each is validated explicitly instead:
#
#   * **The 22 function-valued ones.** ``Callable`` reads better but is worse for the
#     participant: typeguard intercepts the single most common mistake in this lab - passing
#     ``fn(...)`` where ``fn`` belongs - and reports `argument "full_circuit" (int) is not
#     callable`. ``_require_callable`` instead says *"Pass the function full_circuit itself, not
#     a call to it"*, which is the fix. EXERCISES.md section 3 documents that message as the
#     contract and the client tests assert it, so the hand-rolled check wins. Every one of these
#     parameters is guarded on the first line of its function.
#   * **``lattice``/``placement`` (ex1_2, ex3_1) and ``gsched`` (ex1_4, ex3_2).** The challenge's
#     own ``LogicalLattice``, ``Placement`` and ``GateSchedule``. Annotating them would bind the
#     check to ``_iceberg``'s copy of the class while the participant holds the challenge
#     folder's - two identical classes that fail ``isinstance`` against each other, rejecting
#     correct work. Verified: ``isinstance(utils_lattice, _iceberg.LogicalLattice)`` is False.


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


# Shared definitions (identical in the server module; the server uses its own copy)
TOY_ROWS = {1: {1: (15, 0), 2: (12, 1)}, 2: {1: (15, 1), 2: (12, 0)}}
TOY_BUBBLE = [(15, 1), (12, 0)]

J = 1.0
GZ_MELTING = 0.5
GX = 0.75
DELTA_T = 0.5

#: Probe cases, in the order the server expects them.
CIRC_ELEMENTS_CASES = [[], ["trotter"], ["trotter", "syndrome"]]
LOGICAL_X_CASES = [(15, 0, 0), (15, 1, 1), (12, 0, 1), (12, 1, 0)]
SWAP_CASES = [(15, 0), (12, 1)]
MEASURE_SYNDROME_CASES = [(0, 15, 0, 0, False), (1, 12, 1, 0, True)]
SYNDROME_EXTRACTION_CASES = [(0, False, False), (0, True, False), (0, False, True)]
FINAL_MEASUREMENT_CASES = ["compute", "syndrome", "compute-frame1"]
PREP_BLOCKS_CASES = [[0, 0], [1, 1]]

ORP_PROBE_SEED = 2026
ORP_PROBE_SHOTS = 400
BOOTSTRAP_RNG_SEED = 7
#: Firing probability of each probe detector, and the data bit it drags when it fires.
PROBE_DETECTORS = ((0, 0.45, 1), (1, 0.25, None), (2, 0.30, 3), (3, 0.20, None))

L_SITES = 42
_IGNORED_OPS = ("barrier", "id")


# helpers
def _signature(qc: Any, *, with_params: bool = False) -> list:
    """A circuit's op-signature as JSON: ``[[name, [qubits], [clbits]], ...]``.

    Barriers and ``id`` are dropped, and bits become integer indices, so two circuits built on
    equal-sized registers compare equal however they obtained their register objects.

    ``with_params=True`` appends the gate parameters as a fourth element, which the two
    statevector-graded probes need and the structural ones must not have: the grader compares
    gate order only, so requiring identical angles would fail a correct circuit.
    """
    if not hasattr(qc, "data") or not hasattr(qc, "find_bit"):
        raise ValueError(
            "Expected a QuantumCircuit. Make sure your function returns the circuit it built "
            f"on, not None - got {type(qc).__name__}."
        )
    out = []
    for inst in qc.data:
        name = inst.operation.name
        if name in _IGNORED_OPS:
            continue
        op = [
            str(name),
            [int(qc.find_bit(q).index) for q in inst.qubits],
            [int(qc.find_bit(c).index) for c in inst.clbits],
        ]
        if with_params:
            params = []
            for p in inst.operation.params:
                try:
                    params.append(float(p))
                except (TypeError, ValueError):
                    raise ValueError(
                        f"The {name} gate has an unbound parameter; bind every parameter "
                        "before grading (qc.assign_parameters)."
                    ) from None
            op.append(params)
        out.append(op)
    return out


def _require_callable(fn: object, name: str) -> Callable:
    if not callable(fn):
        raise ValueError(
            f"Pass the function {name} itself, not a call to it: "
            f"grade_lab_iceberg_...({name}), not {name}(...). Got {type(fn).__name__}."
        )
    return fn  # type: ignore[return-value]


def _num(x: Any, what: str) -> float:
    try:
        v = float(x)
    except Exception:
        raise ValueError(f"{what} must be a number, got {type(x).__name__}.") from None
    if not math.isfinite(v):
        raise ValueError(f"{what} is NaN or infinite; check the step that produced it.")
    return v


def _site_key(site: Any) -> str:
    """``(block, logical)`` -> a JSON string, because JSON object keys must be strings."""
    try:
        return json.dumps([int(x) for x in site])
    except Exception:
        raise ValueError(
            f"Expected a (block, logical) site pair, got {site!r}. The keys of your "
            "<Zbar> dictionary are the lattice sites."
        ) from None


def _obs_key(key: Any) -> str:
    try:
        site, rep = key
        return json.dumps([[int(x) for x in site], int(rep)])
    except Exception:
        raise ValueError(
            f"Expected a (site, representative) key, got {key!r}: the observables are keyed "
            "by ((block, logical), rep)."
        ) from None


def _zbar_map(values: object, what: str) -> dict:
    if not isinstance(values, dict):
        raise ValueError(
            f"{what} must be a dict of {{site: <Zbar>}}, got {type(values).__name__}."
        )
    if not values:
        raise ValueError(f"{what} is empty: did the job results come back?")
    if len(values) > 4 * L_SITES:
        raise ValueError(
            f"{what} has {len(values)} entries, which is more than this lattice "
            "can have."
        )
    return {_site_key(site): _num(v, f"{what}[{site!r}]") for site, v in values.items()}


def _levels(mapping: Any, field: str) -> dict:
    """``{(site, rep): array}`` -> ``{json key: [floats]}``, NaN preserved as None."""
    if not isinstance(mapping, dict):
        raise ValueError(f"{field} must be a dict keyed by (site, representative).")
    out = {}
    for key, obs in mapping.items():
        series = obs.get(field) if isinstance(obs, dict) else obs
        if series is None:
            raise ValueError(f"The entry for {key!r} has no {field!r}.")
        vals = []
        for x in series:
            v = float(x)
            vals.append(None if not math.isfinite(v) else v)
        out[_obs_key(key)] = vals
    return out


def _toy_system():
    """``(lattice, block_qubits, placement, block_to_index)`` for the toy system."""
    from ._iceberg.iceberg_layout import PLACEMENT, LogicalLattice, Placement

    lattice = LogicalLattice.from_rows(TOY_ROWS, omit=[])
    block_qubits = {b: PLACEMENT[b] for b in lattice.blocks()}
    placement = Placement.from_qubits(placement=block_qubits)
    block_to_index = {b[0]: i for i, b in enumerate(placement.blocks.items())}
    return lattice, block_qubits, placement, block_to_index


def _fresh_circuit(num_blocks: int = 2, rounds: int = 1):
    """An empty circuit on the device register with the notebook's register layout."""
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    _, _, placement, _ = _toy_system()
    syn = [ClassicalRegister(2 * num_blocks, f"syn{i}") for i in range(rounds)]
    data = ClassicalRegister(4 * num_blocks, "data")
    qreg = QuantumRegister(placement.topology.n_qubits, "q")
    return QuantumCircuit(qreg, *syn, data), [0] * num_blocks, placement


class _ParamA:
    """The identity site -> code-qubit map, so probes do not depend on the optimizer's ``l``."""

    def code_qubit(self, site):
        return site


class _GateSchedule:
    """Records how ``full_circuit`` drives a schedule, and flips frames as the real one does."""

    def __init__(self, placement):
        self.placement = placement
        self.calls: list[dict] = []

    def append_step(
        self, qc, frames, delta_t, J_, gx, gz, reverse=False, barriers=False
    ):
        self.calls.append(
            {
                "delta_t": float(delta_t),
                "J": float(J_),
                "gx": float(gx),
                "gz": float(gz),
                "reverse": bool(reverse),
            }
        )
        for i, (_b, block) in enumerate(self.placement.blocks.items()):
            qc.rz(delta_t * (1 + i), block.physical("d0", frames[i]))
        return qc, [1 - f for f in frames]


def _orp_probe(num_logical_blocks: int = 2):
    """The synthetic ORP probe. Deterministic: seed 2026, 400 shots."""
    import numpy as np

    rng = np.random.default_rng(ORP_PROBE_SEED)
    n_data, n_syn = 4 * num_logical_blocks, 2 * num_logical_blocks
    data, syn = [], []
    for _ in range(ORP_PROBE_SHOTS):
        bits = rng.integers(0, 2, n_data)
        for b in range(num_logical_blocks):
            blk = slice(4 * b, 4 * b + 4)
            if bits[blk].sum() % 2 == 1:
                bits[4 * b] ^= 1
        sbits = np.zeros(n_syn, dtype=int)
        for v, p_fire, dragged in PROBE_DETECTORS:
            if v < n_syn and rng.random() < p_fire:
                sbits[v] = 1
                if dragged is not None and dragged < n_data:
                    bits[dragged] ^= 1
        if rng.random() < 0.15:
            bits[2] ^= 1
        data.append("".join(str(x) for x in bits[::-1]))
        syn.append("".join(str(x) for x in sbits[::-1]))
    return [data], [[syn]]


_BLOCKS = "num_logical_blocks"


def _shadow_call(fn: Any, args: tuple, **overrides):
    """Call ``fn`` with ``overrides`` pinned in a copy of its globals, leaving the real ones."""
    target = getattr(fn, "__func__", fn)
    globs = getattr(target, "__globals__", None)
    code = getattr(target, "__code__", None)
    if globs is None or code is None:
        return fn(*args)

    clone = types.FunctionType(
        code,
        {**globs, **overrides},
        target.__name__,
        target.__defaults__,
        target.__closure__,
    )
    clone.__kwdefaults__ = target.__kwdefaults__
    if fn is not target:
        clone = clone.__get__(fn.__self__, type(fn.__self__))
    return clone(*args)


def _call_with_optional_blocks(fn: Any, name: str, *args, num_logical_blocks: int = 2):
    """Call ``fn``, passing ``num_logical_blocks`` only if it accepts it (P3-19).

    The wire contract passes it explicitly, but the notebook's ``postselect_parity`` reads it
    from the module globals instead. Both are supported: pass the argument when the signature
    has a slot for it, otherwise pin it in a shadow copy of the globals (see ``_shadow_call``).
    """
    try:
        params = list(inspect.signature(fn).parameters.values())
    except (TypeError, ValueError):
        params = []

    named = next((p for p in params if p.name == _BLOCKS), None)
    if named is not None:
        if named.kind is named.POSITIONAL_ONLY:
            return fn(*args, num_logical_blocks)
        if named.kind in (named.POSITIONAL_OR_KEYWORD, named.KEYWORD_ONLY):
            return fn(*args, **{_BLOCKS: num_logical_blocks})

    if any(p.kind is p.VAR_KEYWORD for p in params):
        return fn(*args, **{_BLOCKS: num_logical_blocks})
    if any(p.kind is p.VAR_POSITIONAL for p in params):
        return fn(*args, num_logical_blocks)

    required = [
        p
        for p in params
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        and p.default is p.empty
    ]
    if len(required) > len(args):
        return fn(*args, num_logical_blocks)

    return _shadow_call(fn, args, **{_BLOCKS: num_logical_blocks})


# 1.2
@typechecked
def grade_lab_iceberg_ex1_2(
    lattice: Any, block_qubits: Mapping, bubble_sites: Iterable, placement: Any
) -> None:
    """PART 1.2 - the toy system: ``lattice``, ``block_qubits``, ``bubble_sites``,
    ``placement``."""
    try:
        sites = [[int(b), int(lq)] for b, lq in lattice.nodes()]
        edges = [[[int(x) for x in u], [int(y) for y in v]] for u, v in lattice.edges]
    except Exception:
        raise ValueError(
            "Could not read the lattice: pass the LogicalLattice returned by "
            "LogicalLattice.from_rows(...)."
        ) from None
    if not isinstance(block_qubits, dict):
        raise ValueError(
            "block_qubits must be a dict of {block: [six physical qubits]}."
        )
    answer = {
        "sites": sites,
        "edges": edges,
        "block_qubits": {
            str(int(b)): [int(q) for q in qs] for b, qs in block_qubits.items()
        },
        "bubble": [[int(b), int(lq)] for b, lq in bubble_sites],
    }
    _grade(answer, "ex1_2")


# 1.3
@typechecked
def grade_lab_iceberg_ex1_3(
    init_circuit: Any,
    prep_logical_zero: Any,
    prep_logical_zero_blocks: Any,
    logical_x: Any,
    create_bubble: Any,
) -> None:
    """PART 1.3 - the five state-preparation functions, evaluated on the fixed probes."""
    from qiskit import QuantumCircuit

    for fn, name in (
        (init_circuit, "init_circuit"),
        (prep_logical_zero, "prep_logical_zero"),
        (prep_logical_zero_blocks, "prep_logical_zero_blocks"),
        (logical_x, "logical_x"),
        (create_bubble, "create_bubble"),
    ):
        _require_callable(fn, name)

    lattice, _, _, block_to_index = _toy_system()

    qc, frames = init_circuit(2, 1, _toy_system()[2].topology.n_qubits)
    if not hasattr(qc, "cregs"):
        raise ValueError("init_circuit must return (circuit, frames).")
    answer: dict[str, Any] = {
        "init_regs": [[str(r.name), int(r.size)] for r in qc.cregs],
        "init_frames": [int(f) for f in frames],
        "init_nq": int(qc.num_qubits),
        "ghz": _signature(
            prep_logical_zero(QuantumCircuit(4), 0, 1, 2, 3), with_params=True
        ),
        "blocks": [],
        "logical_x": [],
        "bubble": [],
    }

    for fr in PREP_BLOCKS_CASES:
        probe, _, place = _fresh_circuit()
        answer["blocks"].append(
            _signature(
                prep_logical_zero_blocks(
                    probe, fr, place, block_to_index, barriers=False
                )
            )
        )
    for b, lq, frame in LOGICAL_X_CASES:
        probe, _, place = _fresh_circuit()
        answer["logical_x"].append(_signature(logical_x(probe, place, b, lq, frame)))
    for fr in PREP_BLOCKS_CASES:
        probe, _, place = _fresh_circuit()
        answer["bubble"].append(
            _signature(
                create_bubble(
                    probe,
                    fr,
                    place,
                    lattice,
                    _ParamA(),
                    TOY_BUBBLE,
                    block_to_index,
                    barriers=False,
                )
            )
        )
    _grade(answer, "ex1_3")


# 1.4 / 3.2
def _schedule_answer(gsched: Any) -> dict:
    for attr in ("depth", "n_cx", "status"):
        if not hasattr(gsched, attr):
            raise ValueError(
                "Pass the `gsched` returned by ScheduleOptimizer.optimize() - the third "
                f"element of (A, step, gsched). It has no {attr!r}."
            )
    return {
        "depth": int(gsched.depth),
        "n_cx": int(gsched.n_cx),
        "status": str(gsched.status),
    }


@typechecked
def grade_lab_iceberg_ex1_4(gsched: Any) -> None:
    """PART 1.4 - the toy Trotter-step schedule: ``gsched``."""
    _grade(_schedule_answer(gsched), "ex1_4")


@typechecked
def grade_lab_iceberg_ex3_2(gsched_L: Any) -> None:
    """PART 3.2 - the 21-block Trotter-step schedule: ``gsched_L``."""
    _grade(_schedule_answer(gsched_L), "ex3_2")


# 1.5a
@typechecked
def grade_lab_iceberg_ex1_5a(
    compute_to_syndrome: Any,
    syndrome_to_compute: Any,
    measure_syndromes: Any,
    syndrome_extraction: Any,
) -> None:
    """PART 1.5 - the four syndrome-extraction functions, on the fixed probes."""
    for fn, name in (
        (compute_to_syndrome, "compute_to_syndrome"),
        (syndrome_to_compute, "syndrome_to_compute"),
        (measure_syndromes, "measure_syndromes"),
        (syndrome_extraction, "syndrome_extraction"),
    ):
        _require_callable(fn, name)

    answer: dict[str, list] = {
        "compute_to_syndrome": [],
        "syndrome_to_compute": [],
        "measure_syndromes": [],
        "syndrome_extraction": [],
    }
    for field, fn in (
        ("compute_to_syndrome", compute_to_syndrome),
        ("syndrome_to_compute", syndrome_to_compute),
    ):
        for b, frame in SWAP_CASES:
            probe, _, place = _fresh_circuit()
            fn(probe, place.blocks[b], frame)  # mutates in place
            answer[field].append(_signature(probe))
    for i, b, frame, rnd, reset in MEASURE_SYNDROME_CASES:
        probe, _, place = _fresh_circuit()
        measure_syndromes(probe, i, place.blocks[b], frame, rnd, reset)
        answer["measure_syndromes"].append(_signature(probe))
    for rnd, terminal, reset in SYNDROME_EXTRACTION_CASES:
        probe, _, place = _fresh_circuit()
        returned = syndrome_extraction(
            probe, place, rnd, terminal=terminal, barriers=False, reset_ancillas=reset
        )
        answer["syndrome_extraction"].append(
            _signature(returned if returned is not None else probe)
        )
    _grade(answer, "ex1_5a")


# 1.5b
@typechecked
def grade_lab_iceberg_ex1_5b(final_measurements: Any) -> None:
    """PART 1.5 - ``final_measurements``, in both configurations."""
    _require_callable(final_measurements, "final_measurements")
    probes = []
    for case in FINAL_MEASUREMENT_CASES:
        probe, frames, place = _fresh_circuit()
        config = "compute" if case.startswith("compute") else "syndrome"
        fr = [1, 1] if case.endswith("frame1") else frames
        returned = final_measurements(probe, place, fr, configuration=config)
        probes.append(_signature(returned if returned is not None else probe))
    _grade({"probes": probes}, "ex1_5b")


# 1.6
@typechecked
def grade_lab_iceberg_ex1_6(full_circuit: Any) -> None:
    """PART 1.6 - ``full_circuit``, on the three ``circ_elements`` cases."""
    _require_callable(full_circuit, "full_circuit")
    lattice, _, _, block_to_index = _toy_system()
    probes, calls = [], []
    for ce in CIRC_ELEMENTS_CASES:
        _, _, place, _ = _toy_system()
        gs = _GateSchedule(place)
        qc = full_circuit(
            gs,
            _ParamA(),
            TOY_BUBBLE,
            ce,
            lattice,
            place,
            block_to_index,
            gz=GZ_MELTING,
            barriers=False,
        )
        probes.append(_signature(qc))
        calls.append(gs.calls)
    _grade({"probes": probes, "calls": calls}, "ex1_6")


# 1.7
@typechecked
def grade_lab_iceberg_ex1_7(build_observables: Any) -> None:
    """PART 1.7 - ``build_observables``, as sparse Pauli lists."""
    _require_callable(build_observables, "build_observables")
    lattice, _, placement, _ = _toy_system()
    encoded, unencoded = build_observables(placement, lattice, _ParamA())

    def terms(op):
        try:
            simplified = op.simplify()
            return [
                [str(p), float(c.real), float(c.imag)]
                for p, c in zip(simplified.paulis, simplified.coeffs)
            ]
        except Exception:
            raise ValueError(
                "The observables must be SparsePauliOp instances; build them with "
                "SparsePauliOp.from_sparse_list."
            ) from None

    _grade(
        {
            "encoded": {_obs_key(k): terms(v) for k, v in encoded.items()},
            "unencoded": {_site_key(k): terms(v) for k, v in unencoded.items()},
        },
        "ex1_7",
    )


# 1.8
@typechecked
def grade_lab_iceberg_ex1_8(part1_noisy_obs: Iterable) -> None:
    """PART 1.8 - the noisy-simulation curve: ``part1_noisy_obs``."""
    import numpy as np

    if not isinstance(part1_noisy_obs, (list, tuple)):
        raise ValueError(
            "part1_noisy_obs must be a list with one entry per Trotter depth."
        )
    curve = []
    for i, entry in enumerate(part1_noisy_obs):
        if isinstance(entry, dict):
            if not entry:
                raise ValueError(f"The entry for Trotter depth {i} is empty.")
            curve.append(
                float(np.mean([abs(_num(v, "an observable")) for v in entry.values()]))
            )
        else:
            curve.append(abs(_num(entry, f"part1_noisy_obs[{i}]")))
    _grade({"mean_abs": curve}, "ex1_8")


# 1.9
@typechecked
def grade_lab_iceberg_ex1_9(unencoded_trotter_circuit: Any) -> None:
    """PART 1.9 - ``unencoded_trotter_circuit``, with and without measurement."""
    _require_callable(unencoded_trotter_circuit, "unencoded_trotter_circuit")
    lattice, _, _, _ = _toy_system()
    sites = list(lattice.nodes())
    order = [
        [("x", sites[0]), ("z", sites[1]), ("zz", sites[0], sites[1])],
        [("x", sites[2]), ("zz", sites[2], sites[3])],
    ]
    answer = {
        "no_measure": _signature(
            unencoded_trotter_circuit(
                order, lattice, TOY_BUBBLE, DELTA_T, J, GX, GZ_MELTING, measure=False
            ),
            with_params=True,
        ),
        "with_measure": _signature(
            unencoded_trotter_circuit(
                order, lattice, TOY_BUBBLE, DELTA_T, J, GX, GZ_MELTING, measure=True
            ),
            with_params=True,
        ),
        "num_qubits": len(sites),
    }
    _grade(answer, "ex1_9")


# 2.1
@typechecked
def grade_lab_iceberg_ex2_1(
    postselect_parity: Any, num_logical_blocks: int = 2
) -> None:
    """PART 2.1 - ``postselect_parity``, on the synthetic ORP probe."""
    _require_callable(postselect_parity, "postselect_parity")
    data_list, syn_list = _orp_probe(num_logical_blocks)
    result = _call_with_optional_blocks(
        postselect_parity,
        "postselect_parity",
        data_list,
        syn_list,
        num_logical_blocks=num_logical_blocks,
    )
    try:
        kept, kept_syn = result
    except Exception:
        raise ValueError(
            "postselect_parity must return (data_bitstrings_ps_list, syn_bitstrings_ps_list)."
        ) from None
    _grade(
        {
            "kept": [[str(s) for s in circuit] for circuit in kept],
            "kept_syn": [
                [[str(s) for s in rnd] for rnd in circuit] for circuit in kept_syn
            ],
        },
        "ex2_1",
    )


# 2.2
@typechecked
def grade_lab_iceberg_ex2_2(
    detector_violations: Any, num_logical_blocks: int = 2
) -> None:
    """PART 2.2 - ``detector_violations``, on the post-selected probe syndromes.

    2.2 consumes the output of 2.1, so the probe is post-selected first: raw shots would make
    every mask the wrong length.
    """
    _require_callable(detector_violations, "detector_violations")
    from .lab_iceberg_probes import probe_postselected

    _, syn_ps = probe_postselected(num_logical_blocks)
    masks = detector_violations(syn_ps, num_logical_blocks)
    if not isinstance(masks, dict):
        raise ValueError(
            "detector_violations must return a dict keyed by detector index."
        )
    out_masks, out_nps = {}, {}
    for v, item in masks.items():
        mask = item.get("mask") if isinstance(item, dict) else item
        if mask is None:
            raise ValueError(f"The entry for detector {v!r} has no 'mask'.")
        out_masks[str(int(v))] = [bool(x) for x in mask]
        n_ps = item.get("n_ps") if isinstance(item, dict) else None
        out_nps[str(int(v))] = (
            int(n_ps) if n_ps is not None else int(sum(1 for x in mask if not x))
        )
    _grade({"masks": out_masks, "n_ps": out_nps}, "ex2_2")


# 2.3
@typechecked
def grade_lab_iceberg_ex2_3(
    compute_correlations: Any, num_logical_blocks: int = 2
) -> None:
    """PART 2.3 - ``compute_correlations``, on the probe."""
    _require_callable(compute_correlations, "compute_correlations")
    from .lab_iceberg_probes import probe_masks, probe_observables, probe_postselected

    data_ps, syn_ps = probe_postselected(num_logical_blocks)
    masks = probe_masks(syn_ps, num_logical_blocks)
    enc = probe_observables(num_logical_blocks)
    corr = compute_correlations(enc, data_ps, masks, num_logical_blocks)
    _grade(
        {
            "delta": {
                _obs_key(k): [_num(x, "a correlation") for x in v]
                for k, v in corr.items()
            }
        },
        "ex2_3",
    )


# 2.4
@typechecked
def grade_lab_iceberg_ex2_4(
    bootstrap_obs_uncertainty: Any, num_logical_blocks: int = 2
) -> None:
    """PART 2.4 - ``bootstrap_obs_uncertainty``, seeded and on fewer shots."""
    import numpy as np
    from qiskit.primitives import BitArray

    _require_callable(bootstrap_obs_uncertainty, "bootstrap_obs_uncertainty")
    from .lab_iceberg_probes import probe_observables, probe_postselected

    data_ps, _ = probe_postselected(num_logical_blocks)
    obs = next(iter(probe_observables(num_logical_blocks).values()))
    full = BitArray.from_samples(data_ps, num_bits=4 * num_logical_blocks)
    small = BitArray.from_samples(
        data_ps[: max(1, len(data_ps) // 8)], num_bits=4 * num_logical_blocks
    )
    seeded = bootstrap_obs_uncertainty(
        obs, full, n_samples=1000, rng=np.random.default_rng(BOOTSTRAP_RNG_SEED)
    )
    fewer = bootstrap_obs_uncertainty(
        obs, small, n_samples=1000, rng=np.random.default_rng(BOOTSTRAP_RNG_SEED)
    )
    _grade(
        {
            "sig2_seeded": _num(seeded, "the bootstrap variance"),
            "sig2_small": _num(fewer, "the small-sample bootstrap variance"),
        },
        "ex2_4",
    )


# 2.5
@typechecked
def grade_lab_iceberg_ex2_5(compute_obs_k: Any, num_logical_blocks: int = 2) -> None:
    """PART 2.5 - ``compute_obs_k``, on the probe."""
    _require_callable(compute_obs_k, "compute_obs_k")
    from .lab_iceberg_probes import (
        probe_correlations,
        probe_masks,
        probe_observables,
        probe_postselected,
    )

    data_ps, syn_ps = probe_postselected(num_logical_blocks)
    masks = probe_masks(syn_ps, num_logical_blocks)
    enc = probe_observables(num_logical_blocks)
    corr = probe_correlations(num_logical_blocks)
    obs_k = compute_obs_k(enc, data_ps, masks, corr, num_logical_blocks)
    _grade(
        {
            "f_k": _levels(obs_k, "f_k"),
            "O_k": _levels(obs_k, "O_k"),
            "sig2_k": _levels(obs_k, "sig2_k"),
        },
        "ex2_5",
    )


# 2.6
@typechecked
def grade_lab_iceberg_ex2_6(compute_obs_ref: Any, select_k: Any) -> None:
    """PARTS 2.6-2.7 - ``compute_obs_ref`` and ``select_k``, on the fixed obs_k probe."""
    _require_callable(compute_obs_ref, "compute_obs_ref")
    _require_callable(select_k, "select_k")
    from .lab_iceberg_probes import reference_obs_k

    with_ref = compute_obs_ref(
        {k: dict(v) for k, v in reference_obs_k().items()}, 0.05, 0.5, R=1
    )
    selected = select_k({k: dict(v) for k, v in with_ref.items()}, z=1, target_len=2)
    key = next(iter(selected))
    _grade(
        {
            "O_ref": _num(with_ref[key]["O_ref"], "O_ref"),
            "k_star": int(selected[key]["k_star"]),
        },
        "ex2_6",
    )


# 2.7
@typechecked
def grade_lab_iceberg_ex2_7(run_orp: Any, num_logical_blocks: int = 2) -> None:
    """PART 2.8 - ``run_orp``, the whole pipeline on the probe."""
    _require_callable(run_orp, "run_orp")
    from .lab_iceberg_probes import probe_observables

    data_list, syn_list = _orp_probe(num_logical_blocks)
    enc = probe_observables(num_logical_blocks)
    obs_k_list = run_orp(
        enc,
        data_list,
        syn_list,
        num_logical_blocks,
        n_samples=1000,
        f_min=0.05,
        f_ref=0.5,
        z=1,
        target_len=2,
    )
    if not obs_k_list:
        raise ValueError(
            "run_orp returned nothing; it should give one obs_k dict per circuit."
        )
    obs_k = obs_k_list[0]
    _grade(
        {
            "f_k": _levels(obs_k, "f_k"),
            "O_k": _levels(obs_k, "O_k"),
            "sig2_k": _levels(obs_k, "sig2_k"),
            "O_ref": {_obs_key(k): _num(v["O_ref"], "O_ref") for k, v in obs_k.items()},
            "k_star": {_obs_key(k): int(v["k_star"]) for k, v in obs_k.items()},
            "O_k_star": {
                _obs_key(k): _num(v["O_k_star"], "O_k_star") for k, v in obs_k.items()
            },
        },
        "ex2_7",
    )


# 3.1
@typechecked
def grade_lab_iceberg_ex3_1(
    lattice_L: Any, block_qubits_L: Mapping, bubble_sites_L: Iterable, placement_L: Any
) -> None:
    """PART 3.1 - the full Fig. 2a system."""
    try:
        sites = list(lattice_L.nodes())
        n_edges = len(list(lattice_L.edges))
    except Exception:
        raise ValueError(
            "Could not read lattice_L; pass the LogicalLattice itself."
        ) from None
    _grade(
        {
            "n_sites": len(sites),
            "n_blocks": len({int(b) for b, _ in sites}),
            "n_edges": int(n_edges),
            "bubble": [[int(b), int(lq)] for b, lq in bubble_sites_L],
        },
        "ex3_1",
    )


# 3.3
@typechecked
def grade_lab_iceberg_ex3_3(
    isa_qcs_L: Iterable, n_steps_L_list: Iterable | None = None
) -> None:
    """PART 3.3 - the transpiled encoded circuits: ``isa_qcs_L_melting``."""
    circuits = list(isa_qcs_L)
    if not circuits:
        raise ValueError("isa_qcs_L is empty: transpile the circuits first.")

    def two_q(inst):
        return inst.operation.num_qubits == 2

    try:
        depths = [int(qc.depth(two_q)) for qc in circuits]
    except Exception:
        raise ValueError(
            "Could not measure the two-qubit depth; pass the transpiled (ISA) circuits."
        ) from None
    permuted = False
    try:
        layout = circuits[0].layout
        if layout is not None and layout.final_layout is not None:
            permuted = layout.final_layout.to_permutation(circuits[0].qubits) != list(
                range(circuits[0].num_qubits)
            )
    except Exception:
        permuted = False
    _grade({"depth2q": depths, "permuted": bool(permuted)}, "ex3_3")


# 3.4
@typechecked
def grade_lab_iceberg_ex3_4(
    data_bitstrings_list: Iterable, syn_bitstrings_list: Iterable, obs_k_list: Iterable
) -> None:
    """PART 3.4 - job retrieval and post-selection, as summary numbers."""
    if not data_bitstrings_list or not syn_bitstrings_list:
        raise ValueError(
            "The bitstring lists are empty: did the job results come back?"
        )
    first_data = data_bitstrings_list[0]  # ty: ignore[not-subscriptable]
    first_syn = syn_bitstrings_list[0]  # ty: ignore[not-subscriptable]
    if not first_data or not first_syn:
        raise ValueError("The first circuit has no shots.")
    obs_k = obs_k_list[0] if obs_k_list else {}  # ty: ignore[not-subscriptable]
    f0 = []
    for v in obs_k.values():
        series = v.get("f_k") if isinstance(v, dict) else None
        if series is not None and len(series):
            f0.append(_num(series[0], "f_k[0]"))
    _grade(
        {
            "width": len(str(first_data[0])),
            "syn_width": len(str(first_syn[0][0])),
            "shots": len(first_data),
            "rounds": len(first_syn),
            "n_obs": len(obs_k),
            "f0": f0,
        },
        "ex3_4",
    )


# 3.5
@typechecked
def grade_lab_iceberg_ex3_5(
    enc_melting: Mapping,
    enc_localized: Mapping,
    median_melting: SupportsFloat,
    median_localized: SupportsFloat,
) -> None:
    """PARTS 3.5-3.6 - the per-site ``<Zbar>`` of both regimes, and your two medians."""
    _grade(
        {
            "enc_melting": _zbar_map(enc_melting, "enc_melting"),
            "enc_localized": _zbar_map(enc_localized, "enc_localized"),
            "median_melting": _num(median_melting, "median_melting"),
            "median_localized": _num(median_localized, "median_localized"),
        },
        "ex3_5",
    )


# 4.1
@typechecked
def grade_lab_iceberg_ex4_1(
    isa_qcs_unenc: Iterable, n_steps_L_list: Iterable | None = None
) -> None:
    """PART 4.1 - the transpiled unencoded circuits: ``isa_qcs_unenc_melting``."""
    circuits = list(isa_qcs_unenc)
    if not circuits:
        raise ValueError(
            "isa_qcs_unenc is empty: transpile the unencoded circuits first."
        )
    layouts = []
    for qc in circuits:
        try:
            layouts.append(
                [int(q) for q in qc.layout.initial_index_layout(filter_ancillas=True)]
            )
        except Exception:
            raise ValueError(
                "Could not read a circuit layout; pass the transpiled (ISA) circuits."
            ) from None

    def two_q(inst):
        return inst.operation.num_qubits == 2

    _grade(
        {"layouts": layouts, "depth2q_deepest": int(circuits[-1].depth(two_q))}, "ex4_1"
    )


# 4.2
@typechecked
def grade_lab_iceberg_ex4_2(
    enc_melting: Mapping,
    unenc_melting: Mapping,
    enc_localized: Mapping,
    unenc_localized: Mapping,
) -> None:
    """PART 4.3 - the four per-site ``<Zbar>`` maps of the comparison."""
    _grade(
        {
            "enc_melting": _zbar_map(enc_melting, "enc_melting"),
            "unenc_melting": _zbar_map(unenc_melting, "unenc_melting"),
            "enc_localized": _zbar_map(enc_localized, "enc_localized"),
            "unenc_localized": _zbar_map(unenc_localized, "unenc_localized"),
        },
        "ex4_2",
    )


# 5.1
@typechecked
def grade_lab_iceberg_ex5_1(
    mitigation_applied: object,
    enc_mitigated: Mapping,
    unenc_mitigated: Mapping,
    median_enc_unmitigated: SupportsFloat | None = None,
) -> None:
    """PART 5.1 - the improved arms, and your unmitigated PART 3.5 median."""
    if hasattr(mitigation_applied, "__dict__") and not isinstance(
        mitigation_applied, (str, dict)
    ):
        note = repr(vars(mitigation_applied))
    else:
        note = (
            mitigation_applied
            if isinstance(mitigation_applied, str)
            else json.dumps(mitigation_applied, default=str)
        )
    _grade(
        {
            "applied": str(note)[:2000],
            "enc": _zbar_map(enc_mitigated, "enc_mitigated"),
            "unenc": _zbar_map(unenc_mitigated, "unenc_mitigated"),
            "median_before": _num(median_enc_unmitigated, "median_enc_unmitigated")
            if median_enc_unmitigated is not None
            else float("nan"),
        },
        "ex5_1",
    )


# 5.2
@typechecked
def grade_lab_iceberg_ex5_2(
    backend_name: object,
    depth_heavyhex: SupportsFloat,
    depth_square: SupportsFloat,
    gates_heavyhex: SupportsFloat,
    gates_square: SupportsFloat,
    unenc_square: Mapping,
) -> None:
    """PART 5.2 - the square-lattice run: backend, depths, gate counts, per-site ``<Zbar>``."""
    _grade(
        {
            "backend": str(backend_name)[:128],
            "depth_hh": int(depth_heavyhex),  # ty: ignore[invalid-argument-type]
            "depth_sq": int(depth_square),  # ty: ignore[invalid-argument-type]
            "gates_hh": int(gates_heavyhex),  # ty: ignore[invalid-argument-type]
            "gates_sq": int(gates_square),  # ty: ignore[invalid-argument-type]
            "unenc_sq": _zbar_map(unenc_square, "unenc_square"),
        },
        "ex5_2",
    )
