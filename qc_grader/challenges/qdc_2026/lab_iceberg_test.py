"""Tests for the ``lab_iceberg`` grading functions (client side).

    python -m pytest grader/client/qc_grader/challenges/qdc_2026/lab_iceberg_test.py

Every function packs the documented keys, the packed answer is JSON-serialisable and small, bad
input raises ``ValueError`` with a fix hint, and a callable is evaluated client-side rather than
sent. ``grade_answer`` is patched, so nothing leaves the machine; the "participant" is the
prototype grader's reference implementations.

**This file runs in two places.** In a ``Quantum-Challenge-Grader`` checkout only the client is
present, so the tests that need a participant implementation (the prototype grader) or the
server validators are skipped; the rest - packing, the wire format, the input contract - run
everywhere. Nothing is imported at module scope that the client package does not ship, because
``pyproject.toml`` sets ``testpaths = ["qc_grader"]`` and a module-level ImportError here fails
collection for the whole repository, not just this lab.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from typeguard import TypeCheckError

from . import lab_iceberg as C

_TARGET = "qc_grader.challenges.qdc_2026.lab_iceberg.grade_answer"

# The challenge folder, when this test runs inside the challenge repo. Six levels up from
# .../grader/client/qc_grader/challenges/qdc_2026/lab_iceberg_test.py.
_CHALLENGE = Path(__file__).resolve().parents[5]


def _optional(name: str, path: Path):
    """Import a module that only exists in the challenge repo, or return None."""
    if not path.exists():
        return None
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    try:
        return __import__(name)
    except ImportError:  # pragma: no cover - a broken checkout, not a packaging problem
        return None


#: The prototype grader, which supplies the reference "participant" implementations.
P = _optional("ising_iceberg_GRADER", _CHALLENGE / "ising_iceberg_GRADER.py")

#: Skip marker for the tests that need it.
needs_prototype = pytest.mark.skipif(
    P is None,
    reason="needs the challenge repo's ising_iceberg_GRADER.py (absent in a qc-grader checkout)",
)


def _packed(fn, *args, **kwargs) -> dict:
    """Call a grading function with ``grade_answer`` patched and return the packed answer."""
    with patch(_TARGET) as mock:
        fn(*args, **kwargs)
    assert mock.called, "the grading function never called grade_answer"
    answer, kw = mock.call_args[0][0], mock.call_args[1]
    assert kw["challenge"] == "qdc_2026"
    assert kw["lab"] == "lab_iceberg"
    return answer


def _encode(answer: dict) -> str:
    """Serialise with the platform's own encoder when it is installed.

    ``grade_answer`` calls ``qc_grader.custom_encoder.to_json``, not ``json.dumps``, so that is
    what the payload has to survive - it is the encoder that decides whether a numpy scalar or a
    ``SparsePauliOp`` reaches the server at all. Falls back to ``json.dumps`` in the challenge
    repo, where the client package is not installed; measured identical byte counts on every
    exercise, since the grading functions already cast to plain Python.
    """
    try:
        from qc_grader.custom_encoder import to_json
    except ImportError:
        return json.dumps(answer)
    return to_json(answer)


def _assert_wire_ok(answer: dict, max_bytes: int = 1_000_000) -> int:
    """The answer must survive the JSON boundary and stay well under the payload cap."""
    wire = _encode(answer)
    assert len(wire) < max_bytes, f"payload is {len(wire)} bytes"
    assert json.loads(wire) == json.loads(json.dumps(json.loads(wire)))
    return len(wire)


# ids and exports
def test_challenge_and_lab_ids():
    assert C._CHALLENGE == "qdc_2026"
    assert C._LAB == "lab_iceberg"


def test_every_exercise_has_a_grade_function():
    """Every server exercise has a client function. Needs the server half of the bundle."""
    server = _CHALLENGE / "grader" / "server"
    if not (server / "validations" / "qdc_2026" / "lab_iceberg.py").exists():
        pytest.skip(
            "needs the bundle's server validators (absent in a qc-grader checkout)"
        )
    if str(server) not in sys.path:
        sys.path.insert(0, str(server))
    from validations.qdc_2026 import lab_iceberg as S

    for exercise in S.POINTS:
        assert hasattr(C, f"grade_lab_iceberg_{exercise}"), exercise


def test_every_grade_function_is_exported():
    """The ids the client offers and the names ``__init__`` re-exports must agree.

    Runs everywhere, so a lab added without touching ``__all__`` is caught in either repo.
    """
    from . import __all__ as exported

    offered = {n for n in dir(C) if n.startswith("grade_lab_iceberg_")}
    assert offered, "no grading functions found"
    assert offered <= set(exported), sorted(offered - set(exported))


# the vendored lattice code
_VENDORED = ("iceberg_device.py", "iceberg_block.py", "iceberg_layout.py")


@pytest.mark.parametrize("name", _VENDORED)
def test_vendored_copy_matches_the_challenge(name):
    """``_iceberg/`` must stay byte-identical to the challenge's ``utils/``.

    These modules are participant-facing: a participant's function is handed these classes and
    may call any of their methods, so a divergence here grades correct work as wrong. Skipped
    in a ``qc-grader`` checkout, where the original is not present to compare against.
    """
    original = _CHALLENGE / "utils" / name
    if not original.exists():
        pytest.skip(
            "needs the challenge repo's utils/ (absent in a qc-grader checkout)"
        )
    vendored = Path(__file__).resolve().parent / "_iceberg" / name
    assert vendored.exists(), f"{name} is missing from _iceberg/"
    assert vendored.read_bytes() == original.read_bytes(), (
        f"_iceberg/{name} has drifted from utils/{name}. Re-copy it: the grading probes hand "
        "these classes to participant code, so the two must not diverge."
    )


def test_function_valued_params_are_not_annotated_callable():
    """Annotating these ``Callable`` would let typeguard pre-empt our better message.

    typeguard runs before the function body, so ``Callable`` turns the lab's most common
    mistake - passing ``fn(...)`` where ``fn`` belongs - into `argument "full_circuit" (int) is
    not callable` instead of the fix-first wording EXERCISES.md section 3 documents. Each of
    these parameters must stay unannotated *and* be guarded by ``_require_callable``.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(C))
    offenders, unguarded = [], []
    for fn in tree.body:
        if not (
            isinstance(fn, ast.FunctionDef) and fn.name.startswith("grade_lab_iceberg_")
        ):
            continue
        body = ast.unparse(fn)
        for arg in fn.args.args:
            annotation = ast.unparse(arg.annotation) if arg.annotation else None
            guarded = f'"{arg.arg}"' in body and "_require_callable" in body
            if annotation == "Callable":
                offenders.append(f"{fn.name}({arg.arg})")
            elif guarded and annotation not in (None, "Any"):
                unguarded.append(f"{fn.name}({arg.arg}): {annotation}")
    assert not offenders, (
        "these parameters are annotated Callable, which pre-empts _require_callable's "
        f"message: {offenders}"
    )
    assert not unguarded, unguarded


