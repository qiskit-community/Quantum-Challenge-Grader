"""Floquet dynamics lab (qdc_2026 / lab_floquet): client-side grading functions.

Participant callables are evaluated here on fixed probes and fakes; only the reduced
outputs are sent. The server holds its own copy of every probe constant and never runs
participant code. Nothing in this module contacts a backend, a service, a ledger or a file.
"""

import math
import warnings
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
from qc_grader.grader.grade import grade_answer
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from typeguard import typechecked

from . import _floquet_probes as probes

_CHALLENGE = "qdc_2026"
_LAB = "lab_floquet"
_MAX_INSTRUCTIONS = 20_000  # identical to the server's hard cap
_MAX_ERROR_TEXT = 300


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


def _describe(err: BaseException) -> str:
    """``"<Type>: <message>"``, truncated so a long traceback text cannot bloat the payload."""
    return f"{type(err).__name__}: {err}"[:_MAX_ERROR_TEXT]


def _raise_from(err: Exception, name: str, hint: str) -> None:
    raise ValueError(f"Your {name} raised {type(err).__name__}: {err}. {hint}") from err


def _as_circuit(obj: object, what: str) -> QuantumCircuit:
    """Check that ``obj`` is a sendable circuit, or raise ``TypeError``/``ValueError``."""
    if not isinstance(obj, QuantumCircuit):
        raise TypeError(f"{what} must be a QuantumCircuit, got {type(obj).__name__}")
    if obj.num_parameters:
        raise ValueError(f"{what} has unbound parameters; bind them before grading")
    if len(obj.data) > _MAX_INSTRUCTIONS:
        raise ValueError(
            f"{what} has {len(obj.data)} instructions; at most {_MAX_INSTRUCTIONS:,} are accepted"
        )
    return obj


def _floats(values: object) -> list[float]:
    return [float(x) for x in np.asarray(values, dtype=float).ravel()]


def _ints(values: object) -> list[int]:
    out = []
    for x in values:  # ty: ignore[not-iterable] - participant data, guarded by the caller
        if isinstance(x, bool) or int(x) != x:
            raise ValueError(f"expected integers, got {x!r}")
        out.append(int(x))
    return out


def _edges(edges: object) -> list[list[int]]:
    return [_ints(edge) for edge in edges]  # ty: ignore[not-iterable] - guarded by the caller


def _groups(groups: object) -> list[list[list[int]]]:
    return [_edges(group) for group in groups]  # ty: ignore[not-iterable] - guarded by the caller


def _params(values: tuple[float, float, float]) -> probes.ProbeParams:
    return probes.ProbeParams(*values)


# --------------------------------------------------------------------------- #
# Part 1
# --------------------------------------------------------------------------- #


@typechecked
def grade_lab_floquet_ex1_1(
    lattice: object, groups: Sequence[Sequence[Sequence[int]]]
) -> None:
    """Submit the 21-qubit paper patch ``lattice`` and its colour classes ``groups``.

    Pass ``lattice = fh.paper_colored_lattice(21)`` and ``groups = fh.color_groups(lattice)``.
    """
    try:
        answer = {
            "n_qubits": int(lattice.n_qubits),  # ty: ignore[unresolved-attribute]
            "edges": _edges(lattice.edges),  # ty: ignore[unresolved-attribute]
            "groups": _groups(groups),
            "lattice_groups": _groups(lattice.color_groups()),  # ty: ignore[unresolved-attribute]
        }
    except (AttributeError, TypeError, ValueError) as err:
        raise ValueError(
            f"Pass the lattice returned by fh.paper_colored_lattice(21) and its groups ({_describe(err)})."
        ) from err
    _grade(answer, "ex1_1")


@typechecked
def grade_lab_floquet_ex1_2(floquet_cycle: Callable[..., Any]) -> None:
    """Submit your ``floquet_cycle(qc, groups, params)`` function.

    It is applied in place to empty 7-qubit circuits with the default and an alternative set of
    angles; its return value is ignored.
    """
    circuits = []
    for values in (probes.PARAMS, probes.ALT_PARAMS):
        qc = QuantumCircuit(probes.PROBE_N_QUBITS)
        try:
            floquet_cycle(qc, probes.probe_groups(), _params(values))
            circuits.append(_as_circuit(qc, "the circuit floquet_cycle built"))
        except Exception as err:  # noqa: BLE001 - participant code can raise anything
            _raise_from(
                err,
                "floquet_cycle",
                "It must append gates to qc in place and return None.",
            )
    _grade({"circuits": circuits}, "ex1_2")


# --------------------------------------------------------------------------- #
# Part 2
# --------------------------------------------------------------------------- #


