"""Tests for the ``lab_qamoo`` grading functions (client side).

    python -m pytest client/qc_grader/challenges/qdc_2026/lab_qamoo_test.py

Every function packs the documented keys, with plain ``int`` / ``float`` / ``bool`` / ``str``
values; a callable is evaluated here rather than sent, and what it raises or returns wrongly is
reported as data; bad input raises ``ValueError`` with a fix hint. ``grade_answer`` is patched, so
nothing leaves the machine.

The "participant" is a set of small fakes (a ``GenericBackendV2``, hand-made fronts, a stand-in
for the notebook's ``src`` module), so these tests need nothing of the challenge folder. The
last tests, the ones that take the ``challenge`` fixture, also run the functions on the real
``src`` and ``qopt_best_practices`` and skip when those, or their requirements, are not installed.

Tests that encode an answer use the client's own encoder when it can be imported (always, in a
checkout of Quantum-Challenge-Grader; here, if QC_GRADER_REPO names one) and skip otherwise.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterVector
from qiskit.providers import BackendV2
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from typeguard import CollectionCheckStrategy, TypeCheckError, check_type

from . import lab_qamoo as C


def _load_encoder():
    """The client's own ``to_json``: installed, or from the checkout QC_GRADER_REPO names."""
    try:
        from qc_grader.custom_encoder import to_json

        return to_json
    except ImportError:
        pass
    repo = os.environ.get("QC_GRADER_REPO")
    if not repo:
        return None
    package = Path(repo) / "qc_grader" / "custom_encoder"
    spec = importlib.util.spec_from_file_location(
        "_real_custom_encoder",
        package / "__init__.py",
        submodule_search_locations=[str(package)],
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_real_custom_encoder"] = module
    spec.loader.exec_module(module)
    return module.to_json


to_json = _load_encoder()
needs_encoder = pytest.mark.skipif(
    to_json is None,
    reason="needs the client's encoder (qc_grader.custom_encoder, or QC_GRADER_REPO)",
)

EXERCISES = (
    "ex1_1a",
    "ex1_1b",
    "ex1_1c",
    "ex1_1d",
    "ex1_2a",
    "ex1_2b",
    "ex1_2c",
    "ex2_1",
    "ex2_2",
)
PLAIN_DATA = ("ex1_2b", "ex1_2c", "ex2_1", "ex2_2")
_TARGET = "qc_grader.challenges.qdc_2026.lab_qamoo.grade_answer"
_PAYLOAD_LIMIT = 25 * 1024 * 1024  # the platform's cap on an answer's JSON


def _challenge_modules() -> tuple[Any, Any]:
    """The challenge's own packages, or a skip."""
    try:
        importlib.import_module(
            "docplex.mp.model"
        )  # src.Portfolio builds its Ising form with it
        return importlib.import_module("src"), importlib.import_module("qamoo_GRADER")
    except Exception as err:  # noqa: BLE001 - any missing requirement is a skip
        pytest.skip(
            f"needs the challenge folder and its requirements ({type(err).__name__}: {err})"
        )


# --------------------------------------------------------------------------------------------
# helpers and fakes
# --------------------------------------------------------------------------------------------


def _packed(fn, *args, **kwargs) -> dict:
    """Call a grading function with ``grade_answer`` patched and return the packed answer."""
    with patch(_TARGET) as mock:
        fn(*args, **kwargs)
    assert mock.call_count == 1, (
        "the grading function must call grade_answer exactly once"
    )
    answer, kw = mock.call_args[0][0], mock.call_args[1]
    assert kw == {
        "lab": "lab_qamoo",
        "exercise": kw["exercise"],
        "challenge": "qdc_2026",
    }
    assert kw["exercise"] in EXERCISES
    return {"answer": answer, "exercise": kw["exercise"]}


def _answer(fn, *args, **kwargs) -> dict:
    return _packed(fn, *args, **kwargs)["answer"]


def wrong(value: Any) -> Any:
    """A value of the wrong type, passed through as `Any` so the type checker lets it by."""
    return value


def _is_plain(value: Any) -> bool:
    """Only ``dict`` / ``list`` / ``str`` / ``int`` / ``float`` / ``bool`` / ``None``, nothing else."""
    if isinstance(value, dict):
        return all(type(k) is str and _is_plain(v) for k, v in value.items())
    if isinstance(value, list):
        return all(_is_plain(v) for v in value)
    return value is None or type(value) in (str, int, float, bool)


def _assert_plain_wire(answer: dict) -> None:
    """A plain-data answer is plain Python all the way down, and so survives any encoder."""
    assert _is_plain(answer), (
        "the answer holds a non-plain value (tuple, numpy scalar, ...)"
    )
    assert json.loads(json.dumps(answer)) == answer


def _wire_size(answer: dict) -> int:
    """len(to_json(answer)), after checking it encodes and stays under the platform cap."""
    assert to_json is not None
    wire = to_json(answer)
    assert len(wire) < _PAYLOAD_LIMIT
    return len(wire)


def ising(num_qubits: int = 10) -> SparsePauliOp:
    """A small Ising operator: a field on every qubit and a coupling on every neighbour pair."""
    terms = [("Z", [i], 0.5 + i / 10) for i in range(num_qubits)]
    terms += [("ZZ", [i, i + 1], -0.25) for i in range(num_qubits - 1)]
    return SparsePauliOp.from_sparse_list(terms, num_qubits=num_qubits)


def is_pure_z(operator: SparsePauliOp) -> Any:
    return not np.any(
        operator.paulis.x
    )  # a numpy bool, as the solution notebook returns


def is_at_most_weight_2(operator: SparsePauliOp) -> Any:
    return np.all((operator.paulis.x | operator.paulis.z).sum(axis=1) <= 2)


def problem(level: int = 0, n: int = 10) -> SimpleNamespace:
    return SimpleNamespace(k=level, n=n)


def portfolios(levels=(0, 2, 4)) -> dict[int, SimpleNamespace]:
    return {level: problem(level) for level in levels}


def _fake_cost_layer(num_qubits: int = 6) -> QuantumCircuit:
    """What ``get_cost_layer`` returns: a layer with the 2 weights and 1 free cost angle."""
    weights, gamma = ParameterVector("cW", 2), Parameter("gamma[0]")
    layer = QuantumCircuit(num_qubits)
    for qubit in range(num_qubits - 1):
        layer.rzz(weights[1] * gamma, qubit, qubit + 1)
    layer.rz(weights[0] * gamma, 0)
    return layer


def _fake_modules(name: str) -> SimpleNamespace:
    if name == "src":
        return SimpleNamespace(
            cost_operator=lambda prob, weights: ("operator", prob.k, weights)
        )
    assert name == "qopt_best_practices.transpilation.cost_layer"
    return SimpleNamespace(get_cost_layer=lambda operator: _fake_cost_layer())


def _chain_circuit(num_qubits: int = 6, start: int = 0) -> QuantumCircuit:
    circuit = QuantumCircuit(num_qubits)
    for qubit in range(start, num_qubits - 1, 2):
        circuit.rzz(0.1, qubit, qubit + 1)
    return circuit


def backend_line(num_qubits: int = 14) -> GenericBackendV2:
    return GenericBackendV2(
        num_qubits=num_qubits, coupling_map=CouplingMap.from_line(num_qubits), seed=1
    )


def fake_backend(edges, lists=None, name: str = "fake_backend") -> MagicMock:
    backend = MagicMock(spec=BackendV2)  # spec makes it pass @typechecked
    backend.name = name
    backend.coupling_map.get_edges.return_value = edges
    backend.properties = MagicMock(return_value=SimpleNamespace(general_qlists=lists))
    return backend


def pooled(points: list[tuple[int, float, float, int]]) -> list[dict]:
    """Rows shaped like src.pooled_front's, with numpy values and the extra keys it carries."""
    return [
        {
            "weight_index": np.int64(index),
            "weight_return": np.float64(0.5),
            "weight_variance": np.float64(0.5),
            "best_return": np.float64(ret),
            "best_variance": np.float64(var),
            "best_chosen": np.int64(chosen),
            "shots": 70000,
            "pool": 840000,
        }
        for index, ret, var, chosen in points
    ]


FRONT = pooled([(0, 1.5, 3.0, 2), (9, 4.25, 6.5, 5), (18, 7.0, 11.75, 8)])
FRONT_4 = pooled([(72, 8.0, 12.0, 9), (81, 9.0, 14.5, 10)])


def _all_calls() -> dict[str, dict]:
    """One call per grading function, on the fakes: {exercise: {"answer": ..., "exercise": ...}}."""
    backend, chain = backend_line(), list(range(14))
    with patch.object(C, "_notebook_module", _fake_modules):
        ex1_1b = _packed(C.grade_lab_qamoo_ex1_1b, lambda layer, n: layer, portfolios())
    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=1, seed_transpiler=3
    )
    return {
        "ex1_1a": _packed(
            C.grade_lab_qamoo_ex1_1a, is_pure_z, is_at_most_weight_2, ising()
        ),
        "ex1_1b": ex1_1b,
        "ex1_1c": _packed(
            C.grade_lab_qamoo_ex1_1c, problem(), _chain_circuit(), _chain_circuit()
        ),
        "ex1_1d": _packed(
            C.grade_lab_qamoo_ex1_1d,
            lambda prob, p, pre_swap: QuantumCircuit(3),
            portfolios(),
        ),
        "ex1_2a": _packed(C.grade_lab_qamoo_ex1_2a, pm, backend),
        "ex1_2b": _packed(
            C.grade_lab_qamoo_ex1_2b,
            chain,
            fake_backend(
                [(i, i + 1) for i in range(13)], [{"name": "lf_100", "qubits": chain}]
            ),
        ),
        "ex1_2c": _packed(C.grade_lab_qamoo_ex1_2c, {(3, 0): _informed(chain)}, chain),
        "ex2_1": _packed(
            C.grade_lab_qamoo_ex2_1,
            portfolios(),
            {level: {3: FRONT} for level in (0, 2, 4)},
        ),
        "ex2_2": _packed(
            C.grade_lab_qamoo_ex2_2,
            portfolios(),
            {0: {4: FRONT_4}, 2: {4: FRONT_4}},
            {0: {3: FRONT_4}, 2: {3: FRONT_4}},
            {0: {72: ([0.1] * 4, [0.2] * 4)}, 2: {72: ([0.1] * 4, [0.2] * 4)}},
            {0: 16, 2: 40},
        ),
    }