def test_a_callable_mistake_names_the_fix():
    """The ``fn`` vs ``fn(...)`` message must survive, for every function-valued exercise."""
    for fn in (
        C.grade_lab_iceberg_ex1_5b,
        C.grade_lab_iceberg_ex1_6,
        C.grade_lab_iceberg_ex1_7,
        C.grade_lab_iceberg_ex1_9,
        C.grade_lab_iceberg_ex2_1,
        C.grade_lab_iceberg_ex2_7,
    ):
        with pytest.raises(ValueError, match="itself, not a call to it"):
            fn(42)


def test_numeric_params_accept_numpy_scalars():
    """A participant reading a median off a numpy array must not be rejected at the boundary.

    ``np.float32``, ``np.int64`` and 0-d arrays are not ``float`` subclasses, so annotating
    these ``float`` would fail correct work; ``SupportsFloat`` admits them.
    """
    np = pytest.importorskip("numpy")
    sites = {(0, 0): 0.5}
    for value in (0.3, 2, np.float64(0.3), np.float32(0.3), np.int64(2), np.array(0.3)):
        answer = _packed(C.grade_lab_iceberg_ex3_5, sites, sites, value, value)
        assert isinstance(answer["median_melting"], float)


def test_numeric_params_still_reject_a_non_number():
    """Either typeguard or ``_num`` must stop it; which one is not the contract here."""
    for bad in ("0.3", [0.3], None):
        with pytest.raises((TypeCheckError, ValueError)):
            _packed(C.grade_lab_iceberg_ex3_5, {(0, 0): 0.5}, {(0, 0): 0.5}, bad, 0.1)