def _probe_logical_circuit(fn: Callable[..., Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"error": None, "unmeasured": [], "measured": []}
    try:
        unmeasured, measured = [], []
        for depth in probes.LOGICAL_DEPTHS:
            plain = fn(
                depth, probes.probe_lattice(), probes.probe_groups(), measured=False
            )
            unmeasured.append(
                _as_circuit(plain, f"logical_circuit({depth}, measured=False)")
            )
            full = fn(depth, probes.probe_lattice(), probes.probe_groups())
            measured.append(_as_circuit(full, f"logical_circuit({depth})"))
        record.update(unmeasured=unmeasured, measured=measured)
    except Exception as err:  # noqa: BLE001
        record["error"] = _describe(err)
    return record


def _probe_baseline(fn: Callable[..., Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"error": None, "M": [], "Mz2": []}
    try:
        out = fn([dict(c) for c in probes.BASELINE_COUNTS], probes.probe_lattice())
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            raise TypeError("baseline_magnetizations must return the pair (M, Mz2)")
        record.update(M=_floats(out[0]), Mz2=_floats(out[1]))
    except Exception as err:  # noqa: BLE001
        record["error"] = _describe(err)
    return record


@typechecked
def grade_lab_floquet_ex2_1(
    logical_circuit: Callable[..., Any], baseline_magnetizations: Callable[..., Any]
) -> None:
    """Submit your ``logical_circuit`` and ``baseline_magnetizations`` functions (2.5 points each).

    Both are evaluated on the 7-qubit test lattice; an error in one does not stop the other.
    """
    answer = {
        "logical_circuit": _probe_logical_circuit(logical_circuit),
        "baseline_magnetizations": _probe_baseline(baseline_magnetizations),
    }
    _grade(answer, "ex2_1")


class _FakeMitigator:
    """Recording stand-in for ``mthree.M3Mitigation``."""

    def __init__(self, backend: object, expected_backend: object, fail: bool) -> None:
        self.got_backend = backend is expected_backend
        self.fail = fail
        self.cals_calls: list[dict[str, Any]] = []

    def cals_from_system(self, qubits: object = None, **settings: object) -> None:
        try:
            got = _ints(qubits)
        except Exception:  # noqa: BLE001 - recorded, judged on the server
            got = []
        plain = {
            str(k): v
            if isinstance(v, (bool, int, str)) and not isinstance(v, float)
            else repr(v)
            for k, v in settings.items()
        }
        self.cals_calls.append({"qubits": got, "settings": plain})
        if self.fail:
            raise RuntimeError(probes.READOUT_CAL_ERROR)


def _probe_mitigator(fn: Callable[..., Any], name: str) -> dict[str, Any]:
    backend = object()
    created: list[_FakeMitigator] = []
    tracker_qubits: list[list[int]] = []

    def m3_mitigation(target: object) -> _FakeMitigator:
        mitigator = _FakeMitigator(target, backend, fail=name == "B")
        created.append(mitigator)
        return mitigator

    @contextmanager
    def calibration_tracker(
        mitigator: object, qubits: object
    ) -> Generator[dict[str, Any], None, None]:
        try:
            tracker_qubits.append(_ints(qubits))
        except Exception:  # noqa: BLE001
            tracker_qubits.append([])
        yield dict(probes.READOUT_SETTINGS)

    fake_mthree = SimpleNamespace(M3Mitigation=m3_mitigation)
    circuits = [
        SimpleNamespace(
            layout=SimpleNamespace(final_index_layout=lambda q=list(q): list(q))
        )
        for q in probes.READOUT_LAYOUTS
    ]
    use_hardware = name in ("A", "B", "C_true")
    module = None if name.startswith("C") else fake_mthree
    error, returned = None, "none"
    try:
        out = fn(
            circuits,
            use_hardware=use_hardware,
            backend=backend,
            calibration_tracker=calibration_tracker,
            mthree_module=module,
        )
        if out is None:
            returned = "none"
        elif any(out is m for m in created):
            returned = "mitigator"
        else:
            returned = "other"
    except Exception as err:  # noqa: BLE001
        error = _describe(err)
    return {
        "name": name,
        "error": error,
        "returned": returned,
        "constructor_got_backend": [m.got_backend for m in created],
        "tracker_qubits": tracker_qubits,
        "cals_calls": [call for m in created for call in m.cals_calls],
    }


def _probe_corrected(fn: Callable[..., Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "error": None,
        "raw": {"M": [], "Mz2": []},
        "mitigated": {"M": [], "Mz2": []},
        "apply_correction_qubits": [],
    }
    physical = list(probes.CORRECTED_PHYSICAL)
    circuits = [
        SimpleNamespace(
            layout=SimpleNamespace(final_index_layout=lambda: list(physical))
        ),
        SimpleNamespace(layout=None),
    ]
    calls: list[list[int]] = []

    class Mitigator:
        def apply_correction(
            self, counts: object, qubits: object
        ) -> dict[int | str, float]:
            try:
                calls.append(_ints(qubits))
            except Exception:  # noqa: BLE001
                calls.append([])
            index = min(len(calls), len(probes.CORRECTED_QUASI)) - 1
            return dict(probes.CORRECTED_QUASI[index])

    try:
        for key, mitigator in (("raw", None), ("mitigated", Mitigator())):
            counts = [dict(c) for c in probes.CORRECTED_COUNTS]
            out = fn(counts, circuits, probes.probe_lattice(), mitigator)
            if not isinstance(out, (tuple, list)) or len(out) != 2:
                raise TypeError("corrected_mags must return the pair (M, Mz2)")
            record[key] = {"M": _floats(out[0]), "Mz2": _floats(out[1])}
    except Exception as err:  # noqa: BLE001
        record["error"] = _describe(err)
    record["apply_correction_qubits"] = calls
    return record


def _probe_folded_isa(fn: Callable[..., Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"error": None, "circuits": []}
    try:
        circuits = []
        for depth in probes.FOLD_DEPTHS:
            for scale in probes.FOLD_SCALES:
                out = fn(depth, scale, probes.probe_lattice(), probes.probe_groups())
                circuits.append(_as_circuit(out, f"folded_isa({depth}, {scale})"))
        record["circuits"] = circuits
    except Exception as err:  # noqa: BLE001
        record["error"] = _describe(err)
    return record


def _probe_zne_extrapolate(fn: Callable[..., Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"error": None, "intercepts": []}
    intercept = np.asarray(probes.ZNE_INTERCEPT)
    slope = np.asarray(probes.ZNE_SLOPE)
    try:
        intercepts = []
        for scales in probes.ZNE_SCALE_CALLS:
            per_scale = {s: intercept + s * slope for s in probes.FOLD_SCALES}
            out = fn(per_scale) if scales is None else fn(per_scale, tuple(scales))
            intercepts.append(_floats(out))
        record["intercepts"] = intercepts
    except Exception as err:  # noqa: BLE001
        record["error"] = _describe(err)
    return record


@typechecked
def grade_lab_floquet_ex2_2(
    make_readout_mitigator: Callable[..., Any],
    corrected_mags: Callable[..., Any],
    folded_isa: Callable[..., Any],
    zne_extrapolate: Callable[..., Any],
) -> None:
    """Submit your four first-mitigation functions (2.5 points each).

    ``make_readout_mitigator`` receives a fake mthree module and calibration tracker, so no
    calibration job is submitted. Each function is graded independently.
    """
    answer = {
        "make_readout_mitigator": {
            "probes": [
                _probe_mitigator(make_readout_mitigator, name)
                for name in probes.READOUT_PROBES
            ]
        },
        "corrected_mags": _probe_corrected(corrected_mags),
        "folded_isa": _probe_folded_isa(folded_isa),
        "zne_extrapolate": _probe_zne_extrapolate(zne_extrapolate),
    }
    _grade(answer, "ex2_2")


# --------------------------------------------------------------------------- #
# Part 3
# --------------------------------------------------------------------------- #


@typechecked
def grade_lab_floquet_ex3_1(normalize_inverse_rzz: Callable[..., Any]) -> None:
    """Submit your ``normalize_inverse_rzz(qc)`` function; it is applied to two probe circuits."""
    circuits = []
    for n_qubits, ops in probes.NORMALIZE_PROBES:
        try:
            out = normalize_inverse_rzz(probes.build_circuit(n_qubits, ops))
            circuits.append(
                _as_circuit(out, "the circuit normalize_inverse_rzz returned")
            )
        except Exception as err:  # noqa: BLE001
            _raise_from(
                err, "normalize_inverse_rzz", "It must return a new QuantumCircuit."
            )
    _grade({"circuits": circuits}, "ex3_1")


@typechecked
def grade_lab_floquet_ex3_2a(choose_layout: Callable[..., Any]) -> None:
    """Submit your ``choose_layout(backend, lattice, groups, limit)`` function.

    It is called on a 7-qubit fake fractional-RZZ backend whose couplings are the test lattice.
    """
    try:
        layout = _ints(
            choose_layout(
                probes.rzz_probe_backend(),
                probes.probe_lattice(),
                probes.probe_groups(),
                limit=probes.LAYOUT_LIMIT,
            )
        )
    except Exception as err:  # noqa: BLE001
        _raise_from(
            err,
            "choose_layout",
            "It must return a list of physical qubits, one per lattice site.",
        )
    _grade({"layout": layout}, "ex3_2a")


@typechecked
def grade_lab_floquet_ex3_2b(select_mapomatic_layout: Callable[..., Any]) -> None:
    """Submit your ``select_mapomatic_layout(qc, backend)`` function.

    It runs Mapomatic on a 4-qubit fake backend with known RZZ errors; no job is submitted.
    """
    n_qubits, ops = probes.MAPOMATIC_CIRCUIT
    try:
        out = select_mapomatic_layout(
            probes.build_circuit(n_qubits, ops), probes.MapomaticProbeBackend()
        )
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            raise TypeError(
                "select_mapomatic_layout must return (layout, estimated_error)"
            )
        answer = {"layout": _ints(out[0]), "error": float(out[1])}
    except Exception as err:  # noqa: BLE001
        _raise_from(
            err, "select_mapomatic_layout", "It must return (layout, estimated_error)."
        )
    _grade(answer, "ex3_2b")


_OPTION_PATHS: dict[str, tuple[str, ...]] = {
    "max_execution_time": ("max_execution_time",),
    "default_shots": ("default_shots",),
    "resilience_level": ("resilience_level",),
    "measure_mitigation": ("resilience", "measure_mitigation"),
    "zne_mitigation": ("resilience", "zne_mitigation"),
    "measure_noise_learning_randomizations": (
        "resilience",
        "measure_noise_learning",
        "num_randomizations",
    ),
    "twirling_enable_measure": ("twirling", "enable_measure"),
    "twirling_enable_gates": ("twirling", "enable_gates"),
    "twirling_randomizations": ("twirling", "num_randomizations"),
    "twirling_strategy": ("twirling", "strategy"),
    "twirling_shots_per_randomization": ("twirling", "shots_per_randomization"),
    "dynamical_decoupling": ("dynamical_decoupling", "enable"),
}


def _option(options: object, path: tuple[str, ...]) -> bool | int | float | str | None:
    value = options
    for attr in path:
        value = getattr(value, attr, None)
        if value is None:
            return None
    if isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else repr(value)
    return repr(value)


@typechecked
def grade_lab_floquet_ex3_3a(
    build_estimator: Callable[..., Any],
    *,
    shots: int,
    randomizations: int,
    cal_randomizations: int,
) -> None:
    """Submit your ``build_estimator(backend, allowance)`` and the notebook's settings.

    Pass ``shots=SHOTS_NEW``, ``randomizations=RANDOMIZATIONS`` and
    ``cal_randomizations=TREX_CAL_RANDOMIZATIONS``. The Estimator is built on a fake backend
    and never run.
    """
    try:
        estimator = build_estimator(
            probes.rzz_probe_backend(), allowance=probes.ESTIMATOR_ALLOWANCE
        )
    except Exception as err:  # noqa: BLE001
        _raise_from(
            err,
            "build_estimator",
            "It must return a configured Estimator without submitting a job.",
        )
    options = getattr(estimator, "options", None)
    answer = {
        "estimator_module": str(type(estimator).__module__),
        "estimator_class": str(type(estimator).__qualname__),
        "options": {
            name: _option(options, path) for name, path in _OPTION_PATHS.items()
        },
        "declared": {
            "shots": shots,
            "randomizations": randomizations,
            "cal_randomizations": cal_randomizations,
        },
    }
    _grade(answer, "ex3_3a")


@typechecked
def grade_lab_floquet_ex3_3b(make_observables: Callable[..., Any]) -> None:
    """Submit your ``make_observables(lattice)`` function; it must return ``[M, Mz2]``."""
    try:
        out = make_observables(probes.probe_lattice())
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            raise TypeError("make_observables must return [M, Mz2]")
        if not all(isinstance(op, SparsePauliOp) for op in out):
            raise TypeError("both observables must be SparsePauliOp")
    except Exception as err:  # noqa: BLE001
        _raise_from(err, "make_observables", "Return [M, Mz2] as two SparsePauliOp.")
    _grade({"M": out[0], "Mz2": out[1]}, "ex3_3b")


# --------------------------------------------------------------------------- #
# Part 4
# --------------------------------------------------------------------------- #


@typechecked
def grade_lab_floquet_ex4_1(fold_cycles: Callable[..., Any]) -> None:
    """Submit your ``fold_cycles(depth, lattice, groups, factor)`` function."""
    circuits = []
    for depth in probes.FOLD_DEPTHS:
        for factor in probes.FOLD_SCALES:
            try:
                out = fold_cycles(
                    depth, probes.probe_lattice(), probes.probe_groups(), factor
                )
                circuits.append(
                    _as_circuit(out, f"fold_cycles({depth}, ..., {factor})")
                )
            except Exception as err:  # noqa: BLE001
                _raise_from(
                    err, "fold_cycles", "It must return an unmeasured QuantumCircuit."
                )
    _grade({"circuits": circuits}, "ex4_1")


class _ProbeFailure(Exception):
    """Raised by a fake when a participant calls something they should not."""


def _probe_measure(fn: Callable[..., Any], name: str) -> dict[str, Any]:
    backend = probes.rzz_probe_backend()
    built: list[bool] = []
    submitted: list[list[Any]] = []
    charged: list[float] = []
    run_calls = [0]
    bad_pubs: list[str] = []

    class FakeJob:
        def __init__(self, n_pubs: int) -> None:
            self.n_pubs = n_pubs

        def result(self) -> list[SimpleNamespace]:
            n = self.n_pubs - 1 if name == "short_result" else self.n_pubs
            return [
                SimpleNamespace(
                    data=SimpleNamespace(
                        evs=np.asarray([100 * i + 1, 100 * i + 2], dtype=float),
                        stds=np.asarray([0.01 * (i + 1), 0.02 * (i + 1)]),
                    )
                )
                for i in range(n)
            ]

        def metrics(self) -> dict[str, Any]:
            return (
                {}
                if name == "no_metrics"
                else {"usage": {"qpu_charge_time_seconds": probes.MEASURE_CHARGE}}
            )

        def job_id(self) -> str:
            return probes.MEASURE_JOB_ID

    class FakeEstimator:
        def run(self, pubs: object, dry_run: bool = False) -> FakeJob:
            pubs = list(pubs)  # ty: ignore[invalid-argument-type] - participant data
            submitted.append(pubs)
            return FakeJob(len(pubs))

    def build_estimator(
        target: object, *args: object, **kwargs: object
    ) -> FakeEstimator:
        built.append(target is backend)
        return FakeEstimator()

    def run_program(
        key: object, *args: object, submit: Callable[[], Any], **kwargs: object
    ) -> Any:
        run_calls[0] += 1
        return submit()

    def charge_qpu_time(
        key: object,
        *args: object,
        job_id: object = None,
        qpu_seconds: object = 0.0,
        **kwargs: object,
    ) -> float:
        charged.append(float(qpu_seconds))  # ty: ignore[invalid-argument-type] - recorded as sent
        return float(sum(charged))

    def job(*args: object, **kwargs: object) -> None:
        raise _ProbeFailure(
            "the grader's fake service has no stored jobs; submit through run_program"
        )

    cycles: list[int] = [] if name == "empty_cycles" else list(probes.MEASURE_CYCLES)
    factors: tuple[int, ...] = (
        () if name == "empty_factors" else tuple(probes.MEASURE_FACTORS)
    )
    error, run = None, None
    try:
        out = fn(
            probes.probe_lattice(),
            probes.probe_groups(),
            backend,
            list(probes.MEASURE_LAYOUT),
            cycles=cycles,
            factors=factors,
            use_hardware=name != "no_hardware",
            service=SimpleNamespace(job=job),
            build_estimator=build_estimator,
            run_program=run_program,
            charge_qpu_time=charge_qpu_time,
        )
        run = _reduce_run(out)
    except _BadReturn as err:
        error = f"BadReturn: {err}"[:_MAX_ERROR_TEXT]
    except Exception as err:  # noqa: BLE001
        error = _describe(err)

    circuits: list[QuantumCircuit] = []
    observables: list[list[SparsePauliOp]] = []
    if (
        name == "main"
    ):  # only the main probe's PUBs are judged; error probes by calls and charges
        for pubs in submitted:
            for pub in pubs:
                try:
                    circuit, ops = pub
                    ops = list(ops)
                    if not all(isinstance(op, SparsePauliOp) for op in ops):
                        raise TypeError("observables must be SparsePauliOp")
                    circuits.append(_as_circuit(circuit, "a PUB circuit"))
                    observables.append(ops)
                except Exception as err:  # noqa: BLE001
                    bad_pubs.append(_describe(err))
        if bad_pubs and error is None:
            error = f"BadPub: each PUB must be (isa_circuit, [M, Mz2]); {bad_pubs[0]}"[
                :_MAX_ERROR_TEXT
            ]
    return {
        "name": name,
        "error": error,
        "estimator_got_backend": built,
        "run_program_calls": run_calls[0],
        "charged": charged,
        "circuits": circuits,
        "observables": observables,
        "run": run,
    }


class _BadReturn(Exception):
    pass


def _matrix(values: object) -> list[list[float]]:
    array = np.atleast_2d(np.asarray(values, dtype=float))
    if array.ndim != 2:
        raise _BadReturn(
            f"values and stds must be (cycles, factors) arrays, got shape {array.shape}"
        )
    return array.tolist()


# `out` is Any, not object: ty 0.0.30 (the client's pin) cannot subscript the narrowed dict.
def _reduce_run(out: Any) -> dict[str, Any]:
    if not isinstance(out, dict):
        raise _BadReturn(
            f"measure_cycle_folded must return a dict, got {type(out).__name__}"
        )
    for key in (
        "cycles",
        "factors",
        "pub_order",
        "values",
        "stds",
        "job_id",
        "qpu_seconds",
        "provenance",
    ):
        if key not in out:
            raise _BadReturn(f"missing key '{key}'")
    try:
        values, stds = out["values"], out["stds"]
        return {
            "cycles": _ints(np.asarray(out["cycles"]).ravel()),
            "factors": _ints(np.asarray(out["factors"]).ravel()),
            "pub_order": [_ints(pair) for pair in out["pub_order"]],
            "M": _matrix(values["M"]),
            "Mz2": _matrix(values["Mz2"]),
            "M_std": _matrix(stds["M"]),
            "Mz2_std": _matrix(stds["Mz2"]),
            "job_id": str(out["job_id"]),
            "qpu_seconds": float(out["qpu_seconds"]),
            "provenance": str(out["provenance"]),
        }
    except (KeyError, TypeError, ValueError) as err:
        raise _BadReturn(_describe(err)) from err


@typechecked
def grade_lab_floquet_ex4_2(measure_cycle_folded: Callable[..., Any]) -> None:
    """Submit your ``measure_cycle_folded`` function (the unbound one, not ``measure``).

    It is called with a fake backend, Estimator, job runner and ledger, so no job is submitted
    and no QPU time is charged.
    """
    answer = {
        "probes": [
            _probe_measure(measure_cycle_folded, name) for name in probes.MEASURE_PROBES
        ]
    }
    _grade(answer, "ex4_2")


def _zne_run(kind: str, cycles: tuple[int, ...] = probes.ZNE_CYCLES) -> dict[str, Any]:
    factors = np.asarray(probes.ZNE_FACTORS, dtype=float)
    if kind == "linear":
        intercept, slope = (
            np.asarray(probes.ZNE_LINEAR[k]) for k in ("intercept", "slope")
        )
        values = intercept[:, None] + slope[:, None] * factors
    elif kind == "quadratic":
        intercept, slope, curvature = (
            np.asarray(probes.ZNE_QUADRATIC[k])
            for k in ("intercept", "slope", "curvature")
        )
        values = (
            intercept[:, None]
            + slope[:, None] * factors
            + curvature[:, None] * factors**2
        )
    else:
        intercept, rate = (
            np.asarray(probes.ZNE_EXPONENTIAL[k]) for k in ("intercept", "rate")
        )
        values = intercept[:, None] * np.exp(-rate[:, None] * factors)
    return {
        "cycles": np.asarray(cycles),
        "factors": tuple(probes.ZNE_FACTORS),
        "values": {"M": values, "Mz2": values * probes.ZNE_MZ2_SCALE},
        "stds": {
            "M": np.full_like(values, probes.ZNE_STD),
            "Mz2": np.full_like(values, probes.ZNE_STD),
        },
    }


def _record(name: str, call: Callable[[], Any]) -> dict[str, Any]:
    try:
        with warnings.catch_warnings(), np.errstate(all="ignore"):
            warnings.simplefilter("ignore")
            return {"name": name, "value": _floats(call()), "error": None}
    except Exception as err:  # noqa: BLE001
        return {"name": name, "value": None, "error": _describe(err)}


@typechecked
def grade_lab_floquet_ex4_3a(_qmit_zne: Callable[..., Any]) -> None:
    """Submit your ``_qmit_zne(run, chosen_factors, observable, model, custom_fit_factory)``."""

    def run() -> dict[str, Any]:
        out = _zne_run("linear", probes.QMIT_CYCLES)
        out["stds"]["Mz2"] = np.asarray(probes.QMIT_MZ2_STDS)
        return out

    def linear_factory(
        x: np.ndarray, y: np.ndarray
    ) -> tuple[Callable[..., Any], list[float], Any]:
        return (
            (lambda f, a, b: a + b * f),
            [0.5, 0.0],
            ([-np.inf, -np.inf], [np.inf, np.inf]),
        )

    def nan_factory(
        x: np.ndarray, y: np.ndarray
    ) -> tuple[Callable[..., Any], list[float], Any]:
        return (lambda f, a: a * f / f), [0.5], ([-np.inf], [np.inf])

    def broken() -> dict[str, Any]:
        out = run()
        out["values"]["M"] = out["values"]["M"].copy()
        out["values"]["M"][0, 0] = np.nan
        return out

    calls: dict[str, Callable[[], Any]] = {
        "P1": lambda: _qmit_zne(run(), (5, 1), "M", "linear"),
        "P2": lambda: _qmit_zne(run(), (1, 3, 5), "Mz2", "linear"),
        "P3": lambda: _qmit_zne(run(), (1, 3, 5), "M", "custom", linear_factory),
        "P4": lambda: _qmit_zne(run(), (1, 7), "M", "linear"),
        "P5": lambda: _qmit_zne(run(), (1, 1), "M", "linear"),
        "P6": lambda: _qmit_zne(broken(), (1, 3), "M", "linear"),
        "P7": lambda: _qmit_zne(run(), (1, 3, 5), "M", "custom", nan_factory),
    }
    _grade(
        {"probes": [_record(name, calls[name]) for name in probes.QMIT_PROBES]},
        "ex4_3a",
    )


def _grade_extrapolator(fn: Callable[..., Any], method: str, exercise: str) -> None:
    kind = probes.EXTRAPOLATOR_FIXTURE[method]
    chosen = tuple(probes.EXTRAPOLATOR_CHOSEN[method])
    records = [
        _record("M", lambda: fn(_zne_run(kind), chosen_factors=chosen, observable="M")),
        _record(
            "Mz2", lambda: fn(_zne_run(kind), chosen_factors=chosen, observable="Mz2")
        ),
        _record(
            "missing_factor",
            lambda: fn(
                _zne_run(kind),
                chosen_factors=tuple(probes.MISSING_FACTORS),
                observable="M",
            ),
        ),
    ]
    _grade({"probes": records}, exercise)


@typechecked
def grade_lab_floquet_ex4_3b(zne_linear_extrapolator: Callable[..., Any]) -> None:
    """Submit your ``zne_linear_extrapolator(run21, chosen_factors, observable)``."""
    _grade_extrapolator(zne_linear_extrapolator, "linear", "ex4_3b")


@typechecked
def grade_lab_floquet_ex4_3c(zne_richardson_extrapolator: Callable[..., Any]) -> None:
    """Submit your ``zne_richardson_extrapolator(run21, chosen_factors, observable)``."""
    _grade_extrapolator(zne_richardson_extrapolator, "richardson", "ex4_3c")


@typechecked
def grade_lab_floquet_ex4_3d(zne_exponential_extrapolator: Callable[..., Any]) -> None:
    """Submit your ``zne_exponential_extrapolator(run21, chosen_factors, observable, rate_bounds)``."""
    _grade_extrapolator(zne_exponential_extrapolator, "exponential", "ex4_3d")


@typechecked
def grade_lab_floquet_ex4_3e(select_zne_model: Callable[..., Any]) -> None:
    """Submit your ``select_zne_model(run21, reference_trace)``; it must return ``(factors, method)``."""
    target = np.asarray(probes.SELECT_TARGET)
    values = target[:, None] + np.asarray(probes.SELECT_DEVIATIONS)[None, :]
    run = {
        "cycles": np.asarray(probes.ZNE_CYCLES),
        "factors": tuple(probes.ZNE_FACTORS),
        "values": {"M": values, "Mz2": values * probes.SELECT_MZ2_SCALE},
        "stds": {
            "M": np.full_like(values, probes.ZNE_STD),
            "Mz2": np.full_like(values, probes.ZNE_STD),
        },
    }
    try:
        with warnings.catch_warnings(), np.errstate(all="ignore"):
            warnings.simplefilter("ignore")
            out = select_zne_model(run, np.r_[1.0, target])
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            raise TypeError("select_zne_model must return (factors, method)")
        answer = {"factors": _ints(out[0]), "method": str(out[1])}
    except Exception as err:  # noqa: BLE001
        _raise_from(err, "select_zne_model", "It must return (factors, method_name).")
    _grade(answer, "ex4_3e")


# --------------------------------------------------------------------------- #
# Part 5
# --------------------------------------------------------------------------- #


def _probe_extension(
    fn: Callable[..., Any],
    lattice: object,
    probe: tuple[str, bool, bool, tuple[int, ...]],
) -> dict[str, Any]:
    name, use_hardware, include_baseline, factors = probe
    baseline = {"layout": list(range(21))} if include_baseline else None
    backend, ledger = object(), Path(probes.EXTENSION_LEDGER)
    cycles = np.asarray(probes.EXTENSION_CYCLES)
    calls: list[dict[str, Any]] = []
    searches: list[tuple[Any, Any, Any]] = []
    measurements: list[tuple[Any, Any, Any, Any]] = []
    returned: dict[int, dict[str, Any]] = {}

    def guard(what: str) -> None:
        if not use_hardware:
            raise AssertionError(f"local track {what}")

    def lookup(
        key: object, *, backend_name: object, ledger_path: object
    ) -> dict[str, Any] | None:
        guard("accessed the ledger")
        calls.append(
            {
                "callback": "saved_run_settings",
                "n_qubits": None,
                "args": {
                    "key": str(key),
                    "backend_name": str(backend_name),
                    "ledger_path": str(ledger_path),
                },
            }
        )
        return (
            {"layout": list(probes.EXTENSION_SAVED_LAYOUT)}
            if key == probes.EXTENSION_SAVED_KEY
            else None
        )

    def search(lat: Any, groups: Any, target: object) -> list[int]:
        guard("searched hardware layouts")
        calls.append(
            {"callback": "mapomatic_layout", "n_qubits": int(lat.n_qubits), "args": {}}
        )
        searches.append((lat, groups, target))
        return list(
            range(
                probes.EXTENSION_SEARCH_START,
                probes.EXTENSION_SEARCH_START + lat.n_qubits,
            )
        )

    def measure(
        lat: Any, groups: Any, target: object, layout: Any, *, cycles: Any, factors: Any
    ) -> dict[str, Any]:
        guard("measured circuits")
        calls.append(
            {
                "callback": "measure_cycle_folded",
                "n_qubits": int(lat.n_qubits),
                "args": {
                    "cycles": _ints(np.asarray(cycles).ravel()),
                    "factors": _ints(factors),
                },
            }
        )
        measurements.append((lat, groups, target, list(layout)))
        run = {
            "n_qubits": lat.n_qubits,
            "layout": list(layout),
            "qpu_seconds": probes.EXTENSION_RUN_SECONDS,
            "pub_order": [(int(c), f) for c in cycles for f in factors],
        }
        returned[int(lat.n_qubits)] = run
        return run

    def spent(path: object) -> float:
        guard("read QPU charges")
        calls.append(
            {
                "callback": "qpu_time_spent",
                "n_qubits": None,
                "args": {"ledger_path": str(path)},
            }
        )
        return probes.EXTENSION_SPENT_SECONDS

    record: dict[str, Any] = {
        "probe": name,
        "error": None,
        "lattices": [],
        "layouts": [],
        "run_sizes": [],
        "qpu_seconds": None,
        "calls": calls,
        "flags": {},
    }
    try:
        result = fn(
            lattice,
            baseline,
            cycles=cycles,
            selected_factors=factors,
            use_hardware=use_hardware,
            backend=backend,
            backend_name=probes.EXTENSION_BACKEND_NAME,
            ledger_path=ledger,
            saved_run_settings=lookup,
            mapomatic_layout=search,
            measure_cycle_folded=measure,
            qpu_time_spent=spent,
        )
        if not isinstance(result, dict):
            raise TypeError(
                f"extend_sizes must return a dict, got {type(result).__name__}"
            )
        lattices, groups = result["lattices_by_size"], result["groups_by_size"]
        runs, layouts = result["runs_by_size"], result["layout_by_size"]
        record["lattices"] = [
            {
                "n_qubits": int(size),
                "edges": _edges(lat.edges),
                "groups": _groups(groups.get(size, [])),
            }
            for size, lat in lattices.items()
        ]
        record["layouts"] = [
            {"n_qubits": int(size), "layout": _ints(lay)}
            for size, lay in layouts.items()
        ]
        record["run_sizes"] = sorted(int(size) for size in runs)
        record["qpu_seconds"] = float(result["qpu_seconds"])
        record["flags"] = {
            "sizes_match": set(lattices) == set(groups)
            and all(int(lat.n_qubits) == int(size) for size, lat in lattices.items()),
            "lattice21_kept": lattices.get(21) is lattice,
            "baseline_kept": baseline is not None and runs.get(21) is baseline,
            "search_got_patch": all(
                lat is lattices.get(lat.n_qubits) and grp == groups.get(lat.n_qubits)
                for lat, grp, _ in searches
            ),
            "measure_got_patch": all(
                lat is lattices.get(lat.n_qubits)
                and grp == groups.get(lat.n_qubits)
                and lay == list(layouts.get(lat.n_qubits, []))
                for lat, grp, _, lay in measurements
            ),
            "got_probe_backend": all(t is backend for _, _, t in searches)
            and all(t is backend for _, _, t, _ in measurements),
            "runs_kept": all(runs.get(size) is run for size, run in returned.items()),
        }
    except Exception as err:  # noqa: BLE001
        record["error"] = _describe(err)
    return record


@typechecked
def grade_lab_floquet_ex5_1(extend_sizes: Callable[..., Any], lattice: object) -> None:
    """Submit your ``extend_sizes`` function and the notebook's 21-qubit ``lattice``.

    It is called with recording fakes for the ledger, layout search, measurement and QPU
    accounting, so no job is submitted.
    """
    answer = {
        "runs": [
            _probe_extension(extend_sizes, lattice, probe)
            for probe in probes.EXTENSION_PROBES
        ]
    }
    _grade(answer, "ex5_1")


@typechecked
def grade_lab_floquet_ex5_2(
    value: float | np.floating | None, error_bar: float | np.floating | None
) -> None:
    """Submit your 74-qubit estimate ``MZ2_74`` of M_z2 at cycle 18 and its error bar ``MZ2_74_ERROR``.

    Any method is allowed. Only the two numbers are sent, so the result is self-reported.
    """
    if value is None or error_bar is None:
        raise ValueError(
            "Set MZ2_74 and MZ2_74_ERROR from your 74-qubit run before grading."
        )
    value, error_bar = float(value), float(error_bar)
    if not math.isfinite(value):
        raise ValueError(
            f"MZ2_74 is {value}; report the finite M_z2(18) estimate of your 74-qubit run."
        )
    if not math.isfinite(error_bar) or error_bar <= 0:
        raise ValueError(
            f"MZ2_74_ERROR is {error_bar}; report a positive one-standard-deviation error bar "
            "(for example the extrapolation's standard error)."
        )
    _grade({"value": value, "error_bar": error_bar}, "ex5_2")