@pytest.fixture(scope="module")
def calls() -> dict[str, dict]:
    return _all_calls()


@pytest.fixture(scope="module")
def packed(calls: dict[str, dict]) -> dict[str, dict]:
    return {exercise: call["answer"] for exercise, call in calls.items()}


def _informed(layout: list[int] | None = None) -> QuantumCircuit:
    """A 14-qubit circuit transpiled onto the 14-qubit line, pinned to `layout`."""
    manager = generate_preset_pass_manager(
        backend=backend_line(),
        optimization_level=1,
        initial_layout=layout or list(range(14)),
        seed_transpiler=3,
    )
    return manager.run(_chain_circuit(14))


# --------------------------------------------------------------------------------------------
# ids, exports, constants
# --------------------------------------------------------------------------------------------


def test_challenge_and_lab_ids() -> None:
    assert C._CHALLENGE == "qdc_2026"
    assert C._LAB == "lab_qamoo"


def test_every_exercise_has_one_grade_function() -> None:
    names = {name for name in dir(C) if name.startswith("grade_lab_qamoo_")}
    assert names == {f"grade_lab_qamoo_{exercise}" for exercise in EXERCISES}


def test_the_package_exports_every_function_and_the_platform_helpers() -> None:
    # The package is shared by every lab of the challenge, so this lab's names must be
    # among the exports; other labs may add theirs.
    package = importlib.import_module("qc_grader.challenges.qdc_2026")
    assert set(package.__all__) >= {
        "check_progress",
        "join_team",
        *(f"grade_lab_qamoo_{exercise}" for exercise in EXERCISES),
    }
    for name in package.__all__:
        assert callable(getattr(package, name))


def test_each_function_grades_its_own_exercise(calls: dict[str, dict]) -> None:
    assert {exercise: call["exercise"] for exercise, call in calls.items()} == {
        exercise: exercise for exercise in EXERCISES
    }