def test_zbar_maps_accept_numpy_keys():
    """``{(np.int64, np.int64): np.float64}`` is what iterating a numpy array produces."""
    np = pytest.importorskip("numpy")
    sites = {(np.int64(0), np.int64(0)): np.float64(0.5)}
    answer = _packed(C.grade_lab_iceberg_ex3_5, sites, sites, 0.2, 0.1)
    assert set(answer["enc_melting"]) == {"[0, 0]"}


def test_probe_helpers_survive_a_mutating_participant():
    """A participant function may mutate what it is handed; the probe must not degrade.

    The helpers are ``lru_cache``d, so returning the cached object let one exercise corrupt the
    probe for every later exercise in the same kernel - a wrong answer rather than an error.
    """
    from . import lab_iceberg_probes as PR

    data, syn = PR.probe_postselected(2)
    shots, rounds = len(data), len(syn[0])
    data.append("00000000")
    syn[0].append("0000")
    again_data, again_syn = PR.probe_postselected(2)
    assert len(again_data) == shots, "probe_postselected leaked its cached list"
    assert len(again_syn[0]) == rounds, "probe_postselected leaked its cached syndromes"

    obs = PR.probe_observables(2)
    n_obs = len(obs)
    obs.pop(next(iter(obs)))
    assert len(PR.probe_observables(2)) == n_obs, (
        "probe_observables leaked its cached dict"
    )

    corr = PR.probe_correlations(2)
    key = next(iter(corr))
    before = float(corr[key][0])
    corr[key][0] = 999.0
    corr.pop(key)
    fresh = PR.probe_correlations(2)
    assert len(fresh) == n_obs, "probe_correlations leaked its cached dict"
    assert float(fresh[key][0]) == before, "probe_correlations leaked its cached arrays"


def test_vendored_package_is_self_contained():
    """The vendored modules must not reach back into the challenge's ``utils``.

    This is the regression guard for the packaging bug: an ``import utils`` anywhere in the
    client raises ModuleNotFoundError for a participant who pip-installed ``qc-grader``.
    """
    client = Path(__file__).resolve().parent
    for path in sorted(client.rglob("*.py")):
        if path.name == Path(__file__).name:
            continue
        source = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(source.splitlines(), 1):
            code = line.split("#", 1)[0]
            assert "from utils" not in code and "import utils" not in code, (
                f"{path.relative_to(client)}:{lineno} imports the challenge's utils package, "
                "which does not exist in an installed qc-grader. Use ._iceberg instead."
            )


# callables are evaluated
@needs_prototype
def test_structural_probes_are_evaluated_not_sent():
    """A callable must never reach the wire: only its probe output."""
    answer = _packed(C.grade_lab_iceberg_ex1_6, P.GRADER_full_circuit)
    _assert_wire_ok(answer)
    assert set(answer) == {"probes", "calls"}
    assert len(answer["probes"]) == len(C.CIRC_ELEMENTS_CASES)
    for probe in answer["probes"]:
        for op in probe:
            assert isinstance(op[0], str)
            assert all(isinstance(i, int) for i in op[1])


def test_signature_drops_barriers():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.barrier()
    qc.cx(0, 1)
    assert C._signature(qc) == [["h", [0], []], ["cx", [0, 1], []]]


def test_signature_carries_params_only_when_asked():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.rz(0.5, 0)
    assert C._signature(qc) == [["rz", [0], []]]
    assert C._signature(qc, with_params=True) == [["rz", [0], [], [0.5]]]


def test_signature_rejects_a_function_that_returned_none():
    with pytest.raises(ValueError, match="returns the circuit it built on"):
        C._signature(None)


def test_unbound_parameter_is_reported():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter

    qc = QuantumCircuit(1)
    qc.rz(Parameter("theta"), 0)
    with pytest.raises(ValueError, match="unbound parameter"):
        C._signature(qc, with_params=True)


# per-exercise packing
@needs_prototype
def test_ex1_2_packs_the_lattice():
    lattice, block_qubits, placement, _ = P._toy()
    answer = _packed(
        C.grade_lab_iceberg_ex1_2, lattice, block_qubits, P.TOY_BUBBLE, placement
    )
    _assert_wire_ok(answer)
    assert set(answer) == {"sites", "edges", "block_qubits", "bubble"}
    assert len(answer["sites"]) == 4
    assert all(isinstance(k, str) for k in answer["block_qubits"]), (
        "JSON keys must be strings"
    )


