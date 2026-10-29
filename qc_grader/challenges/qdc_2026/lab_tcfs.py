"""QDC 2026, "Trade Circuits for Shots" (lab ``lab_tcfs``): the grading functions.

One ``grade_lab_tcfs_<ex>`` function per exercise of the notebook. Each function packs the
notebook variables it receives into one JSON-serialisable answer and sends it with
``grade_answer``; the server validator of the same exercise grades it.

- Functions that a participant wrote (``basis_circuit``, ``fourier_lcu``,
  ``evaluate_counts``, ``cvar``, ``my_score``) are called here, on the participant's
  machine, at fixed probe inputs; only their outputs are sent.
- A hardware job is reduced to plain data: its job id, backend name, QPU usage, number of
  shots and a seeded sample of its shots. These numbers are self-reported: the server cannot
  reach IBM Quantum, and the organizers may audit the job ids after the event.

The section "Shared definitions" holds the constants and generators that the server module
``validations/qdc_2026/lab_tcfs.py`` defines identically. The server uses its own copy and
never trusts probe values echoed in an answer.

Ids (proposed until the maintainer confirms them): challenge ``qdc_2026``, lab ``lab_tcfs``,
exercises ``ex1a ex1b ex1c ex1d ex2a ex2b ex2c ex2d ex2e ex3d ex3l ex3t``.
"""

# The client contract raises ValueError, with the fix first, for every bad input, type
# problems included (spec section 4.2), so ruff's TypeError preference does not apply.
# ruff: noqa: TRY004

import hashlib
import inspect
import json
import math
from collections.abc import Callable, Mapping, Sequence
from types import SimpleNamespace
from typing import Any, Protocol, TypedDict, cast

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterExpression
from qiskit.primitives import BasePrimitiveJob
from qiskit.providers import BackendV2
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"  # the id the maintainer assigns; identical on the server
_LAB = "lab_tcfs"  # the lab id; identical on the server


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


# ------------------------------------------------------------------------------------------
# Shared definitions (identical in the server module; the server uses its own copy)
# ------------------------------------------------------------------------------------------
ALPHA = 0.10  # the CVaR level of every score
SAMPLE_SHOTS = 4096  # shots in the sample of a job
SAMPLE_SEED = 2026  # seed of every sample the client draws
SWEEP_SAMPLE_SHOTS = 512  # shots per setting in the samples of Exercise 2c
MAX_SWEEP_SETTINGS = 16  # settings of one Exercise 2c sweep (payload under 1 MB)
MAX_NODES = 160  # widest instance and widest circuit the grader accepts

# The 12-node training instance of Part 1 (the paper's instance: the 3-regular graph
# networkx.random_regular_graph(3, 12, seed=42), k = 4, unit weights, lam = 4).
TRAIN12_N = 12
TRAIN12_K = 4
TRAIN12_LAM = 4.0
TRAIN12_EDGES = (
    (0, 6, 1.0), (0, 9, 1.0), (0, 10, 1.0), (1, 6, 1.0), (1, 7, 1.0), (1, 11, 1.0),
    (2, 4, 1.0), (2, 9, 1.0), (2, 10, 1.0), (3, 5, 1.0), (3, 8, 1.0), (3, 11, 1.0),
    (4, 6, 1.0), (4, 11, 1.0), (5, 8, 1.0), (5, 9, 1.0), (7, 8, 1.0), (7, 10, 1.0),
)  # fmt: skip

# The 7-node instance of Exercises 1b and 1d (no symmetry, lam = 5, an edge of weight 2):
# code that fixes n, k, lam or the weights to the training instance's values fails on it.
SMALL7_N = 7
SMALL7_K = 3
SMALL7_LAM = 5.0
SMALL7_EDGES = (
    (0, 1, 1.0), (0, 2, 1.0), (0, 3, 1.0), (0, 4, 1.0), (1, 2, 2.0), (2, 3, 1.0), (4, 5, 1.0),
)  # fmt: skip

# Exercise 1b: fourier_lcu is called at these (instance, gamma), in this order.
PROBES_1B = (("train12", 0.37), ("train12", 0.9), ("train12", 1.63), ("small7", 0.9))

# Exercise 1d: evaluate_counts on seeded synthetic counts of both instances, cvar on
# fixed cases (ports of tcfs.checks._random_counts, _cvar_cases and _confirm_cases).
SEED_1D_TRAIN, SIZE_1D_TRAIN = 2026, 60
SEED_1D_SMALL, SIZE_1D_SMALL = 7, 40
SEED_1D_CVAR, N_CVAR_RANDOM_1D = 1729, 40
SEED_1D_CONFIRM, N_CVAR_CONFIRM_1D = 4242, 5

# Exercise 2a: three probe counts dictionaries per (n, k)
# (port of tcfs.checks._reference_counts_2a with the seed below).
SEED_2A = 2026
SIZE_2A = 1500
SHAPES_2A = ((0.0, 2.0), (3.0, 3.0), (-1.5, 1.5))  # (mean weight - k, sd of the weight)
ALPHA_2A = 0.25

# Exercise 2d: the QPU-time model of one Sampler job (event.job_usage_estimate, fitted
# to the R1 jobs on ibm_phoenix, 2026-09-30) and the planning budget.
USAGE_PER_JOB_S = 2.9
USAGE_PER_EXECUTION_S = 14.2e-6
USAGE_PER_CIRCUIT_S = 0.083
BUDGET_S = 1800.0


def theta_init(n: int, k: int) -> float:
    """Warm-start angle 2 arcsin(sqrt(k / n))."""
    return 2.0 * math.asin(math.sqrt(k / n))


def _random_counts(n: int, k: int, size: int, seed: int) -> dict[str, int]:
    """``size`` distinct n-bit strings (bit density k / n) with counts 1..40, seeded
    (exact port of ``tcfs.checks._random_counts``)."""
    rng = np.random.default_rng(seed)
    keys: list[str] = []
    while len(keys) < size:
        bits = (rng.random(n) < k / n).astype(int)
        key = "".join(str(b) for b in bits[::-1])
        if key not in keys:
            keys.append(key)
    return {key: int(c) for key, c in zip(keys, rng.integers(1, 41, size))}


def probe_counts_1d() -> list[tuple[str, dict[str, int]]]:
    """The synthetic counts of Exercise 1d: 60 keys on the training instance, then 40 on
    the 7-node instance. ``values``, ``feasible`` and ``shots`` of the answer concatenate
    evaluate_counts on both, in this order."""
    return [
        ("train12", _random_counts(TRAIN12_N, TRAIN12_K, SIZE_1D_TRAIN, SEED_1D_TRAIN)),
        ("small7", _random_counts(SMALL7_N, SMALL7_K, SIZE_1D_SMALL, SEED_1D_SMALL)),
    ]


def probe_cases_1d() -> list[tuple[list[float], list[float], float]]:
    """The 48 ``(values, weights, alpha)`` cases of Exercise 1d, in order: three fixed
    cases, 40 seeded cases with ties and weights of different scales, and 5 seeded cases
    without ties."""
    cases: list[tuple[list[float], list[float], float]] = [
        ([1.0, 2.0], [1.0, 3.0], 0.5),
        ([1.0, 2.0], [1.0, 3.0], 0.8),
        ([3.0, 1.0, 2.0], [1.0, 1.0, 2.0], 1.0),
    ]
    rng = np.random.default_rng(SEED_1D_CVAR)
    for _ in range(N_CVAR_RANDOM_1D):
        m = int(rng.integers(2, 30))
        v = rng.integers(-20, 8, m).astype(float)
        w = rng.exponential(1.0, m) * float(rng.choice([1.0, 7.0, 1000.0]))
        cases.append(
            (v.tolist(), w.tolist(), float(np.round(rng.uniform(0.03, 0.9), 4)))
        )
    rng = np.random.default_rng(SEED_1D_CONFIRM)
    for _ in range(N_CVAR_CONFIRM_1D):
        m = int(rng.integers(4, 25))
        v = np.round(rng.normal(0.0, 5.0, m), 6)
        w = rng.exponential(1.0, m) * float(rng.choice([1.0, 7.0, 1000.0]))
        cases.append(
            (v.tolist(), w.tolist(), float(np.round(rng.uniform(0.05, 0.9), 4)))
        )
    return cases