def test_probe_constants() -> None:
    assert (C.NUM_ASSETS, C.BUILD_DEPTH, C.RUN_DEPTH, C.DEEPER_DEPTH) == (100, 2, 3, 4)
    assert (C.PROBE_X_QUBIT, C.PROBE_ZZZ_QUBITS, C.PROBE_COEFF) == (3, (0, 1, 2), 0.5)


def test_probe_constants_agree_with_the_server() -> None:
    server = _server()
    assert (
        server.NUM_ASSETS,
        server.BUILD_DEPTH,
        server.RUN_DEPTH,
        server.DEEPER_DEPTH,
    ) == (
        C.NUM_ASSETS,
        C.BUILD_DEPTH,
        C.RUN_DEPTH,
        C.DEEPER_DEPTH,
    )
    assert (server.PROBE_X_QUBIT, server.PROBE_ZZZ_QUBITS, server.PROBE_COEFF) == (
        C.PROBE_X_QUBIT,
        C.PROBE_ZZZ_QUBITS,
        C.PROBE_COEFF,
    )


# --------------------------------------------------------------------------------------------
# the contract with the server
# --------------------------------------------------------------------------------------------


def _server() -> Any:
    try:
        return importlib.import_module("validations.qdc_2026.lab_qamoo")
    except ImportError:
        pytest.skip("the server validators are not importable here")


_SERVER_TYPES = {
    "ex1_1a": "Ex1_1aAnswer",
    "ex1_1b": "Ex1_1bAnswer",
    "ex1_1c": "Ex1_1cAnswer",
    "ex1_1d": "Ex1_1dAnswer",
    "ex1_2a": "Ex1_2aAnswer",
    "ex1_2b": "Ex1_2bAnswer",
    "ex1_2c": "Ex1_2cAnswer",
    "ex2_1": "Ex2_1Answer",
    "ex2_2": "Ex2_2Answer",
}


@pytest.mark.parametrize("exercise", EXERCISES)
def test_packed_answer_has_the_servers_keys_and_types(
    exercise: str, packed: dict[str, dict]
) -> None:
    """Typeguard on the server checks exactly this: keys, nesting and types, every item."""
    server = _server()
    answer = packed[exercise]
    expected = getattr(server, _SERVER_TYPES[exercise])
    check_type(
        answer, expected, collection_check_strategy=CollectionCheckStrategy.ALL_ITEMS
    )
    assert set(answer) == set(expected.__annotations__)


@pytest.mark.parametrize("exercise", PLAIN_DATA)
def test_plain_data_answers_are_plain(exercise: str, packed: dict[str, dict]) -> None:
    _assert_plain_wire(packed[exercise])


@needs_encoder
@pytest.mark.parametrize("exercise", EXERCISES)
def test_every_packed_answer_encodes_and_stays_small(
    exercise: str, packed: dict[str, dict]
) -> None:
    assert _wire_size(packed[exercise]) < 2_000_000


# --------------------------------------------------------------------------------------------
# exercise 1.1a: the 2 predicates
# --------------------------------------------------------------------------------------------


def test_ex1_1a_packs_the_hamiltonian_and_3_plain_results_per_predicate() -> None:
    h = ising()
    answer = _answer(C.grade_lab_qamoo_ex1_1a, is_pure_z, is_at_most_weight_2, h)
    assert set(answer) == {"hamiltonian", "is_pure_z", "is_at_most_weight_2"}
    assert answer["hamiltonian"] is h
    assert answer["is_pure_z"] == {"values": [True, False, True], "error": ""}
    assert answer["is_at_most_weight_2"] == {"values": [True, True, False], "error": ""}
    for outcome in (answer["is_pure_z"], answer["is_at_most_weight_2"]):
        assert all(type(v) is bool for v in outcome["values"])


def test_ex1_1a_calls_the_predicates_on_the_hamiltonian_and_two_altered_copies() -> (
    None
):
    h, seen = ising(), []
    _answer(
        C.grade_lab_qamoo_ex1_1a,
        lambda op: seen.append(op) or True,
        is_at_most_weight_2,
        h,
    )
    assert len(seen) == 3
    assert seen[0] == h and seen[0] is not h
    assert seen[1].size == h.size + 1
    assert seen[1].paulis.x.sum() == 1  # one X term, on one qubit
    assert int(np.flatnonzero(seen[1].paulis.x.any(axis=0))[0]) == C.PROBE_X_QUBIT
    assert seen[2].size == h.size + 1
    heavy = (seen[2].paulis.z.sum(axis=1) == 3).nonzero()[0]
    assert len(heavy) == 1
    assert list(np.flatnonzero(seen[2].paulis.z[heavy[0]])) == list(C.PROBE_ZZZ_QUBITS)


def test_ex1_1a_a_predicate_that_edits_its_argument_cannot_change_the_submitted_operator() -> (
    None
):
    h = ising()
    before = h.copy()

    def vandal(op: SparsePauliOp) -> bool:
        op.coeffs[:] = 99.0
        return True

    answer = _answer(C.grade_lab_qamoo_ex1_1a, vandal, vandal, h)
    assert answer["hamiltonian"] == before


def test_ex1_1a_a_predicate_that_raises_is_reported_as_data() -> None:
    def broken(op: SparsePauliOp) -> bool:
        raise ValueError("boom")

    answer = _answer(C.grade_lab_qamoo_ex1_1a, broken, is_at_most_weight_2, ising())
    assert answer["is_pure_z"] == {"values": [], "error": "ValueError: boom"}
    assert answer["is_at_most_weight_2"]["error"] == ""


def test_ex1_1a_a_predicate_that_returns_an_array_is_reported_as_data() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex1_1a, lambda op: op.paulis.x, is_at_most_weight_2, ising()
    )
    assert answer["is_pure_z"]["values"] == []
    assert "returned ndarray" in answer["is_pure_z"]["error"]


def test_ex1_1a_a_predicate_that_returns_nothing_counts_as_false() -> None:
    """An unfinished `## YOUR CODE HERE` returns None."""
    answer = _answer(
        C.grade_lab_qamoo_ex1_1a, lambda op: None, lambda op: None, ising()
    )
    assert answer["is_pure_z"] == {"values": [False] * 3, "error": ""}