@needs_prototype
def test_ex1_3_packs_five_sub_functions():
    answer = _packed(
        C.grade_lab_iceberg_ex1_3,
        P.GRADER_init_circuit,
        P.GRADER_prep_logical_zero,
        P.GRADER_prep_logical_zero_blocks,
        P.GRADER_logical_x,
        P.GRADER_create_bubble,
    )
    _assert_wire_ok(answer)
    assert set(answer) == {
        "init_regs",
        "init_frames",
        "init_nq",
        "ghz",
        "blocks",
        "logical_x",
        "bubble",
    }
    assert len(answer["logical_x"]) == len(C.LOGICAL_X_CASES)
    assert len(answer["ghz"][0]) == 4, "the GHZ probe must carry gate parameters"


def test_ex1_4_reads_the_schedule():
    class Gsched:
        depth, n_cx, status = 12, 22, "OPTIMAL"

    answer = _packed(C.grade_lab_iceberg_ex1_4, Gsched())
    assert answer == {"depth": 12, "n_cx": 22, "status": "OPTIMAL"}


def test_ex1_4_rejects_a_non_schedule():
    with pytest.raises(ValueError, match="ScheduleOptimizer.optimize"):
        _packed(C.grade_lab_iceberg_ex1_4, object())


@needs_prototype
def test_ex1_5a_packs_four_probe_lists():
    answer = _packed(
        C.grade_lab_iceberg_ex1_5a,
        P.GRADER_compute_to_syndrome,
        P.GRADER_syndrome_to_compute,
        P.GRADER_measure_syndromes,
        P.GRADER_syndrome_extraction,
    )
    _assert_wire_ok(answer)
    assert len(answer["compute_to_syndrome"]) == len(C.SWAP_CASES)
    assert len(answer["syndrome_extraction"]) == len(C.SYNDROME_EXTRACTION_CASES)


@needs_prototype
def test_ex1_7_packs_sparse_pauli_lists():
    answer = _packed(C.grade_lab_iceberg_ex1_7, P.GRADER_build_observables)
    _assert_wire_ok(answer)
    assert set(answer) == {"encoded", "unencoded"}
    term = next(iter(answer["encoded"].values()))[0]
    assert isinstance(term[0], str) and isinstance(term[1], float)


def test_ex1_8_accepts_dicts_or_scalars():
    from_scalars = _packed(C.grade_lab_iceberg_ex1_8, [1.0, 0.6, 0.4, 0.3, 0.2, 0.15])
    assert from_scalars["mean_abs"][0] == 1.0
    from_dicts = _packed(
        C.grade_lab_iceberg_ex1_8, [{("a", 0): 1.0, ("b", 0): 1.0}] * 6
    )
    assert from_dicts["mean_abs"] == [1.0] * 6


@needs_prototype
def test_ex1_9_carries_parameters():
    answer = _packed(C.grade_lab_iceberg_ex1_9, P.GRADER_unencoded_trotter_circuit)
    _assert_wire_ok(answer)
    assert answer["num_qubits"] == 4
    rotations = [op for op in answer["no_measure"] if op[0] in ("rx", "rz", "rzz")]
    assert rotations and all(len(op) == 4 and op[3] for op in rotations)


@needs_prototype
def test_ex2_1_evaluates_postselect_parity():
    answer = _packed(C.grade_lab_iceberg_ex2_1, P.GRADER_postselect_parity)
    _assert_wire_ok(answer)
    assert set(answer) == {"kept", "kept_syn"}
    assert 0 < len(answer["kept"][0]) < C.ORP_PROBE_SHOTS, (
        "some shots must be discarded"
    )


@needs_prototype
def test_ex2_2_uses_postselected_syndromes():
    """The notebook calls detector_violations on the output of 2.1, so the probe must match."""
    answer = _packed(C.grade_lab_iceberg_ex2_2, P.GRADER_detector_violations)
    _assert_wire_ok(answer)
    kept = _packed(C.grade_lab_iceberg_ex2_1, P.GRADER_postselect_parity)["kept"][0]
    for mask in answer["masks"].values():
        assert len(mask) == len(kept)


@needs_prototype
def test_ex2_3_packs_absolute_correlations():
    answer = _packed(C.grade_lab_iceberg_ex2_3, P.GRADER_compute_correlations)
    _assert_wire_ok(answer)
    for series in answer["delta"].values():
        assert all(v >= 0 for v in series)


