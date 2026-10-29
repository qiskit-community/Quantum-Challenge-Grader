"""QDC 2026 - C-QAMOO lab (lab_qamoo): one grading function per graded cell of the notebook.

Every function takes the arguments the notebook's grading cell passes. Callables are evaluated
here on fixed probes; backends, pass managers and pooled fronts are reduced to plain data.
"""

import contextlib
import importlib
from collections.abc import Callable
from datetime import datetime
from types import ModuleType
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.providers import BackendV2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import PassManager
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"
_LAB = "lab_qamoo"

# Probe constants; the server keeps its own copy.
NUM_ASSETS = 100
BUILD_DEPTH = 2  # build_parametric is graded at p=2
RUN_DEPTH = 3  # exercise 2.1 is scored on the p=3 front
DEEPER_DEPTH = 4  # exercise 2.2 runs p=4
PROBE_X_QUBIT = 3
PROBE_ZZZ_QUBITS = (0, 1, 2)
PROBE_COEFF = 0.5
_DENSE_PROBE_QUBITS = 12
_MAX_ERROR_CHARS = 300


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


def _error_text(err: BaseException) -> str:
    return f"{type(err).__name__}: {err}"[:_MAX_ERROR_CHARS]


def _level_of(problem: Any) -> int:
    try:
        return int(problem.k)
    except (AttributeError, TypeError, ValueError) as err:
        raise ValueError(
            "Pass a portfolio built with src.Portfolio(K) (it carries its sparsity level as `.k`)."
        ) from err


def _smallest_problem(portfolios: dict) -> Any:
    """`portfolios[min(portfolios)]`, or a ValueError that says what to pass."""
    if not portfolios:
        raise ValueError(
            "Pass the `portfolios` dict of Exercise 1.1: {sparsity level: src.Portfolio(level)}."
        )
    return portfolios[min(portfolios)]


def _qubits(chain: Any) -> list[int]:
    try:
        return [int(qubit) for qubit in chain]
    except (TypeError, ValueError) as err:
        raise ValueError(
            "`best_100q_chain` must be a sequence of qubit indices."
        ) from err


def _notebook_module(name: str) -> ModuleType:
    try:
        return importlib.import_module(name)
    except ImportError as err:
        raise ValueError(
            f"Could not import {name!r} ({err}). Run the notebook from the challenge folder, "
            "where src.py and qopt_best_practices/ are."
        ) from err


def _hamiltonian_probes(hamiltonian: SparsePauliOp) -> list[SparsePauliOp]:
    n = hamiltonian.num_qubits
    return [
        hamiltonian.copy(),
        hamiltonian
        + SparsePauliOp.from_sparse_list([("X", [PROBE_X_QUBIT], PROBE_COEFF)], n),
        hamiltonian
        + SparsePauliOp.from_sparse_list(
            [("ZZZ", list(PROBE_ZZZ_QUBITS), PROBE_COEFF)], n
        ),
    ]


def _evaluate(predicate: Callable[..., Any], probes: list[SparsePauliOp]) -> dict:
    values = []
    for probe in probes:
        try:
            outcome = predicate(probe)
        except Exception as err:  # noqa: BLE001 - reported to the grader as the answer
            return {"values": [], "error": _error_text(err)}
        try:
            values.append(bool(outcome))
        except Exception:  # noqa: BLE001 - reported to the grader as the answer
            return {
                "values": [],
                "error": f"returned {type(outcome).__name__}, not True or False",
            }
    return {"values": values, "error": ""}