def test_ex1_1a_long_error_text_is_cut() -> None:
    def broken(op: SparsePauliOp) -> bool:
        raise ValueError("x" * 5000)

    answer = _answer(C.grade_lab_qamoo_ex1_1a, broken, broken, ising())
    assert len(answer["is_pure_z"]["error"]) == C._MAX_ERROR_CHARS


def test_ex1_1a_rejects_a_hamiltonian_that_is_too_small_with_a_hint() -> None:
    with pytest.raises(ValueError, match="100-qubit"):
        C.grade_lab_qamoo_ex1_1a(is_pure_z, is_at_most_weight_2, ising(3))


def test_ex1_1a_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1a(is_pure_z, is_at_most_weight_2, wrong("hamiltonian"))
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1a(wrong(None), is_at_most_weight_2, ising())


@needs_encoder
def test_ex1_1a_the_answer_encodes_and_keeps_its_terms() -> None:
    h = ising(100)
    answer = _answer(C.grade_lab_qamoo_ex1_1a, is_pure_z, is_at_most_weight_2, h)
    assert 10_000 < _wire_size(answer) < 200_000


# --------------------------------------------------------------------------------------------
# exercise 1.1b: the edge colouring
# --------------------------------------------------------------------------------------------


def test_ex1_1b_calls_route_cost_layer_once_on_the_probe_layer_of_the_smallest_level() -> (
    None
):
    calls = []

    def route(layer: QuantumCircuit, n: int) -> QuantumCircuit:
        calls.append((layer, n))
        return layer

    with patch.object(C, "_notebook_module", _fake_modules):
        answer = _answer(C.grade_lab_qamoo_ex1_1b, route, portfolios((2, 0, 4)))
    assert len(calls) == 1
    layer, n = calls[0]
    assert n == 10
    assert sorted(p.name for p in layer.parameters) == [
        "__theta_cost",
        "cW[0]",
        "cW[1]",
    ]
    assert set(answer) == {"level", "routed", "error"}
    assert answer["level"] == 0 and type(answer["level"]) is int
    assert answer["routed"] is layer
    assert answer["error"] == ""


def test_ex1_1b_a_function_that_raises_is_reported_as_data() -> None:
    def route(layer: QuantumCircuit, n: int) -> QuantumCircuit:
        raise KeyError((4, 5))

    with patch.object(C, "_notebook_module", _fake_modules):
        answer = _answer(C.grade_lab_qamoo_ex1_1b, route, portfolios())
    assert answer["routed"] is None
    assert answer["error"] == "KeyError: (4, 5)"


def test_ex1_1b_a_function_that_returns_something_else_is_reported_as_data() -> None:
    with patch.object(C, "_notebook_module", _fake_modules):
        answer = _answer(C.grade_lab_qamoo_ex1_1b, lambda layer, n: None, portfolios())
    assert answer["routed"] is None
    assert "NoneType" in answer["error"] and "not a QuantumCircuit" in answer["error"]


def test_ex1_1b_an_empty_portfolios_dict_gets_a_hint() -> None:
    with pytest.raises(ValueError, match="portfolios"):
        C.grade_lab_qamoo_ex1_1b(lambda layer, n: layer, {})


def test_ex1_1b_a_portfolio_without_a_level_gets_a_hint() -> None:
    with (
        patch.object(C, "_notebook_module", _fake_modules),
        pytest.raises(ValueError, match="src.Portfolio"),
    ):
        C.grade_lab_qamoo_ex1_1b(lambda layer, n: layer, {0: SimpleNamespace(n=10)})


def test_ex1_1b_a_missing_challenge_package_gets_a_hint() -> None:
    with pytest.raises(ValueError, match="challenge folder"):
        C._notebook_module("a_module_the_challenge_does_not_have")


def test_ex1_1b_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1b(wrong("route"), portfolios())
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1b(lambda layer, n: layer, wrong([problem()]))


def test_ex1_1b_the_fake_layer_has_exactly_one_free_angle_or_the_client_refuses() -> (
    None
):
    def two_angles(operator: Any) -> QuantumCircuit:
        circuit = QuantumCircuit(2)
        circuit.rz(Parameter("a") + Parameter("b"), 0)
        return circuit

    def modules(name: str) -> SimpleNamespace:
        if name == "src":
            return _fake_modules(name)
        return SimpleNamespace(get_cost_layer=two_angles)

    with (
        patch.object(C, "_notebook_module", modules),
        pytest.raises(ValueError, match="1 cost angle"),
    ):
        C.grade_lab_qamoo_ex1_1b(lambda layer, n: layer, portfolios())


# --------------------------------------------------------------------------------------------
# exercise 1.1c: the cost layer before and after routing
# --------------------------------------------------------------------------------------------


def test_ex1_1c_packs_the_level_and_both_circuits() -> None:
    naive, informed = _chain_circuit(), _chain_circuit(start=1)
    answer = _answer(C.grade_lab_qamoo_ex1_1c, problem(2), naive, informed)
    assert set(answer) == {"level", "circ_naive", "circ_informed"}
    assert answer["level"] == 2 and type(answer["level"]) is int
    assert answer["circ_naive"] is naive and answer["circ_informed"] is informed


def test_ex1_1c_the_level_may_arrive_as_a_numpy_integer() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex1_1c,
        SimpleNamespace(k=np.int64(4)),
        _chain_circuit(),
        _chain_circuit(),
    )
    assert answer["level"] == 4 and type(answer["level"]) is int


def test_ex1_1c_a_problem_without_a_level_gets_a_hint() -> None:
    with pytest.raises(ValueError, match="src.Portfolio"):
        C.grade_lab_qamoo_ex1_1c(SimpleNamespace(), _chain_circuit(), _chain_circuit())
    with pytest.raises(ValueError, match="src.Portfolio"):
        C.grade_lab_qamoo_ex1_1c("portfolio", _chain_circuit(), _chain_circuit())


def test_ex1_1c_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1c(problem(), wrong(99), _chain_circuit())
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1c(problem(), _chain_circuit(), wrong(None))


