"""Client tests for lab_floquet: packing, probes and early errors, with deliberately wrong dummies."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as np
import pytest
from qc_grader.custom_encoder import to_json
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

from qc_grader.challenges.qdc_2026 import _floquet_probes as probes
from qc_grader.challenges.qdc_2026 import lab_floquet

_PATCH = "qc_grader.challenges.qdc_2026.lab_floquet.grade_answer"
_MAX_BYTES = 1_000_000


def _submit(fn: Any, *args: Any, **kwargs: Any) -> tuple[Any, str]:
    """Run a grade function with grade_answer patched; return the answer and its exercise id."""
    with patch(_PATCH) as grade:
        fn(*args, **kwargs)
    assert grade.call_count == 1
    answer = grade.call_args.args[0]
    assert grade.call_args.kwargs == {
        "lab": "lab_floquet",
        "exercise": grade.call_args.kwargs["exercise"],
        "challenge": "qdc_2026",
    }
    assert len(to_json(answer)) < _MAX_BYTES
    return answer, grade.call_args.kwargs["exercise"]


def _no_gates(qc: QuantumCircuit, groups: Any, params: Any) -> None:
    return None


def _rx_only(qc: QuantumCircuit, groups: Any, params: Any) -> None:
    for q in range(qc.num_qubits):
        qc.rx(0.1, q)


def _zeros(*args: Any, **kwargs: Any) -> np.ndarray:
    return np.zeros(len(probes.ZNE_CYCLES))


def _boom(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("dummy failure")


# --------------------------------------------------------------------------- #
# Part 1
# --------------------------------------------------------------------------- #


def test_ex1_1_packs_plain_ints() -> None:
    lattice = probes.probe_lattice()
    answer, exercise = _submit(lab_floquet.grade_lab_floquet_ex1_1, lattice, [[(0, 1)]])
    assert exercise == "ex1_1"
    assert answer["n_qubits"] == probes.PROBE_N_QUBITS
    assert answer["edges"] == [list(e) for e in probes.PROBE_EDGES]
    assert answer["groups"] == [[[0, 1]]]
    assert all(type(q) is int for q in answer["groups"][0][0])
    assert answer["lattice_groups"] == [
        [list(e) for e in g] for g in probes.PROBE_GROUPS
    ]


def test_ex1_1_rejects_non_lattice() -> None:
    with pytest.raises(ValueError, match="paper_colored_lattice"):
        lab_floquet.grade_lab_floquet_ex1_1(object(), [])


def test_ex1_2_sends_two_probe_circuits() -> None:
    answer, exercise = _submit(lab_floquet.grade_lab_floquet_ex1_2, _rx_only)
    assert exercise == "ex1_2"
    assert len(answer["circuits"]) == 2
    assert all(qc.num_qubits == probes.PROBE_N_QUBITS for qc in answer["circuits"])


def test_ex1_2_in_place_convention_sends_empty_circuit() -> None:
    answer, _ = _submit(lab_floquet.grade_lab_floquet_ex1_2, _no_gates)
    assert all(len(qc.data) == 0 for qc in answer["circuits"])


def test_ex1_2_reports_participant_error() -> None:
    with pytest.raises(ValueError, match="floquet_cycle raised RuntimeError"):
        lab_floquet.grade_lab_floquet_ex1_2(_boom)


# --------------------------------------------------------------------------- #
# Part 2
# --------------------------------------------------------------------------- #


def test_ex2_1_records_each_part_independently() -> None:
    def baseline(counts: Any, lattice: Any) -> tuple[list[float], list[float]]:
        return [np.float64(0.5)] * 3, [0.25] * 3

    answer, exercise = _submit(lab_floquet.grade_lab_floquet_ex2_1, _boom, baseline)
    assert exercise == "ex2_1"
    assert answer["logical_circuit"] == {
        "error": "RuntimeError: dummy failure",
        "unmeasured": [],
        "measured": [],
    }
    assert answer["baseline_magnetizations"] == {
        "error": None,
        "M": [0.5] * 3,
        "Mz2": [0.25] * 3,
    }
    assert all(type(x) is float for x in answer["baseline_magnetizations"]["M"])


def test_ex2_1_sends_both_circuit_variants() -> None:
    def logical(
        depth: int, lattice: Any, groups: Any, *, measured: bool = True
    ) -> QuantumCircuit:
        qc = QuantumCircuit(lattice.n_qubits)
        if measured:
            qc.measure_all()
        return qc

    answer, _ = _submit(lab_floquet.grade_lab_floquet_ex2_1, logical, _boom)
    record = answer["logical_circuit"]
    assert record["error"] is None
    assert (
        len(record["unmeasured"])
        == len(record["measured"])
        == len(probes.LOGICAL_DEPTHS)
    )
    assert all(qc.num_clbits == 0 for qc in record["unmeasured"])
    assert all(qc.num_clbits == probes.PROBE_N_QUBITS for qc in record["measured"])
    assert answer["baseline_magnetizations"]["error"] == "RuntimeError: dummy failure"


def test_ex2_2_records_fake_mthree_calls() -> None:
    def mitigator(
        isa_list: Any,
        *,
        use_hardware: bool,
        backend: Any,
        calibration_tracker: Any,
        mthree_module: Any,
    ) -> Any:
        if mthree_module is None:
            return "not none"  # wrong on purpose
        m = mthree_module.M3Mitigation(backend)
        with calibration_tracker(m, [0, 1]) as settings:
            m.cals_from_system(qubits=[0, 1], **settings)
        return m

    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex2_2, mitigator, _boom, _boom, _boom
    )
    assert exercise == "ex2_2"
    records = {p["name"]: p for p in answer["make_readout_mitigator"]["probes"]}
    assert list(records) == list(probes.READOUT_PROBES)
    assert records["A"]["returned"] == "mitigator"
    assert records["A"]["constructor_got_backend"] == [True]
    assert records["A"]["tracker_qubits"] == [[0, 1]]
    assert records["A"]["cals_calls"] == [
        {"qubits": [0, 1], "settings": dict(probes.READOUT_SETTINGS)}
    ]
    assert records["B"]["error"] == f"RuntimeError: {probes.READOUT_CAL_ERROR}"
    assert records["C_false"]["returned"] == "other"
    assert answer["corrected_mags"]["error"] == "RuntimeError: dummy failure"
    assert answer["folded_isa"] == {
        "error": "RuntimeError: dummy failure",
        "circuits": [],
    }
    assert answer["zne_extrapolate"] == {
        "error": "RuntimeError: dummy failure",
        "intercepts": [],
    }


def test_ex2_2_records_correction_qubits_and_folds() -> None:
    def corrected(
        counts: Any, isa_list: Any, lattice: Any, mitigator: Any = None
    ) -> tuple[Any, Any]:
        if mitigator is not None:
            for counts_dict in counts:
                mitigator.apply_correction(counts_dict, [0])
        return np.ones(3), np.ones(3)

    def folded(depth: int, scale: int, lattice: Any, groups: Any) -> QuantumCircuit:
        qc = QuantumCircuit(lattice.n_qubits)
        qc.measure_all()
        return qc

    def extrapolate(per_scale: Any, scales: Any = (1, 3)) -> list[float]:
        return list(per_scale[1])  # the scale-1 values, wrong on purpose

    answer, _ = _submit(
        lab_floquet.grade_lab_floquet_ex2_2, _boom, corrected, folded, extrapolate
    )
    assert answer["corrected_mags"]["apply_correction_qubits"] == [[0], [0]]
    assert answer["corrected_mags"]["mitigated"] == {"M": [1.0] * 3, "Mz2": [1.0] * 3}
    assert len(answer["folded_isa"]["circuits"]) == len(probes.FOLD_DEPTHS) * len(
        probes.FOLD_SCALES
    )
    expected = list(np.add(probes.ZNE_INTERCEPT, probes.ZNE_SLOPE))
    assert answer["zne_extrapolate"]["intercepts"] == [expected] * len(
        probes.ZNE_SCALE_CALLS
    )


# --------------------------------------------------------------------------- #
# Part 3
# --------------------------------------------------------------------------- #


def test_ex3_1_sends_the_returned_circuits() -> None:
    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex3_1, lambda qc: qc.copy()
    )
    assert exercise == "ex3_1"
    assert [qc.num_qubits for qc in answer["circuits"]] == [
        n for n, _ in probes.NORMALIZE_PROBES
    ]


def test_ex3_1_rejects_non_circuit() -> None:
    with pytest.raises(ValueError, match="must be a QuantumCircuit"):
        lab_floquet.grade_lab_floquet_ex3_1(lambda qc: None)


def test_ex3_2a_packs_layout() -> None:
    def layout(backend: Any, lattice: Any, groups: Any, limit: int) -> np.ndarray:
        assert (
            backend.num_qubits == probes.PROBE_N_QUBITS and limit == probes.LAYOUT_LIMIT
        )
        return np.arange(lattice.n_qubits)[::-1]

    answer, exercise = _submit(lab_floquet.grade_lab_floquet_ex3_2a, layout)
    assert exercise == "ex3_2a"
    assert answer == {"layout": [6, 5, 4, 3, 2, 1, 0]}
    assert all(type(q) is int for q in answer["layout"])


def test_ex3_2a_rejects_fractional_qubits() -> None:
    with pytest.raises(ValueError, match="list of physical qubits"):
        lab_floquet.grade_lab_floquet_ex3_2a(lambda *a, **k: [0.5] * 7)


def test_ex3_2b_packs_layout_and_error() -> None:
    answer, _ = _submit(
        lab_floquet.grade_lab_floquet_ex3_2b,
        lambda qc, backend: ([0, 1, 2], np.float64(0.5)),
    )
    assert answer == {"layout": [0, 1, 2], "error": 0.5}


def test_ex3_2b_rejects_wrong_return() -> None:
    with pytest.raises(ValueError, match="layout, estimated_error"):
        lab_floquet.grade_lab_floquet_ex3_2b(lambda qc, backend: [0, 1, 2])


def test_ex3_3a_reads_options_without_running() -> None:
    options = SimpleNamespace(
        max_execution_time=999,
        default_shots=1,
        resilience_level=2,
        resilience=SimpleNamespace(
            measure_mitigation=False, zne_mitigation=True, measure_noise_learning=None
        ),
        twirling=SimpleNamespace(
            enable_measure=False,
            enable_gates=True,
            num_randomizations=float("inf"),
            strategy="active",
            shots_per_randomization=7,
        ),
        dynamical_decoupling=SimpleNamespace(enable=True),
    )
    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex3_3a,
        lambda backend, allowance: SimpleNamespace(options=options),
        shots=4,
        randomizations=2,
        cal_randomizations=3,
    )
    assert exercise == "ex3_3a"
    assert answer["estimator_class"] == "SimpleNamespace"
    assert answer["declared"] == {
        "shots": 4,
        "randomizations": 2,
        "cal_randomizations": 3,
    }
    assert answer["options"]["max_execution_time"] == 999
    assert answer["options"]["measure_noise_learning_randomizations"] is None
    assert answer["options"]["twirling_randomizations"] == "inf"
    assert set(answer["options"]) == set(lab_floquet._OPTION_PATHS)


def test_ex3_3b_sends_operators() -> None:
    wrong = SparsePauliOp.from_sparse_list(
        [("Z", [0], 1.0)], num_qubits=probes.PROBE_N_QUBITS
    )
    answer, _ = _submit(
        lab_floquet.grade_lab_floquet_ex3_3b, lambda lattice: [wrong, wrong]
    )
    assert answer == {"M": wrong, "Mz2": wrong}


def test_ex3_3b_rejects_non_operator() -> None:
    with pytest.raises(ValueError, match="two SparsePauliOp"):
        lab_floquet.grade_lab_floquet_ex3_3b(lambda lattice: ["Z", "Z"])


# --------------------------------------------------------------------------- #
# Part 4
# --------------------------------------------------------------------------- #


def test_ex4_1_sends_six_circuits() -> None:
    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex4_1,
        lambda depth, lattice, groups, factor: QuantumCircuit(7),
    )
    assert exercise == "ex4_1"
    assert len(answer["circuits"]) == len(probes.FOLD_DEPTHS) * len(probes.FOLD_SCALES)


def test_ex4_1_rejects_oversized_circuit() -> None:
    def huge(depth: int, lattice: Any, groups: Any, factor: int) -> QuantumCircuit:
        qc = QuantumCircuit(7)
        for _ in range(lab_floquet._MAX_INSTRUCTIONS + 1):
            qc.x(0)
        return qc

    with pytest.raises(ValueError, match="at most 20,000"):
        lab_floquet.grade_lab_floquet_ex4_1(huge)


def test_ex4_2_records_every_probe_without_submitting() -> None:
    answer, exercise = _submit(lab_floquet.grade_lab_floquet_ex4_2, _boom)
    assert exercise == "ex4_2"
    assert [p["name"] for p in answer["probes"]] == list(probes.MEASURE_PROBES)
    for record in answer["probes"]:
        assert record["error"] == "RuntimeError: dummy failure"
        assert (
            record["run_program_calls"] == 0
            and record["charged"] == []
            and record["run"] is None
        )


def test_ex4_2_records_fake_calls_and_reduces_run() -> None:
    def measure(
        lattice: Any,
        groups: Any,
        backend: Any,
        layout: Any,
        *,
        cycles: Any,
        factors: Any,
        use_hardware: bool,
        service: Any,
        build_estimator: Any,
        run_program: Any,
        charge_qpu_time: Any,
    ) -> dict[str, Any]:
        estimator = build_estimator(backend)
        pub = (
            QuantumCircuit(lattice.n_qubits),
            [SparsePauliOp("I" * lattice.n_qubits)] * 2,
        )
        job = run_program("k", submit=lambda: estimator.run([pub]))
        job.result()
        charge_qpu_time("k", job_id=job.job_id(), qpu_seconds=1.5)
        return {
            "cycles": [1],
            "factors": [1],
            "pub_order": [(1, 1)],
            "values": {"M": [[0.0]], "Mz2": [[0.0]]},
            "stds": {"M": [[0.0]], "Mz2": [[0.0]]},
            "job_id": job.job_id(),
            "qpu_seconds": 1.5,
            "provenance": "user",
        }

    answer, _ = _submit(lab_floquet.grade_lab_floquet_ex4_2, measure)
    main = answer["probes"][0]
    assert main["error"] is None
    assert (
        main["estimator_got_backend"] == [True]
        and main["run_program_calls"] == 1
        and main["charged"] == [1.5]
    )
    assert len(main["circuits"]) == 1 and len(main["observables"][0]) == 2
    assert main["run"]["M"] == [[0.0]] and main["run"]["pub_order"] == [[1, 1]]
    assert main["run"]["job_id"] == probes.MEASURE_JOB_ID
    assert all(p["circuits"] == [] for p in answer["probes"][1:])


def test_ex4_2_flags_a_bad_return_shape() -> None:
    answer, _ = _submit(
        lab_floquet.grade_lab_floquet_ex4_2, lambda *a, **k: {"cycles": [1]}
    )
    assert answer["probes"][0]["error"].startswith("BadReturn: missing key")


def test_ex4_3a_records_values_and_errors() -> None:
    answer, exercise = _submit(lab_floquet.grade_lab_floquet_ex4_3a, _zeros)
    assert exercise == "ex4_3a"
    assert [p["name"] for p in answer["probes"]] == list(probes.QMIT_PROBES)
    assert all(p["value"] == [0.0] * 3 and p["error"] is None for p in answer["probes"])
    answer, _ = _submit(lab_floquet.grade_lab_floquet_ex4_3a, _boom)
    assert all(
        p["value"] is None and p["error"] == "RuntimeError: dummy failure"
        for p in answer["probes"]
    )


@pytest.mark.parametrize(
    ("fn", "exercise"),
    [
        (lab_floquet.grade_lab_floquet_ex4_3b, "ex4_3b"),
        (lab_floquet.grade_lab_floquet_ex4_3c, "ex4_3c"),
        (lab_floquet.grade_lab_floquet_ex4_3d, "ex4_3d"),
    ],
)
def test_ex4_3_extrapolators_send_three_probes(fn: Any, exercise: str) -> None:
    answer, sent = _submit(fn, _zeros)
    assert sent == exercise
    assert [p["name"] for p in answer["probes"]] == ["M", "Mz2", "missing_factor"]


def test_ex4_3e_packs_choice() -> None:
    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex4_3e,
        lambda run, ref: ((np.int64(1), 5), "linear"),
    )
    assert exercise == "ex4_3e"
    assert answer == {"factors": [1, 5], "method": "linear"}


def test_ex4_3e_rejects_wrong_return() -> None:
    with pytest.raises(ValueError, match="factors, method_name"):
        lab_floquet.grade_lab_floquet_ex4_3e(lambda run, ref: "linear")


# --------------------------------------------------------------------------- #
# Part 5
# --------------------------------------------------------------------------- #


def test_ex5_1_records_guarded_callbacks() -> None:
    def extend(
        lattice: Any,
        run21: Any,
        *,
        cycles: Any,
        selected_factors: Any,
        use_hardware: bool,
        backend: Any,
        backend_name: str,
        ledger_path: Any,
        saved_run_settings: Any,
        mapomatic_layout: Any,
        measure_cycle_folded: Any,
        qpu_time_spent: Any,
    ) -> dict[str, Any]:
        saved_run_settings(
            "trex-28q", backend_name=backend_name, ledger_path=ledger_path
        )
        return {
            "lattices_by_size": {21: lattice},
            "groups_by_size": {21: lattice.color_groups()},
            "runs_by_size": {},
            "layout_by_size": {},
            "qpu_seconds": 0,
        }

    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex5_1, extend, probes.probe_lattice()
    )
    assert exercise == "ex5_1"
    runs = {r["probe"]: r for r in answer["runs"]}
    assert list(runs) == [p[0] for p in probes.EXTENSION_PROBES]
    assert runs["patches_local"]["error"].startswith("AssertionError: local track")
    hardware = runs["layouts_hardware"]
    assert hardware["error"] is None
    assert hardware["calls"] == [
        {
            "callback": "saved_run_settings",
            "n_qubits": None,
            "args": {
                "key": "trex-28q",
                "backend_name": probes.EXTENSION_BACKEND_NAME,
                "ledger_path": probes.EXTENSION_LEDGER,
            },
        }
    ]
    assert (
        hardware["lattices"][0]["n_qubits"] == 21
    )  # keyed by size, not lattice.n_qubits
    assert hardware["flags"]["lattice21_kept"] is True
    assert (
        hardware["flags"]["sizes_match"] is False
    )  # a 7-qubit lattice stored under 21
    assert hardware["qpu_seconds"] == 0.0


def test_ex5_2_packs_floats() -> None:
    answer, exercise = _submit(
        lab_floquet.grade_lab_floquet_ex5_2, np.float64(0.1), 0.2
    )
    assert exercise == "ex5_2"
    assert answer == {"value": 0.1, "error_bar": 0.2}
    assert type(answer["value"]) is float


@pytest.mark.parametrize(
    ("value", "error_bar", "match"),
    [
        (None, 0.01, "Set MZ2_74"),
        (float("nan"), 0.01, "finite"),
        (0.3, 0.0, "positive"),
        (0.3, None, "Set MZ2_74"),
    ],
)
def test_ex5_2_rejects_missing_or_invalid(
    value: Any, error_bar: Any, match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        lab_floquet.grade_lab_floquet_ex5_2(value, error_bar)