@typechecked
def grade_lab_qamoo_ex1_1a(
    is_pure_z: Callable[..., Any],
    is_at_most_weight_2: Callable[..., Any],
    hamiltonian: SparsePauliOp,
) -> None:
    """Submit your 2 predicates and the `hamiltonian` that `to_ising` returned in Exercise 1.1.

    Each predicate is called on `hamiltonian` and on 2 altered copies of it, one with an X term
    and one with a term on 3 qubits.
    """
    if hamiltonian.num_qubits < 4:
        raise ValueError(
            "Pass the 100-qubit `hamiltonian` that `to_ising` returned in Exercise 1.1."
        )
    probes = _hamiltonian_probes(hamiltonian)
    answer = {
        "hamiltonian": hamiltonian,
        "is_pure_z": _evaluate(is_pure_z, probes),
        "is_at_most_weight_2": _evaluate(is_at_most_weight_2, probes),
    }
    _grade(answer, "ex1_1a")


def _probe_cost_layer(problem: Any) -> QuantumCircuit:
    """The unrouted cost layer at weights (1, 1), built as the notebook's `cost_layer` does."""
    src = _notebook_module("src")
    cost_layer_module = _notebook_module("qopt_best_practices.transpilation.cost_layer")
    layer = cost_layer_module.get_cost_layer(src.cost_operator(problem, (1, 1)))
    free = [item for item in layer.parameters if not item.name.startswith("cW[")]
    if len(free) != 1:
        raise ValueError(
            f"Expected 1 cost angle in the cost layer, found {[item.name for item in free]}."
        )
    return layer.assign_parameters({free[0]: Parameter("__theta_cost")}, inplace=False)


@typechecked
def grade_lab_qamoo_ex1_1b(
    route_cost_layer: Callable[..., Any], portfolios: dict[int, Any]
) -> None:
    """Submit your `route_cost_layer` and the `portfolios` dict of Exercise 1.1.

    `route_cost_layer` is called once, on the cost layer of `portfolios[min(portfolios)]`.
    """
    problem = _smallest_problem(portfolios)
    level = _level_of(problem)
    layer = _probe_cost_layer(problem)
    routed, error = None, ""
    try:
        outcome = route_cost_layer(layer, problem.n)
        if isinstance(outcome, QuantumCircuit):
            routed = outcome
        else:
            error = f"route_cost_layer returned {type(outcome).__name__}, not a QuantumCircuit"
    except Exception as err:  # noqa: BLE001 - reported to the grader as the answer
        error = _error_text(err)
    _grade({"level": level, "routed": routed, "error": error}, "ex1_1b")


@typechecked
def grade_lab_qamoo_ex1_1c(
    problem: Any, circ_naive: QuantumCircuit, circ_informed: QuantumCircuit
) -> None:
    """Submit the test `problem`, and `circ_naive` and `circ_informed` (the cost layer before and
    after `route_cost_layer`)."""
    _grade(
        {
            "level": _level_of(problem),
            "circ_naive": circ_naive,
            "circ_informed": circ_informed,
        },
        "ex1_1c",
    )


@typechecked
def grade_lab_qamoo_ex1_1d(
    build_parametric: Callable[..., Any], portfolios: dict[int, Any]
) -> None:
    """Submit your `build_parametric` and the `portfolios` dict.

    It is called at p=2 on `portfolios[min(portfolios)]`, with and without the swap network.
    """
    problem = _smallest_problem(portfolios)
    level = _level_of(problem)
    built: dict[bool, QuantumCircuit | None] = {True: None, False: None}
    error = ""
    for pre_swap in (True, False):
        try:
            circuit = build_parametric(problem, BUILD_DEPTH, pre_swap)
        except Exception as err:  # noqa: BLE001 - reported to the grader as the answer
            error = f"(pre_swap={pre_swap}) {_error_text(err)}"
            break
        if not isinstance(circuit, QuantumCircuit):
            error = f"(pre_swap={pre_swap}) returned {type(circuit).__name__}, not a QuantumCircuit"
            break
        built[pre_swap] = circuit
    answer = {
        "level": level,
        "with_swap": None if error else built[True],
        "without_swap": None if error else built[False],
        "error": error,
    }
    _grade(answer, "ex1_1d")