# --------------------------------------------------------------------------------------------
# exercise 1.1d: build_parametric
# --------------------------------------------------------------------------------------------


def test_ex1_1d_builds_at_p2_with_and_without_the_swap_network() -> None:
    calls = []

    def build(prob: Any, p: int, pre_swap: bool) -> QuantumCircuit:
        calls.append((prob.k, p, pre_swap))
        return QuantumCircuit(2 if pre_swap else 3)

    answer = _answer(C.grade_lab_qamoo_ex1_1d, build, portfolios((4, 2, 0)))
    assert calls == [(0, 2, True), (0, 2, False)]
    assert set(answer) == {"level", "with_swap", "without_swap", "error"}
    assert answer["level"] == 0
    assert (
        answer["with_swap"].num_qubits == 2 and answer["without_swap"].num_qubits == 3
    )
    assert answer["error"] == ""


def test_ex1_1d_a_function_that_raises_is_reported_as_data_without_circuits() -> None:
    def build(prob: Any, p: int, pre_swap: bool) -> QuantumCircuit:
        if not pre_swap:
            raise RuntimeError("no registers yet")
        return QuantumCircuit(2)

    answer = _answer(C.grade_lab_qamoo_ex1_1d, build, portfolios())
    assert answer["with_swap"] is None and answer["without_swap"] is None
    assert answer["error"] == "(pre_swap=False) RuntimeError: no registers yet"


def test_ex1_1d_a_function_that_returns_something_else_is_reported_as_data() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex1_1d, lambda prob, p, pre_swap: None, portfolios()
    )
    assert answer["with_swap"] is None
    assert answer["error"].startswith("(pre_swap=True) returned NoneType")


def test_ex1_1d_an_empty_portfolios_dict_gets_a_hint() -> None:
    with pytest.raises(ValueError, match="portfolios"):
        C.grade_lab_qamoo_ex1_1d(lambda prob, p, pre_swap: QuantumCircuit(1), {})


def test_ex1_1d_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1d(wrong("build"), portfolios())
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_1d(
            lambda prob, p, pre_swap: QuantumCircuit(1), wrong("portfolios")
        )


# --------------------------------------------------------------------------------------------
# exercise 1.2a: the naive pass manager
# --------------------------------------------------------------------------------------------


def test_ex1_2a_runs_the_pass_manager_twice_on_a_dense_probe() -> None:
    backend = backend_line()
    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=1, seed_transpiler=5
    )
    probes, original = [], type(pm).run

    def spy(
        self: Any, circuit: QuantumCircuit, *args: Any, **kwargs: Any
    ) -> QuantumCircuit:
        probes.append(circuit)
        return original(self, circuit, *args, **kwargs)

    with patch.object(type(pm), "run", spy):
        answer = _answer(C.grade_lab_qamoo_ex1_2a, pm, backend)
    assert len(probes) == 2
    assert (
        probes[0] is not probes[1]
    )  # a fresh probe each time: the first run cannot spoil the second
    probe = probes[0]
    assert probe.num_qubits == probe.num_clbits == 12
    assert probe.count_ops()["cx"] == 66  # all pairs of 12 qubits
    assert set(answer) == {"backend", "first", "second", "error", "target"}
    assert answer["backend"] == backend.name
    assert answer["error"] == ""
    assert isinstance(answer["first"], QuantumCircuit) and isinstance(
        answer["second"], QuantumCircuit
    )
    assert answer["first"] == answer["second"]  # seeded: the same circuit twice


def test_ex1_2a_the_target_is_plain_data_the_server_can_check_against() -> None:
    backend = backend_line()
    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=0, seed_transpiler=5
    )
    answer = _answer(C.grade_lab_qamoo_ex1_2a, pm, backend)
    target = answer["target"]
    assert _is_plain(target)
    assert set(target) == set(backend.target.operation_names)
    assert target["cx"] is not None and all(
        len(q) == 2 and all(type(i) is int for i in q) for q in target["cx"]
    )
    assert [0, 1] in target["cx"] and [0, 13] not in target["cx"]
    assert target["rz"] == [[q] for q in range(14)]
    for instruction in answer["first"].data:
        if instruction.operation.name not in ("barrier", "delay"):
            assert instruction.operation.name in target


def test_ex1_2a_a_pass_manager_that_raises_is_reported_as_data() -> None:
    pm = generate_preset_pass_manager(backend=backend_line(), optimization_level=0)
    with patch.object(type(pm), "run", side_effect=RuntimeError("no layout")):
        answer = _answer(C.grade_lab_qamoo_ex1_2a, pm, backend_line())
    assert answer["first"] is None and answer["second"] is None
    assert answer["error"] == "RuntimeError: no layout"


def test_ex1_2a_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_2a(wrong("pm"), backend_line())
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_2a(
            generate_preset_pass_manager(optimization_level=0), wrong("ibm_fez")
        )


@needs_encoder
def test_ex1_2a_the_answer_encodes() -> None:
    backend = backend_line()
    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=1, seed_transpiler=5
    )
    assert _wire_size(_answer(C.grade_lab_qamoo_ex1_2a, pm, backend)) < 2_000_000


# --------------------------------------------------------------------------------------------
# exercise 1.2b: the 100-qubit chain
# --------------------------------------------------------------------------------------------


def test_ex1_2b_packs_plain_ints_and_the_calibration_chain() -> None:
    edges = [(0, 1), (1, 2), (2, 3)]
    backend = fake_backend(
        edges,
        [
            {"name": "lf_50", "qubits": [9]},
            {"name": "lf_100", "qubits": [np.int64(3), 2, 1, 0]},
        ],
    )
    chain = [np.int64(0), np.int32(1), 2, 3]
    answer = _answer(C.grade_lab_qamoo_ex1_2b, chain, backend)
    assert set(answer) == {"backend", "chain", "edges", "lf_reference"}
    assert answer == {
        "backend": "fake_backend",
        "chain": [0, 1, 2, 3],
        "edges": [[0, 1], [1, 2], [2, 3]],
        "lf_reference": [3, 2, 1, 0],
    }
    _assert_plain_wire(answer)


