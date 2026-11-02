"""Probe constants and probe objects for the Floquet dynamics lab (qdc_2026 / lab_floquet).

The grading server holds an identical copy of every constant below
(``validations/qdc_2026/_floquet_reference.py``) and never trusts values echoed in a
payload. ``probe_constants()`` is dumped to the server fixtures as ``probes.json``; a server
test asserts that both copies agree.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2

Edge = tuple[int, int]
Op = tuple[str, tuple[int, ...], float]

# --------------------------------------------------------------------------- #
# Probe lattice: subdivided K_{1,3}, the smallest heavy-hex fragment with three colours
# --------------------------------------------------------------------------- #

PROBE_N_QUBITS = 7
PROBE_EDGES: tuple[Edge, ...] = ((0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6))
PROBE_COLORS: tuple[int, ...] = (0, 1, 2, 1, 0, 0)
PROBE_POSITIONS: dict[int, tuple[float, float]] = {
    0: (0.0, 0.0),
    1: (1.0, 0.0),
    2: (-0.5, 0.87),
    3: (-0.5, -0.87),
    4: (2.0, 0.0),
    5: (-1.0, 1.73),
    6: (-1.0, -1.73),
}
PROBE_GROUPS: tuple[tuple[Edge, ...], ...] = (
    ((0, 1), (2, 5), (3, 6)),
    ((0, 2), (1, 4)),
    ((0, 3),),
)
PROBE_DEGREES: tuple[int, ...] = (3, 2, 2, 2, 1, 1, 1)
PROBE_Z2_SITES: tuple[int, ...] = (1, 2, 3)

PARAMS: tuple[float, float, float] = (math.pi / 6, math.pi / 27, math.pi / 3)
ALT_PARAMS: tuple[float, float, float] = (0.37, 0.11, 0.83)
THETA_ZZ = PARAMS[2]

# --------------------------------------------------------------------------- #
# ex2_1 / ex2_2 probes
# --------------------------------------------------------------------------- #

LOGICAL_DEPTHS: tuple[int, ...] = (0, 1, 2)
BASELINE_COUNTS: tuple[dict[str, int], ...] = (
    {"0000000": 6, "0000010": 2},
    {"0000000": 3, "0001000": 2, "1000000": 3},
)

READOUT_LAYOUTS: tuple[tuple[int, ...], ...] = ((2, 5, 8), (5, 1, 9))
READOUT_SETTINGS: dict[str, bool | int | str] = {
    "shots": 128,
    "method": "balanced",
    "async_cal": False,
}
READOUT_QUBITS: tuple[int, ...] = (1, 2, 5, 8, 9)
READOUT_PROBES: tuple[str, ...] = ("A", "B", "C_false", "C_true", "D")
READOUT_CAL_ERROR = "calibration failed"

CORRECTED_PHYSICAL: tuple[int, ...] = tuple(
    range(PROBE_N_QUBITS + 2, 2, -1)
)  # (9, 8, ..., 3)
CORRECTED_COUNTS: tuple[dict[str, int], ...] = (
    {"0" * PROBE_N_QUBITS: 7, "0" * (PROBE_N_QUBITS - 2) + "10": 1},
    {"0" * PROBE_N_QUBITS: 4, "1" + "0" * (PROBE_N_QUBITS - 1): 4},
)
# Signed quasi-distributions as mthree returns them: integer keys first, bitstrings second.
CORRECTED_QUASI: tuple[dict[int | str, float], ...] = (
    {0: 1.1, (1 << PROBE_N_QUBITS) - 1: -0.1},
    {"0" * PROBE_N_QUBITS: 0.6, "1" * PROBE_N_QUBITS: 0.4},
)

FOLD_DEPTHS: tuple[int, ...] = (1, 2)
FOLD_SCALES: tuple[int, ...] = (1, 3, 5)

ZNE_INTERCEPT: tuple[float, ...] = (0.3, -0.2, 0.55)
ZNE_SLOPE: tuple[float, ...] = (-0.02, 0.03, -0.04)
ZNE_SCALE_CALLS: tuple[tuple[int, ...] | None, ...] = (
    (1, 3),
    (1, 3, 5),
    None,
)  # None: default

# --------------------------------------------------------------------------- #
# ex3_1 / ex3_2 / ex3_3 probes
# --------------------------------------------------------------------------- #

NORMALIZE_PROBES: tuple[tuple[int, tuple[Op, ...]], ...] = (
    (
        3,
        (
            ("rx", (0,), 0.2),
            ("rzz", (0, 1), -THETA_ZZ),
            ("rz", (2,), -0.1),
            ("rzz", (1, 2), THETA_ZZ),
            ("rzz", (0, 2), -0.21),
        ),
    ),
    (
        4,
        (
            ("rzz", (2, 3), -0.4),
            ("rx", (1,), 0.3),
            ("rzz", (0, 1), 0.5),
            ("rzz", (1, 2), -THETA_ZZ),
        ),
    ),
)

BACKEND_BASIS: tuple[str, ...] = ("rz", "sx", "x", "rzz")
BACKEND_SEED = 2026
LAYOUT_LIMIT = 10

MAPOMATIC_N_QUBITS = 4
MAPOMATIC_COUPLING: tuple[Edge, ...] = ((0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2))
MAPOMATIC_RZZ_ERRORS: dict[tuple[int, ...], float] = {
    (0, 1): 0.020,
    (1, 2): 0.010,
    (2, 3): 0.005,
}
MAPOMATIC_CIRCUIT: tuple[int, tuple[Op, ...]] = (
    3,
    (("rzz", (0, 1), 0.2), ("rzz", (1, 2), 0.2)),
)

ESTIMATOR_ALLOWANCE = 321

# --------------------------------------------------------------------------- #
# ex4_2 probes
# --------------------------------------------------------------------------- #

MEASURE_LAYOUT: tuple[int, ...] = (
    0,
    2,
    3,
    1,
    5,
    6,
    4,
)  # a non-identity symmetry of the lattice
MEASURE_CYCLES: tuple[int, ...] = (1, 2)
MEASURE_FACTORS: tuple[int, ...] = (1, 3)
MEASURE_CHARGE = 42.0
MEASURE_JOB_ID = "job-probe-1"
MEASURE_PROBES: tuple[str, ...] = (
    "main",
    "empty_cycles",
    "empty_factors",
    "no_hardware",
    "short_result",
    "no_metrics",
)

# --------------------------------------------------------------------------- #
# ex4_3 ZNE fixtures
# --------------------------------------------------------------------------- #

ZNE_FACTORS: tuple[int, ...] = (1, 3, 5)
ZNE_CYCLES: tuple[int, ...] = (1, 2, 3)
ZNE_STD = 0.01
ZNE_MZ2_SCALE = 0.8
ZNE_LINEAR = {"intercept": (0.31, -0.14, 0.47), "slope": (-0.025, 0.018, -0.014)}
ZNE_QUADRATIC = {
    "intercept": (0.41, 0.27, -0.13),
    "slope": (-0.03, 0.02, 0.016),
    "curvature": (0.004, -0.003, 0.002),
}
ZNE_EXPONENTIAL = {"intercept": (0.72, 0.48, 0.61), "rate": (0.13, 0.19, 0.09)}
EXTRAPOLATOR_CHOSEN: dict[str, tuple[int, ...]] = {
    "linear": (1, 3),
    "richardson": (1, 3, 5),
    "exponential": (1, 3),
}
EXTRAPOLATOR_FIXTURE: dict[str, str] = {
    "linear": "linear",
    "richardson": "quadratic",
    "exponential": "exponential",
}
MISSING_FACTORS: tuple[int, ...] = (1, 7)

QMIT_CYCLES: tuple[int, ...] = (2, 8, 30)
QMIT_MZ2_STDS: tuple[tuple[float, ...], ...] = (
    (0.01, 0.02, 0.03),
    (0.04, 0.05, 0.06),
    (0.07, 0.08, 0.09),
)
QMIT_PROBES: tuple[str, ...] = ("P1", "P2", "P3", "P4", "P5", "P6", "P7")

SELECT_TARGET: tuple[float, ...] = (0.52, 0.63, 0.71)
SELECT_DEVIATIONS: tuple[float, ...] = (-0.02, -0.06, -0.20)  # per factor 1, 3, 5
SELECT_MZ2_SCALE = 0.9
SELECT_CANDIDATES: tuple[tuple[int, ...], ...] = ((1, 3), (1, 3, 5))
SELECT_METHODS: tuple[str, ...] = ("linear", "richardson", "exp")

# --------------------------------------------------------------------------- #
# ex5_1 size-extension fixture
# --------------------------------------------------------------------------- #

EXTENSION_SIZES: tuple[int, ...] = (21, 28, 35, 51)
EXTENSION_CYCLES: tuple[int, ...] = (2, 10, 30)
EXTENSION_BACKEND_NAME = "fixture_backend"
EXTENSION_LEDGER = "fixture-ledger.json"
EXTENSION_SAVED_KEY = "trex-35q"
EXTENSION_SAVED_LAYOUT: tuple[int, ...] = tuple(range(80, 115))
EXTENSION_SEARCH_START = 20  # searched layouts are range(20, 20 + n)
EXTENSION_RUN_SECONDS = 7.0
EXTENSION_SPENT_SECONDS = (
    123.0  # includes earlier experiments; deliberately differs from run charges
)
EXTENSION_PROBES: tuple[tuple[str, bool, bool, tuple[int, ...]], ...] = (
    # probe name, use_hardware, include the 21-qubit baseline run, selected factors
    ("patches_local", False, False, (1, 3)),
    ("patches_baseline", False, True, (1, 3)),
    ("layouts_hardware", True, True, (1, 3)),
    ("acquisition_local", False, True, (1, 3)),
    ("acquisition_f13", True, True, (1, 3)),
    ("acquisition_f135", True, True, (1, 3, 5)),
)


def probe_constants() -> dict[str, Any]:
    """Every probe constant as plain JSON data; the server holds an identical function."""
    return {
        "probe_lattice": {
            "n_qubits": PROBE_N_QUBITS,
            "edges": [list(e) for e in PROBE_EDGES],
            "colors": list(PROBE_COLORS),
            "positions": [[q, x, y] for q, (x, y) in sorted(PROBE_POSITIONS.items())],
            "groups": [[list(e) for e in g] for g in PROBE_GROUPS],
            "degrees": list(PROBE_DEGREES),
            "z2_sites": list(PROBE_Z2_SITES),
        },
        "params": list(PARAMS),
        "alt_params": list(ALT_PARAMS),
        "logical_depths": list(LOGICAL_DEPTHS),
        "baseline_counts": [dict(c) for c in BASELINE_COUNTS],
        "readout": {
            "layouts": [list(x) for x in READOUT_LAYOUTS],
            "settings": dict(READOUT_SETTINGS),
            "qubits": list(READOUT_QUBITS),
            "probes": list(READOUT_PROBES),
            "cal_error": READOUT_CAL_ERROR,
        },
        "corrected": {
            "physical": list(CORRECTED_PHYSICAL),
            "counts": [dict(c) for c in CORRECTED_COUNTS],
            "quasi": [
                [[str(k), type(k).__name__, v] for k, v in q.items()]
                for q in CORRECTED_QUASI
            ],
        },
        "fold": {"depths": list(FOLD_DEPTHS), "scales": list(FOLD_SCALES)},
        "zne_extrapolate": {
            "intercept": list(ZNE_INTERCEPT),
            "slope": list(ZNE_SLOPE),
            "calls": [None if c is None else list(c) for c in ZNE_SCALE_CALLS],
        },
        "normalize": [
            [n, [[name, list(q), a] for name, q, a in ops]]
            for n, ops in NORMALIZE_PROBES
        ],
        "backend": {
            "basis": list(BACKEND_BASIS),
            "seed": BACKEND_SEED,
            "layout_limit": LAYOUT_LIMIT,
        },
        "mapomatic": {
            "n_qubits": MAPOMATIC_N_QUBITS,
            "coupling": [list(e) for e in MAPOMATIC_COUPLING],
            "rzz_errors": [
                [list(k), v] for k, v in sorted(MAPOMATIC_RZZ_ERRORS.items())
            ],
            "circuit": [
                MAPOMATIC_CIRCUIT[0],
                [[name, list(q), a] for name, q, a in MAPOMATIC_CIRCUIT[1]],
            ],
        },
        "estimator_allowance": ESTIMATOR_ALLOWANCE,
        "measure": {
            "layout": list(MEASURE_LAYOUT),
            "cycles": list(MEASURE_CYCLES),
            "factors": list(MEASURE_FACTORS),
            "charge": MEASURE_CHARGE,
            "job_id": MEASURE_JOB_ID,
            "probes": list(MEASURE_PROBES),
        },
        "zne": {
            "factors": list(ZNE_FACTORS),
            "cycles": list(ZNE_CYCLES),
            "std": ZNE_STD,
            "mz2_scale": ZNE_MZ2_SCALE,
            "linear": {k: list(v) for k, v in ZNE_LINEAR.items()},
            "quadratic": {k: list(v) for k, v in ZNE_QUADRATIC.items()},
            "exponential": {k: list(v) for k, v in ZNE_EXPONENTIAL.items()},
            "chosen": {k: list(v) for k, v in EXTRAPOLATOR_CHOSEN.items()},
            "fixture": dict(EXTRAPOLATOR_FIXTURE),
            "missing_factors": list(MISSING_FACTORS),
        },
        "qmit": {
            "cycles": list(QMIT_CYCLES),
            "mz2_stds": [list(r) for r in QMIT_MZ2_STDS],
            "probes": list(QMIT_PROBES),
        },
        "select": {
            "target": list(SELECT_TARGET),
            "deviations": list(SELECT_DEVIATIONS),
            "mz2_scale": SELECT_MZ2_SCALE,
            "candidates": [list(c) for c in SELECT_CANDIDATES],
            "methods": list(SELECT_METHODS),
        },
        "extension": {
            "sizes": list(EXTENSION_SIZES),
            "cycles": list(EXTENSION_CYCLES),
            "backend_name": EXTENSION_BACKEND_NAME,
            "ledger": EXTENSION_LEDGER,
            "saved_key": EXTENSION_SAVED_KEY,
            "saved_layout": list(EXTENSION_SAVED_LAYOUT),
            "search_start": EXTENSION_SEARCH_START,
            "run_seconds": EXTENSION_RUN_SECONDS,
            "spent_seconds": EXTENSION_SPENT_SECONDS,
            "probes": [
                [name, hw, base, list(f)] for name, hw, base, f in EXTENSION_PROBES
            ],
        },
    }


# --------------------------------------------------------------------------- #
# Probe objects handed to participant functions
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ProbeLattice:
    """Mirror of the public interface of ``reference.lattice.HeavyHexLattice``."""

    n_qubits: int
    edges: tuple[Edge, ...]
    edge_colors: tuple[int, ...]
    positions: dict[int, tuple[float, float]] = field(default_factory=dict)

    @property
    def n_edges(self) -> int:
        return len(self.edges)

    @property
    def n_colors(self) -> int:
        return len(set(self.edge_colors))

    def color_groups(self) -> list[list[Edge]]:
        groups: dict[int, list[Edge]] = {}
        for e, c in zip(self.edges, self.edge_colors):
            groups.setdefault(c, []).append(e)
        return [groups[c] for c in sorted(groups)]

    def degrees(self) -> list[int]:
        deg = [0] * self.n_qubits
        for i, j in self.edges:
            deg[i] += 1
            deg[j] += 1
        return deg

    def validate(self) -> None:
        incident: dict[int, list[int]] = {q: [] for q in range(self.n_qubits)}
        for (i, j), c in zip(self.edges, self.edge_colors):
            incident[i].append(c)
            incident[j].append(c)
        if max(self.degrees()) > 3 or self.n_colors > 3:
            raise ValueError("not a heavy-hex colouring")
        if any(len(cols) != len(set(cols)) for cols in incident.values()):
            raise ValueError("colour clash")


@dataclass(frozen=True)
class ProbeParams:
    """Mirror of ``FloquetParams``: the three drive angles."""

    theta_x: float
    theta_z: float
    theta_zz: float


def probe_lattice() -> ProbeLattice:
    """A fresh 7-qubit probe lattice."""
    return ProbeLattice(
        n_qubits=PROBE_N_QUBITS,
        edges=PROBE_EDGES,
        edge_colors=PROBE_COLORS,
        positions=dict(PROBE_POSITIONS),
    )


def probe_groups() -> list[list[Edge]]:
    """A fresh copy of the probe colour groups, so a participant cannot mutate the constant."""
    return [list(g) for g in PROBE_GROUPS]


def build_circuit(n_qubits: int, ops: tuple[Op, ...]) -> QuantumCircuit:
    """Build a probe circuit from ``(gate, qubits, angle)`` triples."""
    qc = QuantumCircuit(n_qubits)
    for name, qubits, angle in ops:
        getattr(qc, name)(angle, *qubits)
    return qc


def rzz_probe_backend() -> GenericBackendV2:
    """7-qubit fractional-RZZ backend whose coupling map is exactly the probe lattice."""
    coupling = [list(pair) for a, b in PROBE_EDGES for pair in ((a, b), (b, a))]
    return GenericBackendV2(
        PROBE_N_QUBITS,
        basis_gates=list(BACKEND_BASIS),
        coupling_map=coupling,
        noise_info=False,
        seed=BACKEND_SEED,
    )


class MapomaticProbeBackend(GenericBackendV2):
    """GenericBackendV2 plus the BackendV1-style methods that mapomatic 0.14.0 reads."""

    def __init__(self) -> None:
        super().__init__(
            MAPOMATIC_N_QUBITS,
            basis_gates=list(BACKEND_BASIS),
            coupling_map=[list(e) for e in MAPOMATIC_COUPLING],
            noise_info=False,
            seed=BACKEND_SEED,
        )

    def configuration(self) -> SimpleNamespace:
        return SimpleNamespace(
            basis_gates=list(BACKEND_BASIS), n_qubits=MAPOMATIC_N_QUBITS
        )

    def properties(self) -> SimpleNamespace:
        def gate_error(name: str, qubits: int | list[int]) -> float:
            pair = (qubits,) if isinstance(qubits, int) else tuple(sorted(qubits))
            return MAPOMATIC_RZZ_ERRORS.get(pair, 0.0)

        return SimpleNamespace(gate_error=gate_error, readout_error=lambda qubit: 0.0)