def _dense_probe() -> QuantumCircuit:
    """A dense 12-qubit circuit: layout and routing have choices to make, so a missing seed shows."""
    probe = QuantumCircuit(_DENSE_PROBE_QUBITS, _DENSE_PROBE_QUBITS)
    probe.h(range(_DENSE_PROBE_QUBITS))
    for first in range(_DENSE_PROBE_QUBITS):
        for second in range(first + 1, _DENSE_PROBE_QUBITS):
            probe.cx(first, second)
    probe.measure(range(_DENSE_PROBE_QUBITS), range(_DENSE_PROBE_QUBITS))
    return probe


def _target_map(backend: BackendV2) -> dict:
    """Operation name -> the qubit tuples it is supported on (None: any)."""
    target = backend.target
    supported = {}
    for name in target.operation_names:
        qargs = target.qargs_for_operation_name(name)
        supported[str(name)] = (
            None if qargs is None else sorted([int(q) for q in item] for item in qargs)
        )
    return supported


@typechecked
def grade_lab_qamoo_ex1_2a(pm_naive: PassManager, backend: BackendV2) -> None:
    """Submit `pm_naive` and `backend`. `pm_naive.run` is called twice on a dense 12-qubit probe."""
    first, second, error = None, None, ""
    try:
        first, second = pm_naive.run(_dense_probe()), pm_naive.run(_dense_probe())
    except Exception as err:  # noqa: BLE001 - reported to the grader as the answer
        first, second, error = None, None, _error_text(err)
    answer = {
        "backend": backend.name,
        "first": first,
        "second": second,
        "error": error,
        "target": _target_map(backend),
    }
    _grade(answer, "ex1_2a")


def _best_chain(backend: BackendV2, size: int = NUM_ASSETS) -> list[int] | None:
    """The backend's own best-layer-fidelity chain of `size` qubits right now, or None."""
    properties = getattr(
        backend, "properties", None
    )  # an IBMBackend method; BackendV2 has none
    if not callable(properties):
        return None
    for read in (
        lambda: properties(refresh=True, datetime=datetime.now()),
        lambda: properties(),
    ):
        # no calibration list, or none readable: the server then grades connectivity only
        with contextlib.suppress(Exception):
            qlists = getattr(read(), "general_qlists", None) or []
            found = [item for item in qlists if item.get("name") == f"lf_{size}"]
            if found:
                return [int(q) for q in found[0]["qubits"]]
    return None


@typechecked
def grade_lab_qamoo_ex1_2b(best_100q_chain: Any, backend: BackendV2) -> None:
    """Submit `best_100q_chain` and `backend`. Grade right after fetching the chain: it is compared
    with the backend's current calibration."""
    if backend.coupling_map is None:
        raise ValueError(
            "`backend` has no coupling map. Pass the IBM backend you selected."
        )
    answer = {
        "backend": backend.name,
        "chain": _qubits(best_100q_chain),
        "edges": [[int(a), int(b)] for a, b in backend.coupling_map.get_edges()],
        "lf_reference": _best_chain(backend),
    }
    _grade(answer, "ex1_2b")


@typechecked
def grade_lab_qamoo_ex1_2c(
    isa_informed: dict[Any, QuantumCircuit], best_100q_chain: Any
) -> None:
    """Submit `isa_informed` (keyed by (p, K)) and `best_100q_chain`."""
    circuits = []
    for key, circuit in isa_informed.items():
        try:
            p, k = (int(x) for x in key)
        except (TypeError, ValueError) as err:
            raise ValueError(
                "`isa_informed` must be keyed by (p, K) tuples, as the notebook builds it."
            ) from err
        try:
            transpile_layout = circuit.layout
            layout = (
                None
                if transpile_layout is None
                else [int(q) for q in transpile_layout.final_index_layout()]
            )
        except Exception:  # noqa: BLE001 - a circuit without a usable layout is graded as drifted
            layout = None
        circuits.append(
            {
                "p": p,
                "k": k,
                "final_layout": layout,
                "depth_2q": int(
                    circuit.depth(lambda instruction: len(instruction.qubits) == 2)
                ),
                "num_2q": int(circuit.num_nonlocal_gates()),
            }
        )
    _grade({"chain": _qubits(best_100q_chain), "circuits": circuits}, "ex1_2c")