def test_ex1_2b_reads_the_calibration_fresh_and_names_the_time() -> None:
    backend = fake_backend([(0, 1)], [{"name": "lf_100", "qubits": [0, 1]}])
    _answer(C.grade_lab_qamoo_ex1_2b, [0, 1], backend)
    first_call = backend.properties.call_args_list[0]
    assert first_call.kwargs["refresh"] is True
    assert "datetime" in first_call.kwargs


def test_ex1_2b_falls_back_to_the_cached_calibration() -> None:
    backend = fake_backend([(0, 1)], None)
    lists = [{"name": "lf_100", "qubits": [1, 0]}]

    def properties(**kwargs: Any) -> Any:
        if kwargs:
            raise TypeError("no refresh on this backend")
        return SimpleNamespace(general_qlists=lists)

    backend.properties.side_effect = properties
    assert _answer(C.grade_lab_qamoo_ex1_2b, [0, 1], backend)["lf_reference"] == [1, 0]


def test_ex1_2b_without_a_list_the_reference_is_none() -> None:
    for lists in (None, [], [{"name": "lf_50", "qubits": [0]}]):
        backend = fake_backend([(0, 1)], lists)
        assert (
            _answer(C.grade_lab_qamoo_ex1_2b, [0, 1], backend)["lf_reference"] is None
        )
    backend = fake_backend([(0, 1)], None)
    backend.properties.side_effect = RuntimeError("offline")
    assert _answer(C.grade_lab_qamoo_ex1_2b, [0, 1], backend)["lf_reference"] is None


def test_ex1_2b_a_chain_that_is_not_a_sequence_of_qubits_gets_a_hint() -> None:
    backend = fake_backend([(0, 1)], None)
    for chain in (7, None, ["a", "b"]):
        with pytest.raises(ValueError, match="best_100q_chain"):
            C.grade_lab_qamoo_ex1_2b(chain, backend)


def test_ex1_2b_a_backend_without_a_coupling_map_gets_a_hint() -> None:
    backend = fake_backend([], None)
    backend.coupling_map = None
    with pytest.raises(ValueError, match="coupling map"):
        C.grade_lab_qamoo_ex1_2b([0, 1], backend)


def test_ex1_2b_a_string_backend_is_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_2b([0, 1], wrong("ibm_fez"))


def test_ex1_2b_a_real_sized_answer_is_small() -> None:
    edges = [(i, i + 1) for i in range(155)] + [(i + 1, i) for i in range(155)]
    backend = fake_backend(edges, [{"name": "lf_100", "qubits": list(range(100))}])
    answer = _answer(C.grade_lab_qamoo_ex1_2b, list(range(100)), backend)
    assert len(json.dumps(answer)) < 20_000


# --------------------------------------------------------------------------------------------
# exercise 1.2c: the informed transpilation
# --------------------------------------------------------------------------------------------


def test_ex1_2c_packs_one_record_per_key_with_the_layout_and_the_2_qubit_cost() -> None:
    chain = list(range(14))
    isa = _informed(chain)
    answer = _answer(C.grade_lab_qamoo_ex1_2c, {(1, 0): isa, (3, 4): isa}, chain)
    assert set(answer) == {"chain", "circuits"}
    assert answer["chain"] == chain
    assert [(c["p"], c["k"]) for c in answer["circuits"]] == [(1, 0), (3, 4)]
    for record in answer["circuits"]:
        assert set(record) == {"p", "k", "final_layout", "depth_2q", "num_2q"}
        assert record["final_layout"] == chain
        assert record["num_2q"] == isa.num_nonlocal_gates()
        assert record["depth_2q"] == isa.depth(
            lambda instruction: len(instruction.qubits) == 2
        )
    _assert_plain_wire(answer)


def test_ex1_2c_the_chain_may_hold_numpy_integers() -> None:
    chain = [np.int64(q) for q in range(14)]
    answer = _answer(C.grade_lab_qamoo_ex1_2c, {(1, 0): _informed()}, chain)
    assert answer["chain"] == list(range(14)) and _is_plain(answer)


def test_ex1_2c_keys_may_hold_numpy_integers() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex1_2c,
        {(np.int64(2), np.int64(4)): _informed()},
        list(range(14)),
    )
    assert (answer["circuits"][0]["p"], answer["circuits"][0]["k"]) == (2, 4)
    assert _is_plain(answer)


def test_ex1_2c_a_circuit_without_a_layout_is_sent_with_none() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex1_2c, {(1, 0): _chain_circuit(14)}, list(range(14))
    )
    assert answer["circuits"][0]["final_layout"] is None


def test_ex1_2c_a_layout_that_drifted_is_sent_as_it_is() -> None:
    shifted = _informed([1, 0, *range(2, 14)])
    answer = _answer(C.grade_lab_qamoo_ex1_2c, {(1, 0): shifted}, list(range(14)))
    assert answer["circuits"][0]["final_layout"] != list(range(14))


def test_ex1_2c_keys_that_are_not_p_k_pairs_get_a_hint() -> None:
    for bad_key in ("a", 7, (1,), (1, "x")):
        with pytest.raises(ValueError, match="keyed by"):
            C.grade_lab_qamoo_ex1_2c({bad_key: _chain_circuit()}, [0, 1])


def test_ex1_2c_a_chain_that_is_not_qubits_gets_a_hint() -> None:
    with pytest.raises(ValueError, match="best_100q_chain"):
        C.grade_lab_qamoo_ex1_2c({(1, 0): _chain_circuit()}, 5)


def test_ex1_2c_an_empty_dict_is_sent_empty_for_the_server_to_explain() -> None:
    assert _answer(C.grade_lab_qamoo_ex1_2c, {}, [0, 1]) == {
        "chain": [0, 1],
        "circuits": [],
    }


def test_ex1_2c_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_2c(wrong({(1, 0): "circuit"}), [0, 1])
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex1_2c(wrong([_chain_circuit()]), [0, 1])


# --------------------------------------------------------------------------------------------
# exercise 2.1: the p=3 fronts
# --------------------------------------------------------------------------------------------