@needs_prototype
def test_ex2_4_is_seeded_and_reproducible():
    first = _packed(C.grade_lab_iceberg_ex2_4, P.GRADER_bootstrap_obs_uncertainty)
    second = _packed(C.grade_lab_iceberg_ex2_4, P.GRADER_bootstrap_obs_uncertainty)
    assert first == second
    assert first["sig2_small"] > first["sig2_seeded"]


@needs_prototype
def test_ex2_5_nan_becomes_null():
    answer = _packed(C.grade_lab_iceberg_ex2_5, P.GRADER_compute_obs_k)
    _assert_wire_ok(answer)
    wire = json.loads(json.dumps(answer))
    assert wire == answer, "NaN must be encoded as null, not as the literal NaN"


@needs_prototype
def test_ex2_7_packs_the_whole_pipeline():
    answer = _packed(C.grade_lab_iceberg_ex2_7, P.GRADER_run_orp)
    _assert_wire_ok(answer)
    assert set(answer) == {"f_k", "O_k", "sig2_k", "O_ref", "k_star", "O_k_star"}
    assert set(answer["O_k"]) == set(answer["k_star"])


def test_ex3_5_keys_are_json_strings():
    values = {(0, 0): 0.5, (1, 1): -0.3}
    answer = _packed(C.grade_lab_iceberg_ex3_5, values, values, 0.2, 0.1)
    _assert_wire_ok(answer)
    assert set(answer["enc_melting"]) == {"[0, 0]", "[1, 1]"}


def test_ex3_5_rejects_an_empty_map():
    with pytest.raises(ValueError, match="empty"):
        _packed(C.grade_lab_iceberg_ex3_5, {}, {}, 0.2, 0.1)


def test_ex3_5_rejects_a_non_finite_median():
    with pytest.raises(ValueError, match="NaN or infinite"):
        _packed(
            C.grade_lab_iceberg_ex3_5, {(0, 0): 0.5}, {(0, 0): 0.5}, float("nan"), 0.1
        )


def test_ex5_1_accepts_an_options_object():
    """The sampler options object is not JSON-serialisable, so it must be reduced to text."""

    class Options:
        def __init__(self):
            self.dynamical_decoupling = True

    answer = _packed(
        C.grade_lab_iceberg_ex5_1, Options(), {(0, 0): 0.2}, {(0, 0): 0.3}, 0.25
    )
    _assert_wire_ok(answer)
    assert isinstance(answer["applied"], str)


def test_ex5_2_casts_everything():
    answer = _packed(
        C.grade_lab_iceberg_ex5_2, "ibm_phoenix", 174, 50, 900, 600, {(0, 0): 0.25}
    )
    _assert_wire_ok(answer)
    assert isinstance(answer["depth_hh"], int)
    assert isinstance(answer["backend"], str)


# input contract
@pytest.mark.parametrize(
    "name,fn",
    [
        ("full_circuit", C.grade_lab_iceberg_ex1_6),
        ("build_observables", C.grade_lab_iceberg_ex1_7),
        ("final_measurements", C.grade_lab_iceberg_ex1_5b),
        ("unencoded_trotter_circuit", C.grade_lab_iceberg_ex1_9),
        ("postselect_parity", C.grade_lab_iceberg_ex2_1),
        ("run_orp", C.grade_lab_iceberg_ex2_7),
    ],
)
def test_passing_a_value_instead_of_a_function_is_reported(name, fn):
    with pytest.raises(ValueError, match="not a call to it"):
        _packed(fn, 42)


@needs_prototype
def test_num_logical_blocks_is_passed_explicitly_when_accepted():
    """P3-19: the wire contract is explicit, and a function that takes it gets it."""
    seen = {}

    def postselect(data_list, syn_list, num_logical_blocks):
        seen["explicit"] = num_logical_blocks
        return P.GRADER_postselect_parity(data_list, syn_list, num_logical_blocks)

    _packed(C.grade_lab_iceberg_ex2_1, postselect)
    assert seen["explicit"] == 2


@needs_prototype
def test_a_function_reading_the_global_still_works():
    """The notebook's own signature omits it and reads a global; that must keep working."""
    captured = {}

    def postselect(data_list, syn_list):
        captured["from_global"] = num_logical_blocks  # noqa: F821 - injected by the client
        return P.GRADER_postselect_parity(data_list, syn_list, num_logical_blocks)  # noqa: F821

    _packed(C.grade_lab_iceberg_ex2_1, postselect)
    assert captured["from_global"] == 2
    assert "num_logical_blocks" not in postselect.__globals__, (
        "the global must be restored"
    )