def _front_points(summary: Any, where: str) -> list[dict]:
    """The scored fields of a src.pooled_front list."""
    try:
        return [
            {
                "weight_index": int(item["weight_index"]),
                "expected_return": float(item["best_return"]),
                "variance": float(item["best_variance"]),
                "chosen": int(item["best_chosen"]),
            }
            for item in summary
        ]
    except (KeyError, TypeError, ValueError) as err:
        raise ValueError(
            f"{where} must be the list that src.pooled_front returns ({_error_text(err)})."
        ) from err


@typechecked
def grade_lab_qamoo_ex2_1(
    portfolios: dict[int, Any],
    depth_summaries: dict[int, Any],
    references: Any = None,
    random_pick: Any = None,
) -> None:
    """Submit `portfolios` and `depth_summaries` (level -> {3: the pooled p=3 front}).

    `references` and `random_pick` are accepted so the notebook's call works as it is; they do not
    enter the score, which is taken from the p=3 fronts alone.
    """
    fronts = []
    for level in sorted(portfolios):
        summaries = depth_summaries.get(level)
        if not summaries or summaries.get(RUN_DEPTH) is None:
            continue
        points = _front_points(
            summaries[RUN_DEPTH], f"depth_summaries[{level}][{RUN_DEPTH}]"
        )
        fronts.append({"level": int(level), "points": points})
    _grade({"fronts": fronts}, "ex2_1")


def _angle_sets(angles: Any) -> list[dict]:
    """p4_angles[level] ({weight index: (betas, gammas)}) as records; a malformed entry is sent empty."""
    records = []
    for index, entry in angles.items():
        try:
            betas, gammas = (
                (entry.get("betas"), entry.get("gammas"))
                if isinstance(entry, dict)
                else (entry[0], entry[1])
            )
            record = {
                "weight_index": int(index),
                "betas": [float(x) for x in np.asarray(betas, dtype=float).ravel()],
                "gammas": [float(x) for x in np.asarray(gammas, dtype=float).ravel()],
            }
        except (TypeError, ValueError, IndexError, KeyError):
            record = {
                "weight_index": int(index)
                if isinstance(index, (int, np.integer))
                else -1,
                "betas": [],
                "gammas": [],
            }
        records.append(record)
    return records


@typechecked
def grade_lab_qamoo_ex2_2(
    portfolios: dict[int, Any],
    p4_summaries: dict[int, Any],
    p3_summaries: dict[int, Any] | None = None,
    p4_angles: dict[int, Any] | None = None,
    p4_depths: dict[int, Any] | None = None,
) -> None:
    """Submit `portfolios`, `p4_summaries`, `p3_at_p4_weights`, `p4_angles` and `p4_depths`.

    `p3_summaries` is the p=3 run re-pooled at the 3 weights of exercise 2.2 (`p3_at_p4_weights`),
    not the 12-weight `depth_summaries`.
    """
    levels = []
    for level in sorted(portfolios):
        front4 = (p4_summaries.get(level) or {}).get(DEEPER_DEPTH)
        front3 = ((p3_summaries or {}).get(level) or {}).get(RUN_DEPTH)
        angles = None if p4_angles is None else p4_angles.get(level)
        depth = None if p4_depths is None else p4_depths.get(level)
        levels.append(
            {
                "level": int(level),
                "p4_front": None
                if front4 is None
                else _front_points(front4, f"p4_summaries[{level}][{DEEPER_DEPTH}]"),
                "p3_front": None
                if front3 is None
                else _front_points(front3, f"p3_summaries[{level}][{RUN_DEPTH}]"),
                "angles": _angle_sets(angles) if angles else None,
                "depth_2q": None if depth is None else int(depth),
            }
        )
    _grade({"levels": levels}, "ex2_2")