def test_ex2_1_packs_only_the_scored_fields_as_plain_numbers() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex2_1,
        portfolios(),
        {level: {3: FRONT} for level in (0, 2, 4)},
        {"reference": "ignored"},
        {"random": "ignored"},
    )
    assert set(answer) == {"fronts"}
    assert [entry["level"] for entry in answer["fronts"]] == [0, 2, 4]
    for entry in answer["fronts"]:
        assert set(entry) == {"level", "points"}
        assert entry["points"] == [
            {"weight_index": 0, "expected_return": 1.5, "variance": 3.0, "chosen": 2},
            {"weight_index": 9, "expected_return": 4.25, "variance": 6.5, "chosen": 5},
            {
                "weight_index": 18,
                "expected_return": 7.0,
                "variance": 11.75,
                "chosen": 8,
            },
        ]
    _assert_plain_wire(answer)


def test_ex2_1_the_last_two_arguments_are_accepted_and_unused() -> None:
    plain = _answer(C.grade_lab_qamoo_ex2_1, portfolios(), {0: {3: FRONT}})
    full = _answer(
        C.grade_lab_qamoo_ex2_1, portfolios(), {0: {3: FRONT}}, object(), object()
    )
    assert plain == full


def test_ex2_1_a_level_without_a_p3_front_is_left_out() -> None:
    summaries = {0: {3: FRONT}, 2: {}, 4: {1: FRONT}}
    answer = _answer(C.grade_lab_qamoo_ex2_1, portfolios(), summaries)
    assert [entry["level"] for entry in answer["fronts"]] == [0]
    answer = _answer(C.grade_lab_qamoo_ex2_1, portfolios(), {})
    assert answer == {"fronts": []}


def test_ex2_1_an_empty_front_is_sent_empty_for_the_server_to_explain() -> None:
    answer = _answer(C.grade_lab_qamoo_ex2_1, portfolios((0,)), {0: {3: []}})
    assert answer == {"fronts": [{"level": 0, "points": []}]}


def test_ex2_1_levels_follow_the_portfolios_dict_in_sorted_order() -> None:
    summaries = {level: {3: FRONT} for level in (4, 0, 2)}
    answer = _answer(
        C.grade_lab_qamoo_ex2_1,
        {4: problem(4), 0: problem(0), 2: problem(2)},
        summaries,
    )
    assert [entry["level"] for entry in answer["fronts"]] == [0, 2, 4]


def test_ex2_1_a_summary_that_is_not_a_pooled_front_gets_a_hint() -> None:
    with pytest.raises(
        ValueError, match=r"depth_summaries\[0\]\[3\].*src.pooled_front"
    ):
        C.grade_lab_qamoo_ex2_1(portfolios((0,)), {0: {3: [{"best_return": 1.0}]}})
    with pytest.raises(ValueError, match="src.pooled_front"):
        C.grade_lab_qamoo_ex2_1(portfolios((0,)), {0: {3: 5}})


def test_ex2_1_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex2_1(wrong([0, 2]), {0: {3: FRONT}})
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex2_1(portfolios(), wrong([FRONT]))


def test_ex2_1_a_realistic_answer_is_small() -> None:
    rng = np.random.default_rng(0)
    points = [
        (int(i % 100), float(r), float(v), int(c))
        for i, (r, v, c) in enumerate(
            zip(rng.random(500), rng.random(500), rng.integers(0, 100, 500))
        )
    ]
    answer = _answer(
        C.grade_lab_qamoo_ex2_1,
        portfolios(),
        {level: {3: pooled(points)} for level in (0, 2, 4)},
    )
    assert len(json.dumps(answer)) < 400_000


# --------------------------------------------------------------------------------------------
# exercise 2.2: p=4
# --------------------------------------------------------------------------------------------

ANGLES = {
    72: ([0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]),
    81: (np.array([0.1] * 4), [np.float64(0.2)] * 4),
}


def test_ex2_2_packs_fronts_angles_and_depth_per_level() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex2_2,
        portfolios((0, 2)),
        {0: {4: FRONT_4}, 2: {4: FRONT_4}},
        {0: {3: FRONT}, 2: {3: FRONT}},
        {0: ANGLES, 2: ANGLES},
        {0: np.int64(16), 2: 40},
    )
    assert set(answer) == {"levels"}
    assert [entry["level"] for entry in answer["levels"]] == [0, 2]
    for entry in answer["levels"]:
        assert set(entry) == {"level", "p4_front", "p3_front", "angles", "depth_2q"}
        assert [p["weight_index"] for p in entry["p4_front"]] == [72, 81]
        assert [p["weight_index"] for p in entry["p3_front"]] == [0, 9, 18]
        assert entry["angles"] == [
            {
                "weight_index": 72,
                "betas": [0.1, 0.2, 0.3, 0.4],
                "gammas": [0.5, 0.6, 0.7, 0.8],
            },
            {"weight_index": 81, "betas": [0.1] * 4, "gammas": [0.2] * 4},
        ]
    assert [entry["depth_2q"] for entry in answer["levels"]] == [16, 40]
    _assert_plain_wire(answer)


def test_ex2_2_angles_may_be_dicts_or_pairs_of_arrays() -> None:
    entries = {
        72: {"betas": np.arange(4.0), "gammas": [1, 2, 3, 4]},
        81: (np.zeros(4), np.ones(4)),
    }
    answer = _answer(
        C.grade_lab_qamoo_ex2_2,
        portfolios((0,)),
        {0: {4: FRONT_4}},
        None,
        {0: entries},
        {0: 16},
    )
    assert answer["levels"][0]["angles"] == [
        {
            "weight_index": 72,
            "betas": [0.0, 1.0, 2.0, 3.0],
            "gammas": [1.0, 2.0, 3.0, 4.0],
        },
        {"weight_index": 81, "betas": [0.0] * 4, "gammas": [1.0] * 4},
    ]
    assert _is_plain(answer)


def test_ex2_2_a_malformed_angle_entry_is_sent_empty_so_the_server_can_say_so() -> None:
    entries = {72: "oops", 81: ([0.1] * 4, ["x"] * 4), 90: ANGLES[72]}
    answer = _answer(
        C.grade_lab_qamoo_ex2_2,
        portfolios((0,)),
        {0: {4: FRONT_4}},
        None,
        {0: entries},
        {0: 16},
    )
    sets = {a["weight_index"]: a for a in answer["levels"][0]["angles"]}
    assert sets[72] == {"weight_index": 72, "betas": [], "gammas": []}
    assert sets[81] == {"weight_index": 81, "betas": [], "gammas": []}
    assert sets[90]["betas"] == [0.1, 0.2, 0.3, 0.4]