def seed_2a(n: int, k: int) -> int:
    """Seed of the Exercise 2a probes: SEED_2A + the first 8 hex digits of
    sha256(f"{n},{k}") read as an integer."""
    return SEED_2A + int(hashlib.sha256(f"{n},{k}".encode()).hexdigest()[:8], 16)


def probe_digest(probes: object) -> str:
    """First 16 hex digits of sha256 of the probes as compact JSON (insertion order);
    both test suites assert the digests of the probes."""
    body = json.dumps(probes, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def probe_counts_2a(n: int, k: int) -> list[dict[str, int]]:
    """The three probe counts dictionaries of Exercise 2a for an instance (n, k).

    n-bit strings with Hamming weights drawn around k (``SHAPES_2A``), ``SIZE_2A``
    distinct strings each (fewer on a small instance), 1 to 6 shots each. Port of
    ``tcfs.checks._reference_counts_2a`` with the seed of :func:`seed_2a`.
    """
    rng = np.random.default_rng(seed_2a(n, k))
    size = min(SIZE_2A, 2 ** min(n, 30) // 4)
    out: list[dict[str, int]] = []
    for offset, sd in SHAPES_2A:
        counts: dict[str, int] = {}
        for _ in range(50 * size):
            if len(counts) >= size:
                break
            w = int(np.clip(np.rint(rng.normal(k + offset, sd)), 0, n))
            bits = np.zeros(n, dtype=np.uint8)
            bits[rng.choice(n, w, replace=False)] = 1
            key = "".join("1" if b else "0" for b in bits[::-1])
            if key not in counts:
                counts[key] = int(rng.integers(1, 7))
        out.append(counts)
    return out


def fourier_weights(n: int, k: int, lam: float, gamma: float) -> np.ndarray:
    """Branch probabilities q_b = |c_b| / sum_b |c_b| of the Fourier LCU of the penalty.

    c_b = (1 / (n+1)) sum_W exp(i gamma lam (W - k)^2) exp(-i theta_b W), theta_b =
    2 pi b / (n+1), b = 0..n (``tcfs.exact.penalty_lcu_coefficients``).
    """
    w = np.arange(n + 1)
    u = np.exp(1j * (float(gamma) * float(lam) * (w - k) ** 2))
    c = np.fft.fft(u) / (n + 1)
    a = np.abs(c)
    return a / a.sum()


def job_usage_estimate(circuits: int, shots: int) -> float:
    """Estimated QPU seconds of one Sampler job of ``circuits`` circuits (or parameter
    sets) with ``shots`` shots each (``event.job_usage_estimate``)."""
    return float(
        USAGE_PER_JOB_S
        + USAGE_PER_EXECUTION_S * int(circuits) * int(shots)
        + USAGE_PER_CIRCUIT_S * int(circuits)
    )


# ------------------------------------------------------------------------------------------
# Types of the notebook objects
# ------------------------------------------------------------------------------------------
class ProblemInstance(Protocol):
    """What the grading functions read from an instance. The kit's instances provide it:
    ``inst``, the training instance of Part 1, and ``inst106``, your instance of Part 2."""

    n: int
    k: int
    edges: Sequence[Sequence[float]]
    lam: float


Angle = float | np.floating | ParameterExpression
Layers = Sequence[Sequence[Angle]]


class _FrontierArmRequired(TypedDict):
    job: BasePrimitiveJob
    layers: Layers


class FrontierArm(_FrontierArmRequired, total=False):
    """One side of a Part 3 experiment: ``{"job": job, "layers": [(gamma, theta, beta),
    ...], "lcu": None or {"kind": "penalty", "gamma": g}}``."""

    lcu: Mapping[str, object] | None


# ------------------------------------------------------------------------------------------
# Helpers: participant code and values
# ------------------------------------------------------------------------------------------
_TOL_REAL = 1e-5  # imaginary parts below this count as rounding (float32 answers)
_MAX_CIRCUIT_OPS = 20_000
_MAX_PLAN_ROWS = 1000
_MAX_TEXT = 10_000
_NOTE_CHARS = 200
_MAX_SETS_1D = (
    16  # parameter sets of the practice job the client sends (13 + 1 expected)
)


def _call(label: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call participant code; an exception becomes a ValueError that names the call."""
    try:
        return fn(*args, **kwargs)
    except NotImplementedError as err:
        raise ValueError(
            f"{label} is not implemented yet (it raises NotImplementedError): fill in the "
            "region between '### your code' and '###', run that cell, then grade again."
        ) from err
    except Exception as err:
        hint = ""
        if isinstance(err, AttributeError) and "7-node" in label:
            hint = (
                " The grader's 7-node instance has only the fields n, k, lam, edges and "
                "theta_init; read those in your function, not the kit's helper methods."
            )
        raise ValueError(
            f"{label} raised {type(err).__name__}: {err}. The grader calls your function "
            "here, on fixed test inputs: fix the error shown in the traceback above, then "
            f"grade again.{hint}"
        ) from err


def _kind(x: object) -> str:
    """A short description of a value for a message."""
    if x is None:
        return "None"
    if isinstance(x, np.ndarray):
        return f"an array of shape {x.shape}"
    if isinstance(x, (list, tuple)):
        return f"a {type(x).__name__} of {len(x)} values"
    name = type(x).__name__
    return f"{'an' if name[:1].lower() in 'aeiou' else 'a'} {name}"


def _real(x: object) -> float | None:
    """``x`` as a float when it is one real number (a Python or NumPy scalar, a
    one-element array, a complex number with zero imaginary part), else None. Booleans,
    strings and symbolic parameters are not numbers."""
    if x is None or isinstance(x, (bool, np.bool_, str, bytes, ParameterExpression)):
        return None
    try:
        arr = np.asarray(x)
    except Exception:  # noqa: BLE001 - any participant object
        return None
    if arr.size != 1 or arr.dtype.kind not in "iufc":
        return None
    v = arr.reshape(-1)[0]
    if arr.dtype.kind == "c":
        if abs(v.imag) > _TOL_REAL * max(1.0, abs(v.real)):
            return None
        v = v.real
    return float(v)


def _numbers(x: object, name: str, where: str) -> np.ndarray:
    """``x`` as a flat array of numbers (bool, int, float or complex)."""
    if x is None or isinstance(x, (str, bytes, Mapping)):
        raise ValueError(
            f"{name} must be an array or list of numbers ({where}), got {_kind(x)}."
        )
    try:
        arr = np.asarray(x)
        if arr.dtype == object:
            arr = arr.astype(complex)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"{name} must hold numbers only ({where}), got {_kind(x)}."
        ) from err
    if arr.dtype.kind not in "biufc":
        raise ValueError(f"{name} must hold numbers only ({where}), got {_kind(x)}.")
    return arr.ravel()


def _real_list(
    x: object,
    name: str,
    m: int,
    where: str,
    length_text: Callable[[int], str],
    complex_text: str,
) -> list[float]:
    """``x`` as m real floats; ValueError with ``length_text(size)`` or ``complex_text``."""
    arr = _numbers(x, name, where)
    if arr.dtype.kind == "b":
        raise ValueError(f"{name} must hold numbers, not booleans ({where}).")
    if arr.size != m:
        raise ValueError(length_text(int(arr.size)))
    if arr.dtype.kind == "c":
        if arr.size and float(np.max(np.abs(arr.imag))) > _TOL_REAL:
            raise ValueError(complex_text)
        arr = arr.real
    return [float(v) for v in arr.astype(float)]


def _score_pair(out: object, call: str, fix: str) -> list[float]:
    """What my_score returned, as [CVaR, F]; ValueError unless two real numbers."""
    if out is None:
        raise ValueError(f"{call} returned None; {fix}.")
    if isinstance(out, Mapping):
        raise ValueError(f"{call} returned a dict; {fix}.")
    if isinstance(out, (str, bytes)):
        raise ValueError(f"{call} returned a string; {fix}.")
    if _real(out) is not None:
        raise ValueError(
            f"{call} returned one number; {fix} (the CVaR_alpha and the feasible fraction)."
        )
    if isinstance(out, np.ndarray):
        items: list[object] = list(np.asarray(out).ravel().tolist())
    elif isinstance(out, (list, tuple)):
        items = list(out)
    else:
        raise ValueError(f"{call} returned {_kind(out)}; {fix}.")
    if len(items) != 2:
        count = "1 value" if len(items) == 1 else f"{len(items)} values"
        raise ValueError(f"{call} returned {count}; {fix}.")
    pair = []
    for pos, item in zip(("first", "second"), items):
        v = _real(item)
        if v is None:
            raise ValueError(
                f"{call} returned {_kind(item)} as its {pos} value; {fix}."
            )
        pair.append(v)
    return pair


def _whole(v: object) -> int | None:
    """``v`` as an int when it is a whole number (an int, or a float with no fraction)."""
    if isinstance(v, (bool, np.bool_)):
        return None
    if isinstance(v, (int, np.integer)):
        return int(v)
    if (
        isinstance(v, (float, np.floating))
        and math.isfinite(float(v))
        and float(v).is_integer()
    ):
        return int(v)
    return None


_ANGLE_NAMES = ("gamma", "theta", "beta")


def _angle(v: object, where: str, ensemble: bool, position: int = 1) -> float:
    """An angle of a layer tuple as a float. A free parameter is accepted only in a
    declared ensemble and only as theta (position 1 of the layer), the angle that the
    branches of the LCU fix; it is sent as 0.0."""
    if isinstance(v, ParameterExpression):
        if not v.parameters:
            return float(v.numeric())
        names = sorted(p.name for p in v.parameters)
        if ensemble and position == 1:
            return 0.0
        if ensemble:
            raise ValueError(
                f"Give {where} the numbers the job ran with: its {_ANGLE_NAMES[position]} "
                f"holds the free parameter {names}; in a declared ensemble only theta (the "
                "second angle of a layer) may stay free."
            )
        raise ValueError(
            f"Give {where} the numbers the job ran with: it holds the free parameter "
            f"{names}, and only a declared ensemble "
            '(lcu={"kind": "penalty", ...}) may leave its theta free.'
        )
    x = _real(v)
    if x is None:
        raise ValueError(
            f"{where} must be a number (an angle in radians), got {_kind(v)}."
        )
    return x


# ------------------------------------------------------------------------------------------
# Helpers: instances
# ------------------------------------------------------------------------------------------
def _edge_list(inst: ProblemInstance, name: str) -> list[tuple[int, int, float]]:
    try:
        return sorted(
            (min(int(i), int(j)), max(int(i), int(j)), float(w))
            for i, j, w in inst.edges
        )
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"{name}.edges must hold (i, j, w) triples; load the instance with the kit."
        ) from err


def _require_training(inst: ProblemInstance, name: str, exercise: str) -> None:
    """ValueError unless ``inst`` is the 12-node training instance of Part 1."""
    if (
        int(inst.n) == TRAIN12_N
        and int(inst.k) == TRAIN12_K
        and _edge_list(inst, name) == sorted(TRAIN12_EDGES)
    ):
        return
    raise ValueError(
        f"Pass the training instance of Part 1 as {name} (inst = event.training_instance()): "
        f"Exercise {exercise} is graded on the 12-node training instance, and the instance "
        f"passed has n = {inst.n}, k = {inst.k} and {len(list(inst.edges))} edges."
    )


def _instance_id(inst: ProblemInstance, name: str = "inst106") -> str:
    """The id of a Part 2 instance; ValueError when the kit did not attach one."""
    iid = getattr(inst, "instance_id", None)
    if not isinstance(iid, str) or not iid.strip():
        raise ValueError(
            f"Load {name} as in Part 0 (hw.load_handout with your handout file, or the demo "
            f"instance): {name} carries no instance_id, and the grader needs it to know "
            "which instance you ran."
        )
    if int(inst.n) > MAX_NODES:
        raise ValueError(
            f"{name} has n = {inst.n} nodes; the instances of this challenge have at most {MAX_NODES}."
        )
    return iid.strip()


def _small7() -> SimpleNamespace:
    """The 7-node instance of Exercise 1b with the fields of the kit's instances."""
    return SimpleNamespace(
        n=SMALL7_N,
        k=SMALL7_K,
        lam=SMALL7_LAM,
        edges=SMALL7_EDGES,
        theta_init=theta_init(SMALL7_N, SMALL7_K),
        name="small7",
    )


# ------------------------------------------------------------------------------------------
# Helpers: jobs
# ------------------------------------------------------------------------------------------
_FAILED_STATES = ("ERROR", "CANCELLED", "FAILED")
_MAX_SETS = 4096  # parameter sets of one job the client reads


def _require_done(job: BasePrimitiveJob, name: str) -> None:
    """ValueError unless the job finished successfully."""
    try:
        status = job.status()
    except Exception as err:  # network, local jobs
        raise ValueError(
            f"Run this cell again in a moment: the status of {name} cannot be read ({err})."
        ) from err
    status = str(getattr(status, "name", status)).upper()
    if status in _FAILED_STATES:
        raise ValueError(
            f"Grade a job that finished: {name} ended with status {status}. Look at "
            f"{name}.error_message(), submit the job again (with a new tag) and grade the new job."
        )
    if status != "DONE":
        raise ValueError(
            f"Wait until {name} is done ({name}.status() is {status}; {name}.result() waits "
            "for it), then run this cell again."
        )


def _register(pub: Any, i: int, name: str) -> Any:
    """The BitArray of PUB ``i``: register ``meas``, or the only classical register."""
    data = pub.data
    names = [nm for nm in data if hasattr(getattr(data, nm), "get_counts")]
    if "meas" in names:
        return data.meas
    if len(names) == 1:
        return getattr(data, names[0])
    if not names:
        raise ValueError(
            f"Measure the circuit of {name}: PUB {i} of the job has no classical register."
        )
    raise ValueError(
        f"Measure into one classical register (qc.measure_all()): PUB {i} of {name} has the "
        f"registers {names}."
    )


def _job_sets(
    job: BasePrimitiveJob, name: str, width: int
) -> tuple[list[dict[str, int]], list[int]]:
    """``(counts, sets_per_pub)``: one counts dictionary per parameter set, PUB by PUB and
    in C order within a PUB (the order of ``BitArray.get_counts(i)``)."""
    _require_done(job, name)
    try:
        result = job.result()
    except Exception as err:  # network, failed job
        raise ValueError(
            f"Run this cell again when the result of {name} can be read ({err})."
        ) from err
    sets: list[dict[str, int]] = []
    per_pub: list[int] = []
    for i, pub in enumerate(result):
        bits = _register(pub, i, name)
        if int(bits.num_bits) != width:
            raise ValueError(
                f"Grade the job of the right instance: the outcomes of {name} (PUB {i}) are "
                f"{bits.num_bits} bits wide, and this exercise needs {width}-bit outcomes, one "
                "bit per node of the instance."
            )
        shape = tuple(bits.shape)
        locs = list(np.ndindex(shape)) if shape else [()]
        if len(sets) + len(locs) > _MAX_SETS:
            raise ValueError(
                f"Grade a smaller job: {name} holds more than {_MAX_SETS} parameter sets."
            )
        for loc in locs:
            counts = bits.get_counts(loc) if shape else bits.get_counts()
            sets.append({str(key): int(v) for key, v in counts.items()})
        per_pub.append(len(locs))
    if not sets:
        raise ValueError(f"Grade a job with results: {name} holds no PUB.")
    return sets, per_pub


def _backend_name(job: BasePrimitiveJob) -> str:
    get = getattr(job, "backend", None)
    if not callable(get):
        return ""
    try:
        backend = get()
    except Exception:  # noqa: BLE001 - network
        return ""
    if backend is None:
        return ""
    name = getattr(backend, "name", backend)
    name = name() if callable(name) else name
    return str(name)


def _usage_seconds(job: BasePrimitiveJob) -> float:
    """QPU seconds that IBM reports for the job (0.0 until it is finalised)."""
    get = getattr(job, "usage", None)
    if not callable(get):
        return 0.0
    try:
        value = float(get() or 0.0)
    except Exception:  # noqa: BLE001 - network, not finalised
        return 0.0
    return value if math.isfinite(value) and value >= 0 else 0.0


def _job_record(job: BasePrimitiveJob, sets: list[dict[str, int]]) -> dict[str, Any]:
    return {
        "job_id": str(job.job_id()),
        "backend": _backend_name(job),
        "usage_seconds": _usage_seconds(job),
        "shots": int(sum(sum(c.values()) for c in sets)),
    }


def _merge(sets: list[dict[str, int]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for counts in sets:
        for key, v in counts.items():
            out[key] = out.get(key, 0) + v
    return out


def _sorted_shots(counts: dict[str, int]) -> tuple[list[str], np.ndarray]:
    """Keys in sorted order and the cumulative shot counts: shot j of the key-sorted shot
    list belongs to keys[searchsorted(cum, j, side="right")]."""
    keys = sorted(counts)
    cum = np.cumsum(np.array([counts[key] for key in keys], dtype=np.int64))
    return keys, cum


def _take(keys: list[str], cum: np.ndarray, idx: np.ndarray) -> dict[str, int]:
    got = np.bincount(np.searchsorted(cum, idx, side="right"), minlength=len(keys))
    return {keys[i]: int(got[i]) for i in np.flatnonzero(got)}


def _sample_without_replacement(
    counts: dict[str, int], size: int, rng: np.random.Generator
) -> dict[str, int]:
    """``size`` shots drawn without replacement (all shots when there are fewer)."""
    keys, cum = _sorted_shots(counts)
    total = int(cum[-1]) if len(cum) else 0
    if total <= size:
        return {key: int(counts[key]) for key in keys if counts[key] > 0}
    return _take(keys, cum, rng.choice(total, size=size, replace=False))


def _sample_ensemble(
    sets: list[dict[str, int]], q: np.ndarray, size: int, rng: np.random.Generator
) -> dict[str, int]:
    """``size`` draws from the pooled distribution sum_b q_b p_b: each draw picks branch b
    with probability q_b, then one of that branch's shots uniformly."""
    branch = rng.choice(len(sets), size=size, p=q)
    out: dict[str, int] = {}
    for b, n_b in enumerate(np.bincount(branch, minlength=len(sets))):
        if n_b == 0:
            continue
        keys, cum = _sorted_shots(sets[b])
        total = int(cum[-1]) if len(cum) else 0
        if total == 0:
            raise ValueError(
                f"Grade a complete job: branch {b} of the ensemble has no shots."
            )
        for key, v in _take(keys, cum, rng.integers(0, total, size=int(n_b))).items():
            out[key] = out.get(key, 0) + v
    return dict(sorted(out.items()))


def _lcu_weights(
    lcu: Mapping[str, object] | None, inst: ProblemInstance, n_sets: int, name: str
) -> np.ndarray | None:
    """The branch weights of a declared penalty ensemble, or None for ``lcu=None``."""
    if lcu is None:
        return None
    fix = (
        'pass lcu=None for a single circuit, or lcu={"kind": "penalty", "gamma": gamma} for '
        "the Fourier-LCU ensemble of the penalty at gamma"
    )
    if not isinstance(lcu, Mapping):
        raise ValueError(f"Declare the ensemble as a dict: {fix}.")
    unknown = sorted(set(map(str, lcu)) - {"kind", "gamma", "branches"})
    if unknown:
        raise ValueError(f"Remove the keys {unknown} from lcu: {fix}.")
    if lcu.get("kind") != "penalty":
        raise ValueError(f'Use the kind "penalty" (got {lcu.get("kind")!r}): {fix}.')
    gamma = _real(lcu.get("gamma"))
    if gamma is None or not math.isfinite(gamma):
        raise ValueError(
            f'Give lcu a finite "gamma", the cost angle of the ensemble: {fix}.'
        )
    n = int(inst.n)
    q = fourier_weights(n, int(inst.k), float(inst.lam), gamma)
    raw = lcu.get("branches")
    if raw is None:
        branches = list(range(n + 1))
    else:
        if isinstance(raw, (str, bytes, Mapping)) or not isinstance(
            raw, Sequence | np.ndarray
        ):
            raise ValueError(
                'lcu["branches"] must be a list of branch indices b in 0..n, one per parameter set.'
            )
        branches = [_whole(b) for b in np.asarray(raw, dtype=object).ravel().tolist()]
        if any(b is None or not 0 <= b <= n for b in branches) or len(
            set(branches)
        ) != len(branches):
            raise ValueError(
                f'lcu["branches"] must list different branch indices b in 0..{n}, one per parameter set.'
            )
    if n_sets != len(branches):
        raise ValueError(
            f"Put one parameter set per branch in {name}: the job holds {n_sets} parameter "
            f"sets, and the ensemble declares {len(branches)} branches (b = 0..n in this "
            'order, e.g. pub = (isa, {"theta": thetas}, shots) with thetas from fourier_lcu, '
            'or a subset with lcu["branches"]).'
        )
    w = q[np.asarray(branches, dtype=int)]
    if not w.sum() > 0:
        raise ValueError(
            "The declared branches carry no weight at this gamma: choose other branches."
        )
    return w / w.sum()


def _hardware_job(
    job: BasePrimitiveJob,
    name: str,
    inst: ProblemInstance,
    lcu: Mapping[str, object] | None = None,
    single: bool = False,
) -> dict[str, Any]:
    """The HardwareJob record of a job of ``inst``: job_id, backend, usage_seconds,
    shots and a sample of SAMPLE_SHOTS shots (pooled, or drawn through the ensemble's
    weights when ``lcu`` declares a penalty ensemble)."""
    sets, per_pub = _job_sets(job, name, int(inst.n))
    if single and per_pub != [1]:
        raise ValueError(
            f"Grade a job of one circuit: {name} holds {len(per_pub)} PUBs with {len(sets)} "
            "parameter sets. Run the circuit as the PUB (isa_c,), with no parameter values."
        )
    weights = _lcu_weights(lcu, inst, len(sets), name)
    rng = np.random.default_rng(SAMPLE_SEED)
    if weights is None:
        sample = _sample_without_replacement(_merge(sets), SAMPLE_SHOTS, rng)
    else:
        sample = _sample_ensemble(sets, weights, SAMPLE_SHOTS, rng)
    record = _job_record(job, sets)
    record["sample"] = sample
    return record


def _layer_count(layers: int | Layers, name: str) -> int:
    if isinstance(layers, (bool, np.bool_)):
        raise ValueError(
            f"{name} must be the number of layers of the circuit, an int >= 1."
        )
    if isinstance(layers, (int, np.integer)):
        count = int(layers)
    else:
        count = len(list(layers))
    if count < 1:
        raise ValueError(
            f"{name} must be at least 1 (the number of layers of the circuit), got {count}."
        )
    return count


def _layer_angles(layers: Layers, name: str, ensemble: bool) -> list[list[float]]:
    rows = list(layers)
    if not rows:
        raise ValueError(
            f"{name} is empty: pass the layer tuples of the circuit, [(gamma, theta, beta), ...]."
        )
    out = []
    for i, layer in enumerate(rows):
        if isinstance(layer, (str, bytes)) or not isinstance(
            layer, Sequence | np.ndarray
        ):
            raise ValueError(
                f"{name}[{i}] must be a layer tuple (gamma, theta, beta), got {_kind(layer)}."
            )
        values = list(layer)
        if len(values) != 3:
            raise ValueError(
                f"{name}[{i}] holds {len(values)} angles; a layer of the basis circuit is (gamma, theta, beta)."
            )
        out.append(
            [_angle(v, f"{name}[{i}]", ensemble, j) for j, v in enumerate(values)]
        )
    return out


def _frontier_answer(
    axis: str,
    hypothesis: str,
    control: FrontierArm,
    treatment: FrontierArm,
    inst106: ProblemInstance,
) -> dict[str, Any]:
    iid = _instance_id(inst106)
    hypothesis = hypothesis.strip()
    if len(hypothesis) > _MAX_TEXT:
        raise ValueError(
            f"Shorten the hypothesis to one sentence: it has {len(hypothesis)} characters."
        )
    arms: dict[str, Any] = {}
    for side, arm in (("control", control), ("treatment", treatment)):
        lcu = arm.get("lcu")
        record = _hardware_job(arm["job"], f'{side}["job"]', inst106, lcu)
        angles = _layer_angles(arm["layers"], f'{side}["layers"]', lcu is not None)
        record["layers"] = len(angles)
        record["lcu"] = "single" if lcu is None else "penalty-ensemble"
        record["angles"] = angles
        arms[side] = record
    return {
        "instance_id": iid,
        "axis": axis,
        "hypothesis": hypothesis,
        "control": arms["control"],
        "treatment": arms["treatment"],
    }


# ------------------------------------------------------------------------------------------
# Part 1 - the method on the 12-qubit training instance
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_tcfs_ex1a(
    basis_circuit: Callable[[ProblemInstance], QuantumCircuit],
    inst: ProblemInstance,
) -> None:
    """Grade Exercise 1a, the basis circuit: ``grade_lab_tcfs_ex1a(basis_circuit, inst)``.

    Args:
        basis_circuit: your function ``basis_circuit`` of Exercise 1a (the function itself,
            not its result).
        inst: the training instance of Part 1 (``inst = event.training_instance()``).

    The grader calls ``basis_circuit(inst)`` here and sends the circuit it returns.
    """
    _require_training(inst, "inst", "1a")
    qc = _call("basis_circuit(inst)", basis_circuit, inst)
    if qc is None:
        raise ValueError(
            "End basis_circuit with return qc: basis_circuit(inst) returned None."
        )
    if not isinstance(qc, QuantumCircuit):
        raise ValueError(
            f"Return the QuantumCircuit from basis_circuit: basis_circuit(inst) returned {_kind(qc)}."
        )
    if qc.num_qubits > MAX_NODES or qc.size() > _MAX_CIRCUIT_OPS:
        raise ValueError(
            f"Build the circuit on inst.n = {inst.n} qubits: basis_circuit(inst) returned a circuit "
            f"with {qc.num_qubits} qubits and {qc.size()} operations."
        )
    _grade({"circuit": qc}, "ex1a")


def _lcu_probe(
    fourier_lcu: Callable[..., Any], inst: Any, label: str, gamma: float, on: str
) -> dict[str, Any]:
    """One call of the participant's fourier_lcu, as a probe record of Exercise 1b."""
    m = int(inst.n) + 1
    where = f"{on} at gamma = {gamma}"
    out = _call(f"fourier_lcu(inst, {gamma}) {on}", fourier_lcu, inst, gamma)
    order = "return thetas, c, weights, Gamma, in this order"
    if isinstance(out, Mapping):
        raise ValueError(f"Return the four values, not a dict: {order}.")
    if not isinstance(out, (tuple, list)) or len(out) != 4:
        raise ValueError(
            f"Return four values from fourier_lcu, {order} (it returned {_kind(out)} {where})."
        )

    def length(name: str) -> Callable[[int], str]:
        return lambda size: (
            f"Return n+1 = {m} entries in {name}, one per b = 0..n: {name} has {size} "
            f"entries {where}."
        )

    thetas = _real_list(
        out[0],
        "thetas",
        m,
        where,
        length("thetas"),
        f"Return the real angles theta_b first: the first value fourier_lcu returned {where} "
        f"is complex (c goes second; {order}).",
    )
    c = _numbers(out[1], "c", where)
    if c.dtype.kind == "b":
        raise ValueError(f"c must hold complex coefficients, not booleans ({where}).")
    if c.size != m:
        raise ValueError(length("c")(int(c.size)))
    c = c.astype(complex)
    weights = _real_list(
        out[2],
        "weights",
        m,
        where,
        length("weights"),
        f"Return real probabilities as weights, q_b = |c_b| / sum_b |c_b|: the third value "
        f"fourier_lcu returned {where} is complex ({order}).",
    )
    gamma_value = _real(out[3])
    if gamma_value is None:
        raise ValueError(
            f"Return Gamma as one real number, ||c||_1^2: the fourth value fourier_lcu "
            f"returned {where} is {_kind(out[3])} ({order})."
        )
    return {
        "instance": label,
        "gamma": float(gamma),
        "thetas": thetas,
        "c_re": [float(v) for v in c.real],
        "c_im": [float(v) for v in c.imag],
        "weights": weights,
        "Gamma": gamma_value,
    }


_ON_INSTANCE = {
    "train12": "on the training instance",
    "small7": "on the 7-node instance (n = 7, k = 3, lam = 5, an edge of weight 2)",
}


def _probe_instance(label: str, inst: ProblemInstance) -> Any:
    """The participant's training instance, or the 7-node instance of the probes."""
    return inst if label == "train12" else _small7()


@typechecked
def grade_lab_tcfs_ex1b(
    fourier_lcu: Callable[[ProblemInstance, float], Sequence[object]],
    inst: ProblemInstance,
) -> None:
    """Grade Exercise 1b, the Fourier LCU: ``grade_lab_tcfs_ex1b(fourier_lcu, inst)``.

    Args:
        fourier_lcu: your function ``fourier_lcu(inst, gamma)`` of Exercise 1b (the function
            itself), returning ``thetas, c, weights, Gamma``.
        inst: the training instance of Part 1 (``inst = event.training_instance()``).

    The grader calls ``fourier_lcu`` here: on ``inst`` at gamma = 0.37, 0.9 and 1.63, and at
    gamma = 0.9 on a 7-node instance (n = 7, k = 3, lam = 5) whose fields ``n``, ``k``,
    ``lam``, ``edges`` and ``theta_init`` it reads like the kit's instances.
    """
    _require_training(inst, "inst", "1b")
    probes = [
        _lcu_probe(
            fourier_lcu, _probe_instance(label, inst), label, gamma, _ON_INSTANCE[label]
        )
        for label, gamma in PROBES_1B
    ]
    _grade({"probes": probes}, "ex1b")


def _is_two_qubit(instruction: Any) -> bool:
    op = instruction.operation
    return op.num_qubits == 2 and op.name not in (
        "barrier",
        "delay",
        "measure",
        "reset",
    )


@typechecked
def grade_lab_tcfs_ex1c(isa: QuantumCircuit, backend: BackendV2 | str) -> None:
    """Grade Exercise 1c, the ISA circuit: ``grade_lab_tcfs_ex1c(isa, backend)``.

    Args:
        isa: your transpiled, still parametrized basis circuit of Exercise 1c.
        backend: your assigned backend of the setup cell (or its name).

    The circuit, the backend name and the circuit's two-qubit gate count and two-qubit depth
    are sent.
    """
    if isa.num_qubits > MAX_NODES or isa.size() > _MAX_CIRCUIT_OPS:
        raise ValueError(
            f"Transpile the 12-qubit basis circuit for your backend: isa has {isa.num_qubits} "
            f"qubits and {isa.size()} operations (at most {MAX_NODES} qubits and "
            f"{_MAX_CIRCUIT_OPS} operations are accepted)."
        )
    name = backend if isinstance(backend, str) else str(backend.name)
    _grade(
        {
            "circuit": isa,
            "backend": name.strip(),
            "num_2q": int(sum(1 for ci in isa.data if _is_two_qubit(ci))),
            "depth_2q": int(isa.depth(_is_two_qubit)),
        },
        "ex1c",
    )


def _feasible_list(x: object, m: int, where: str) -> list[bool]:
    arr = _numbers(x, "feasible", where)
    if arr.size != m:
        raise ValueError(
            f"Return one feasible flag per key of counts: evaluate_counts returned {arr.size} "
            f"for {m} bitstrings ({where})."
        )
    if arr.dtype.kind == "c" or not np.all(np.isin(arr, (0, 1))):
        raise ValueError(
            f"feasible must hold booleans, True exactly when W(x) = k ({where})."
        )
    return [bool(v) for v in arr]


def _shots_list(x: object, m: int, where: str) -> list[int]:
    arr = _numbers(x, "shots", where)
    if arr.size != m:
        raise ValueError(
            f"Return one shot count per key of counts: evaluate_counts returned {arr.size} "
            f"for {m} bitstrings ({where})."
        )
    whole = [_whole(v) for v in (arr.real if arr.dtype.kind == "c" else arr).tolist()]
    if arr.dtype.kind == "b" or any(v is None for v in whole):
        raise ValueError(
            "The third array of evaluate_counts must hold the shot count of each bitstring, "
            f"the values of the counts dictionary ({where})."
        )
    return [int(v) for v in whole if v is not None]


@typechecked
def grade_lab_tcfs_ex1d(
    evaluate_counts: Callable[[ProblemInstance, dict[str, int]], Sequence[object]],
    cvar: Callable[[Sequence[float], Sequence[float], float], float],
    job: BasePrimitiveJob,
    inst: ProblemInstance,
) -> None:
    """Grade Exercise 1d: ``grade_lab_tcfs_ex1d(evaluate_counts, cvar, job, inst)``.

    Args:
        evaluate_counts: your function ``evaluate_counts(inst, counts)`` of Exercise 1d.
        cvar: your function ``cvar(values, weights, alpha)`` of Exercise 1d.
        job: the practice job of Exercise 1d (the job object of the job cell, not its id
            and not ``job.result()``): two PUBs, the 13 branches of the ensemble and the
            single trained circuit.
        inst: the training instance of Part 1 (``inst = event.training_instance()``).

    The grader calls ``evaluate_counts`` here on seeded synthetic counts, 60 bitstrings of
    ``inst`` and 40 of a 7-node instance (n = 7, k = 3, lam = 5, an edge of weight 2) whose
    fields ``n``, ``k``, ``lam`` and ``edges`` it reads like the kit's instances, and
    ``cvar`` on 48 fixed cases, and sends their outputs with the counts of every parameter
    set of the job and its id, backend name and QPU usage (self-reported).
    """
    _require_training(inst, "inst", "1d")
    values: list[float] = []
    feasible: list[bool] = []
    shots: list[int] = []
    for label, counts in probe_counts_1d():
        m = len(counts)
        where = f"on the synthetic counts {_ON_INSTANCE[label]}"
        out = _call(
            f"evaluate_counts(inst, counts) {_ON_INSTANCE[label]}",
            evaluate_counts,
            _probe_instance(label, inst),
            dict(counts),
        )
        if not isinstance(out, (tuple, list)) or len(out) != 3:
            raise ValueError(
                "Return three arrays from evaluate_counts, values, feasible and shots, "
                f"each with one entry per key of counts (it returned {_kind(out)} {where})."
            )
        values += _real_list(
            out[0],
            "values",
            m,
            where,
            lambda size, m=m, where=where: (
                f"Return one value per key of counts: evaluate_counts returned {size} "
                f"values for {m} bitstrings ({where})."
            ),
            f"values must be real numbers, f_lambda(x) of each bitstring ({where}).",
        )
        feasible += _feasible_list(out[1], m, where)
        shots += _shots_list(out[2], m, where)
    cvar_values = []
    for i, (v, w, alpha) in enumerate(probe_cases_1d()):
        got = _call(f"cvar(values, weights, {alpha:g})", cvar, list(v), list(w), alpha)
        value = _real(got)
        if value is None:
            raise ValueError(
                f"Return one number from cvar: on reference case {i} it returned {_kind(got)}."
            )
        cvar_values.append(value)
    sets, per_pub = _job_sets(job, "job", TRAIN12_N)
    if len(sets) > _MAX_SETS_1D:
        raise ValueError(
            f"Grade the practice job of Exercise 1d (13 + 1 parameter sets): job holds "
            f"{len(sets)} parameter sets."
        )
    _grade(
        {
            "values": values,
            "feasible": feasible,
            "shots": shots,
            "cvar_cases": cvar_values,
            "job": _job_record(job, sets),
            "counts_list": sets,
            "n_sets": per_pub,
        },
        "ex1d",
    )


# ------------------------------------------------------------------------------------------
# Part 2 - the campaign on the 106-qubit instance
# ------------------------------------------------------------------------------------------
_FIX_2A = "my_score returns two numbers: return tail, F"


@typechecked
def grade_lab_tcfs_ex2a(
    my_score: Callable[[dict[str, int]], Sequence[object]],
    inst106: ProblemInstance,
) -> None:
    """Grade Exercise 2a, your scoring function: ``grade_lab_tcfs_ex2a(my_score, inst106)``.

    Args:
        my_score: your function ``my_score(counts, alpha=0.10)`` of Exercise 2a (the
            function itself); keep the parameter name ``alpha``.
        inst106: your 106-qubit instance of Part 2.

    The grader calls ``my_score(counts)`` on three seeded probe counts dictionaries of your
    instance and ``my_score(counts, alpha=0.25)`` on the first, here, and sends the pairs.
    """
    iid = _instance_id(inst106)
    probes = probe_counts_2a(int(inst106.n), int(inst106.k))
    outputs = [
        _score_pair(
            _call("my_score(counts)", my_score, dict(c)), "my_score(counts)", _FIX_2A
        )
        for c in probes
    ]
    call = f"my_score(counts, alpha={ALPHA_2A:g})"
    try:
        inspect.signature(my_score).bind({}, alpha=ALPHA_2A)
    except TypeError as err:
        raise ValueError(
            f"Keep the parameter alpha of my_score, def my_score(counts, alpha=0.10): the "
            f"grader calls {call} ({err})."
        ) from err
    except ValueError:
        pass  # no signature to inspect (a builtin); the call below decides
    raw = _call(call, my_score, dict(probes[0]), alpha=ALPHA_2A)
    _grade(
        {
            "instance_id": iid,
            "outputs": outputs,
            "output_alpha25": _score_pair(raw, call, _FIX_2A),
        },
        "ex2a",
    )


_STATS_FIX = "pass the stats that nb.weight_histogram(inst106, counts, ideal=info) returned in Step 3"


def _baseline_mean(
    stats: Mapping[str, object] | Sequence[float] | float | np.floating,
) -> float:
    if isinstance(stats, Mapping):
        mapping = cast(Mapping[str, object], stats)
        if "mean_W" not in mapping:
            if "exp_W" in mapping:
                raise ValueError(
                    f"Use the measured mean, not the ideal one: stats holds exp_W, the ideal "
                    f"moments of Step 1; {_STATS_FIX}."
                )
            raise ValueError(f'stats has no key "mean_W": {_STATS_FIX}.')
        value = _real(mapping["mean_W"])
    elif (
        isinstance(stats, tuple) and hasattr(stats, "mean") and not callable(stats.mean)
    ):
        value = _real(stats.mean)
    else:
        value = _real(stats)
    if value is None:
        raise ValueError(
            f"stats must hold the measured mean Hamming weight of the baseline job: {_STATS_FIX}."
        )
    return value


def _baseline_layer(
    layers: Sequence[Sequence[float | np.floating]] | Sequence[float | np.floating],
) -> list[float]:
    rows = list(layers)
    if len(rows) == 3 and all(_real(v) is not None for v in rows):
        layer: Sequence[object] = rows
    elif len(rows) == 1 and isinstance(rows[0], Sequence | np.ndarray):
        layer = list(cast(Sequence[object], rows[0]))
    else:
        raise ValueError(
            "Pass layers of Step 1 (layers, info = hw.lagrangian_layers(inst106)): one layer "
            f"(gamma, theta, beta); got {_kind(layers)}."
        )
    values = [_real(v) for v in layer]
    if len(values) != 3 or any(v is None for v in values):
        raise ValueError(
            "The layer of Step 1 must hold three numbers, (gamma, theta, beta)."
        )
    return [float(v) for v in values if v is not None]


@typechecked
def grade_lab_tcfs_ex2b(
    job_c: BasePrimitiveJob,
    theta_c: float | np.floating,
    stats: Mapping[str, object] | Sequence[float] | float | np.floating,
    layers: Sequence[Sequence[float | np.floating]] | Sequence[float | np.floating],
    inst106: ProblemInstance,
) -> None:
    """Grade Exercise 2b: ``grade_lab_tcfs_ex2b(job_c, theta_c, stats, layers, inst106)``.

    Args:
        job_c: the job object of the re-centred circuit (tag ``"recentred"``): one PUB,
            ``(isa_c,)``, with at least 1,000 shots.
        theta_c: your re-centred angle, a float in radians.
        stats: the baseline's ``stats`` of Step 3 (what ``nb.weight_histogram`` returned);
            ``stats["mean_W"]`` is sent.
        layers: ``layers`` of Step 1 (``hw.lagrangian_layers``); its one layer
            ``(gamma, theta, beta)`` is sent.
        inst106: your 106-qubit instance of Part 2.

    The job is sent as its id, backend name, QPU usage, shots and a seeded sample of 4,096
    of its shots (self-reported).
    """
    iid = _instance_id(inst106)
    theta = _real(theta_c)
    if theta is None:
        raise ValueError(f"theta_c must be one real number, got {_kind(theta_c)}.")
    _grade(
        {
            "instance_id": iid,
            "theta_c": theta,
            "baseline_mean_w": _baseline_mean(stats),
            "layers_baseline": _baseline_layer(layers),
            "job": _hardware_job(job_c, "job_c", inst106, single=True),
        },
        "ex2b",
    )


_SCORES_2C = (
    "scores_s = [my_score(data_s.c.get_counts(i)) for i in range(len(thetas_sweep))]"
)


@typechecked
def grade_lab_tcfs_ex2c(
    job_s: BasePrimitiveJob,
    thetas_sweep: np.ndarray | Sequence[float | np.floating],
    scores_s: np.ndarray | Sequence[Sequence[float | np.floating]],
    inst106: ProblemInstance,
) -> None:
    """Grade Exercise 2c, the sweep: ``grade_lab_tcfs_ex2c(job_s, thetas_sweep, scores_s, inst106)``.

    Args:
        job_s: the job object of the sweep (tag ``"theta-sweep"``): one PUB that carries all
            values of theta, ``(isa_s, {"theta": thetas_sweep}, 4096)``.
        thetas_sweep: the values of theta of the PUB, in its order.
        scores_s: your pairs (CVaR_0.10, F), one per setting in the order of
            ``thetas_sweep``, as ``my_score`` returns them.
        inst106: your 106-qubit instance of Part 2.

    Per setting the grader sends a seeded sample of 512 of its shots and its mean Hamming
    weight, with the job's id, backend name, QPU usage and shots (self-reported).
    """
    iid = _instance_id(inst106)
    sets, per_pub = _job_sets(job_s, "job_s", int(inst106.n))
    if len(per_pub) != 1:
        raise ValueError(
            'Put all values of theta into one PUB, pub_s = (isa_s, {"theta": thetas_sweep}, 4096): '
            f"job_s holds {len(per_pub)} PUBs."
        )
    m = len(sets)
    if m > MAX_SWEEP_SETTINGS:
        raise ValueError(
            f"Grade a sweep of at most {MAX_SWEEP_SETTINGS} settings: job_s holds {m}."
        )
    thetas = _real_list(
        thetas_sweep,
        "thetas_sweep",
        m,
        "the sweep",
        lambda size: (
            f"Pass the values of theta of the PUB, in its order: thetas_sweep holds {size} "
            f"values and the PUB of job_s holds {m} parameter sets."
        ),
        "thetas_sweep must hold real angles in radians.",
    )
    if isinstance(scores_s, (str, bytes, Mapping)):
        raise ValueError(
            f"scores_s must be a list of {m} pairs (CVaR_0.10, F): {_SCORES_2C}."
        )
    items = list(scores_s)
    if len(items) != m:
        raise ValueError(
            f"Give one pair (CVaR_0.10, F) per setting: scores_s holds {len(items)} entries "
            f"and the job has {m} settings; {_SCORES_2C}."
        )
    scores = [
        _score_pair(
            item,
            f"scores_s[{i}]",
            f"each entry is my_score of one setting, {_SCORES_2C}",
        )
        for i, item in enumerate(items)
    ]
    rng = np.random.default_rng(SAMPLE_SEED)
    samples = [_sample_without_replacement(c, SWEEP_SAMPLE_SHOTS, rng) for c in sets]
    mean_w = [
        float(sum(key.count("1") * v for key, v in c.items()) / max(1, sum(c.values())))
        for c in sets
    ]
    _grade(
        {
            "instance_id": iid,
            "thetas": thetas,
            "scores": scores,
            "mean_w": mean_w,
            "shots_per_setting": int(min(sum(c.values()) for c in sets)),
            "samples": samples,
            "job": _job_record(job_s, sets),
        },
        "ex2c",
    )


_PLAN = "my_plan = [(label, circuits, shots, repeat), ...]"
_PLAN_ROW = (
    "each row is (label, circuits, shots) or (label, circuits, shots, repeat), or a dict "
    "with the keys label, circuits, shots and repeat"
)


def _plan_row(item: Sequence[object] | Mapping[str, object], i: int) -> dict[str, Any]:
    """Row ``i`` (from 1) as {label, circuits, shots, repeat}, with the defaults of
    ``nb.plan`` for a dict (circuits 1, shots 2**15, repeat 1)."""
    if isinstance(item, Mapping):
        mapping = cast(Mapping[str, object], item)
        unknown = sorted(
            set(map(str, mapping)) - {"label", "circuits", "shots", "repeat"}
        )
        if unknown:
            raise ValueError(
                f"Remove the keys {unknown} from row {i} of my_plan: {_PLAN_ROW}."
            )
        label = mapping.get("label")
        values = (
            mapping.get("circuits", 1),
            mapping.get("shots", 2**15),
            mapping.get("repeat", 1),
        )
    elif isinstance(item, (tuple, list)):
        if len(item) not in (3, 4):
            raise ValueError(
                f"Row {i} of my_plan holds {len(item)} values: {_PLAN_ROW}."
            )
        label = item[0]
        values = (item[1], item[2], item[3] if len(item) == 4 else 1)
    else:
        raise ValueError(f"Row {i} of my_plan is {_kind(item)}: {_PLAN_ROW}.")
    if not isinstance(label, str):
        raise ValueError(
            f"Give row {i} of my_plan a label, a short text that names the kind of job: {_PLAN_ROW}."
        )
    row: dict[str, Any] = {"label": label.strip()[:_NOTE_CHARS]}
    for key, v in zip(("circuits", "shots", "repeat"), values):
        whole = _whole(v)
        if whole is None:
            raise ValueError(
                f'Row {i} of my_plan ("{label.strip()}"): {key} must be a whole number, got {v!r}.'
            )
        row[key] = whole
    return row


@typechecked
def grade_lab_tcfs_ex2d(
    my_plan: Sequence[
        Sequence[str | int | float | np.integer | np.floating] | Mapping[str, object]
    ],
) -> None:
    """Grade Exercise 2d, your QPU-time plan: ``grade_lab_tcfs_ex2d(my_plan)``.

    Args:
        my_plan: your list of rows ``(label, circuits, shots, repeat)`` of Exercise 2d (the
            list itself, not what ``nb.plan`` returns); a row may also be a list, or a dict
            with the keys ``label``, ``circuits``, ``shots`` and ``repeat``.
    """
    if isinstance(my_plan, str):
        raise ValueError(f"my_plan must be a list of rows, got a string: {_PLAN}.")
    rows = list(my_plan)
    if rows and isinstance(rows[0], str):
        raise ValueError(
            f"Put the row into a list: my_plan is one row, and the plan is a list of rows, {_PLAN}."
        )
    if len(rows) > _MAX_PLAN_ROWS:
        raise ValueError(
            f"Plan with at most {_MAX_PLAN_ROWS} rows: my_plan holds {len(rows)}."
        )
    _grade({"rows": [_plan_row(item, i) for i, item in enumerate(rows, 1)]}, "ex2d")


@typechecked
def grade_lab_tcfs_ex2e(
    job: BasePrimitiveJob,
    inst106: ProblemInstance,
    lcu: Mapping[str, object] | None = None,
    layers: int | Layers = 1,
    note: str = "",
) -> None:
    """Grade a campaign job, Exercise 2e: ``grade_lab_tcfs_ex2e(job, inst106, lcu=None, note="...")``.

    Every job of your 106-qubit instance that you want counted goes through this call; the
    best score counts.

    Args:
        job: the job object that ``sampler.run`` (or ``jobs.run_once``) returned.
        inst106: your 106-qubit instance of Part 2.
        lcu: ``None`` for a single circuit (several circuits or parameter sets are pooled
            with their shots), or ``{"kind": "penalty", "gamma": gamma}`` for the Fourier-LCU
            ensemble of the penalty: the parameter sets of the job are the branches
            b = 0..n in this order (a subset with ``"branches": [b, ...]``), and the sample
            is drawn through the branch weights q_b, which the grader computes itself.
        layers: the number of layers of the circuit (or its list of layer tuples).
        note: a short label for your own records.

    The job is sent as its id, backend name, QPU usage, shots and a seeded sample of 4,096
    shots (self-reported).
    """
    iid = _instance_id(inst106)
    record = _hardware_job(job, "job", inst106, lcu)
    record["layers"] = _layer_count(layers, "layers")
    record["lcu"] = "single" if lcu is None else "penalty-ensemble"
    _grade(
        {"instance_id": iid, "job": record, "note": note.strip()[:_NOTE_CHARS]}, "ex2e"
    )


# ------------------------------------------------------------------------------------------
# Part 3 - the frontier round: one exercise per axis
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_tcfs_ex3d(
    hypothesis: str,
    control: FrontierArm,
    treatment: FrontierArm,
    inst106: ProblemInstance,
) -> None:
    """Grade a frontier experiment on axis D, depth:
    ``grade_lab_tcfs_ex3d(hypothesis, control, treatment, inst106)``.

    Args:
        hypothesis: your hypothesis, one sentence (at most 500 characters).
        control: ``{"job": job, "layers": [(gamma, theta, beta)]}``, the one-layer control
            job and the layer tuple of its circuit (for example the re-centred job of
            Exercise 2b and ``[(gamma, theta_c, beta)]``).
        treatment: ``{"job": job2, "layers": layers2}``, the treatment job and the layer
            tuples of its circuit, with more layers than the control.
        inst106: your 106-qubit instance of Part 2.

    Both dicts may carry ``"lcu": None`` or ``{"kind": "penalty", "gamma": g}``. Each job is
    sent as its id, backend name, QPU usage, shots, a seeded sample of 4,096 shots, its
    number of layers, its declaration and its angles (self-reported).
    """
    _grade(_frontier_answer("D", hypothesis, control, treatment, inst106), "ex3d")


@typechecked
def grade_lab_tcfs_ex3l(
    hypothesis: str,
    control: FrontierArm,
    treatment: FrontierArm,
    inst106: ProblemInstance,
) -> None:
    """Grade a frontier experiment on axis L, partial LCU:
    ``grade_lab_tcfs_ex3l(hypothesis, control, treatment, inst106)``.

    Args:
        hypothesis: your hypothesis, one sentence (at most 500 characters).
        control: ``{"job": job, "layers": [(gamma, theta, beta)], "lcu": None}``, a
            single-circuit control job and the layer tuples of its circuit.
        treatment: ``{"job": job_ens, "layers": [(gamma, Parameter("theta"), beta)], "lcu":
            {"kind": "penalty", "gamma": gamma}}``, the ensemble job (one PUB whose
            parameter sets are the branches b = 0..n), its layer tuples and its declaration.
        inst106: your 106-qubit instance of Part 2.

    Each job is sent as its id, backend name, QPU usage, shots, a seeded sample of 4,096
    shots (for the ensemble drawn through the branch weights q_b), its number of layers,
    its declaration and its angles (self-reported; the ensemble's free theta, which its
    branches fix, is sent as 0.0).
    """
    _grade(_frontier_answer("L", hypothesis, control, treatment, inst106), "ex3l")


@typechecked
def grade_lab_tcfs_ex3t(
    hypothesis: str,
    control: FrontierArm,
    treatment: FrontierArm,
    inst106: ProblemInstance,
) -> None:
    """Grade a frontier experiment on axis T, training policy:
    ``grade_lab_tcfs_ex3t(hypothesis, control, treatment, inst106)``.

    Args:
        hypothesis: your hypothesis, one sentence (at most 500 characters).
        control: ``{"job": job, "layers": [(gamma, theta, beta), ...]}``, the control job
            (the re-centred transfer of Part 2) and the layer tuples of its circuit.
        treatment: the same for the treatment job: the same number of layers and the same
            declaration, with angles chosen another way.
        inst106: your 106-qubit instance of Part 2.

    Both dicts may carry ``"lcu": None`` or ``{"kind": "penalty", "gamma": g}``. Each job is
    sent as its id, backend name, QPU usage, shots, a seeded sample of 4,096 shots, its
    number of layers, its declaration and its angles (self-reported).
    """
    _grade(_frontier_answer("T", hypothesis, control, treatment, inst106), "ex3t")