def test_ex2_2_missing_parts_are_sent_as_none() -> None:
    answer = _answer(C.grade_lab_qamoo_ex2_2, portfolios((0, 2)), {0: {4: FRONT_4}})
    assert answer["levels"][0] == {
        "level": 0,
        "p4_front": [
            {"weight_index": 72, "expected_return": 8.0, "variance": 12.0, "chosen": 9},
            {
                "weight_index": 81,
                "expected_return": 9.0,
                "variance": 14.5,
                "chosen": 10,
            },
        ],
        "p3_front": None,
        "angles": None,
        "depth_2q": None,
    }
    assert answer["levels"][1] == {
        "level": 2,
        "p4_front": None,
        "p3_front": None,
        "angles": None,
        "depth_2q": None,
    }


def test_ex2_2_empty_angles_are_sent_as_none() -> None:
    answer = _answer(
        C.grade_lab_qamoo_ex2_2,
        portfolios((0,)),
        {0: {4: FRONT_4}},
        None,
        {0: {}},
        {0: 16},
    )
    assert answer["levels"][0]["angles"] is None


def test_ex2_2_every_level_of_portfolios_is_listed_so_the_server_can_say_which_are_not_scored() -> (
    None
):
    answer = _answer(C.grade_lab_qamoo_ex2_2, portfolios(), {0: {4: FRONT_4}})
    assert [entry["level"] for entry in answer["levels"]] == [0, 2, 4]


def test_ex2_2_the_p3_baseline_is_the_re_pooled_one_and_the_12_weight_front_is_not_used() -> (
    None
):
    answer = _answer(
        C.grade_lab_qamoo_ex2_2, portfolios((0,)), {0: {4: FRONT_4}}, {0: {3: FRONT_4}}
    )
    assert [p["weight_index"] for p in answer["levels"][0]["p3_front"]] == [72, 81]


def test_ex2_2_a_summary_that_is_not_a_pooled_front_gets_a_hint() -> None:
    with pytest.raises(ValueError, match=r"p4_summaries\[0\]\[4\]"):
        C.grade_lab_qamoo_ex2_2(portfolios((0,)), {0: {4: [{"best_return": 1.0}]}})
    with pytest.raises(ValueError, match=r"p3_summaries\[0\]\[3\]"):
        C.grade_lab_qamoo_ex2_2(portfolios((0,)), {0: {4: FRONT_4}}, {0: {3: ["row"]}})


def test_ex2_2_wrong_types_are_rejected() -> None:
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex2_2(portfolios(), wrong("summaries"))
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex2_2(portfolios(), {0: {4: FRONT_4}}, wrong("p3"))
    with pytest.raises(TypeCheckError):
        C.grade_lab_qamoo_ex2_2(portfolios(), {0: {4: FRONT_4}}, None, wrong([1]), None)


# --------------------------------------------------------------------------------------------
# against the challenge's own packages (skipped without them)
# --------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def challenge() -> tuple[Any, Any]:
    return _challenge_modules()


def test_the_probe_cost_layer_is_the_prototypes_layer(
    challenge: tuple[Any, Any],
) -> None:
    src, prototype = challenge
    prob = src.Portfolio(0)
    layer = C._probe_cost_layer(prob)
    reference = prototype.GRADER_cost_layer(prob, (1, 1), prototype._cost_angle())
    assert sorted(p.name for p in layer.parameters) == sorted(
        p.name for p in reference.parameters
    )
    assert prototype._bind_by_name(layer) == prototype._bind_by_name(reference)


def test_ex1_1b_on_the_real_instance_packs_the_reference_routing(
    challenge: tuple[Any, Any],
) -> None:
    src, prototype = challenge
    answer = _answer(
        C.grade_lab_qamoo_ex1_1b,
        lambda layer, n: prototype.GRADER_route_cost_layer(layer, n),
        {0: src.Portfolio(0)},
    )
    assert answer["level"] == 0 and answer["error"] == ""
    assert answer["routed"].num_nonlocal_gates() == 99
    assert answer["routed"].depth(lambda instruction: len(instruction.qubits) == 2) == 2


def test_ex1_1d_on_the_real_instance_packs_both_reference_circuits(
    challenge: tuple[Any, Any],
) -> None:
    src, prototype = challenge
    answer = _answer(
        C.grade_lab_qamoo_ex1_1d,
        lambda prob, p, pre_swap: prototype.GRADER_build_parametric(prob, p, pre_swap),
        {0: src.Portfolio(0)},
    )
    assert answer["error"] == ""
    assert answer["with_swap"].num_qubits == answer["without_swap"].num_qubits == 100
    assert answer["with_swap"].num_clbits == 100
    assert {p.name for p in answer["with_swap"].parameters} == {
        "cW[0]",
        "cW[1]",
        "beta[0]",
        "beta[1]",
        "gamma[0]",
        "gamma[1]",
    }


def test_ex1_1a_on_the_real_hamiltonian(challenge: tuple[Any, Any]) -> None:
    pytest.importorskip("qiskit_addon_opt_mapper")
    pytest.importorskip("docplex")
    src, _ = challenge
    # imported by name: the addon is a challenge requirement, not a client dependency
    converters = importlib.import_module("qiskit_addon_opt_mapper.converters")
    translators = importlib.import_module("qiskit_addon_opt_mapper.translators")

    model, _ = src.weighted_sum_model(src.Portfolio(0), 1.0, 1.0)
    problem_op = translators.from_docplex_mp(model)
    qubo = converters.OptimizationProblemToQubo().convert(problem_op)
    hamiltonian, _offset = translators.to_ising(qubo)
    answer = _answer(
        C.grade_lab_qamoo_ex1_1a, is_pure_z, is_at_most_weight_2, hamiltonian
    )
    assert answer["hamiltonian"].num_qubits == 100
    assert answer["is_pure_z"]["values"] == [True, False, True]
    assert answer["is_at_most_weight_2"]["values"] == [True, True, False]
