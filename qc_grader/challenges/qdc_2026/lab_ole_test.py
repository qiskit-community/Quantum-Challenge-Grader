"""Tests of the lab_ole grading functions: what each one packs, and the errors it raises."""

import math
from typing import Any
from unittest.mock import Mock, patch

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from typeguard import TypeCheckError

from qc_grader.challenges.qdc_2026 import lab_ole
from qc_grader.custom_encoder import to_json

_PATCH = "qc_grader.challenges.qdc_2026.lab_ole.grade_answer"


def _untyped(value: Any) -> Any:
    """A deliberately ill-typed argument, past the static type checker."""
    return value


def _sent(function: Any, *args: Any) -> dict:
    with patch(_PATCH) as grade:
        function(*args)
    grade.assert_called_once()
    answer = grade.call_args.args[0]
    assert len(to_json(answer)) < 1_000_000  # serialisable, and small
    return answer


def _echo(eta: Any, delta: Any) -> QuantumCircuit:
    qc = QuantumCircuit(lab_ole.NUM_QUBITS)
    qc.rx(0.5 - eta, 69)
    qc.rz(math.pi / 4, 69)
    qc.rzz(math.pi / 2, 69, 70)
    qc.barrier()
    qc.rx(2 * delta, 70)
    qc.id(71)
    return qc


def test_ex1_packs_gate_lists() -> None:
    answer = _sent(lab_ole.grade_lab_ole_ex1, _echo)
    assert len(answer["circuits"]) == len(lab_ole.PROBES_EX1)
    first = answer["circuits"][0]
    assert first["num_qubits"] == 156
    assert first["names"] == ["rx", "rz", "rzz", "rx"]  # barrier and id dropped
    assert first["qubits"] == [[69], [69], [69, 70], [70]]
    eta, delta = lab_ole.PROBES_EX1[0]
    assert first["params"] == [[0.5 - eta], [math.pi / 4], [math.pi / 2], [2 * delta]]
    assert all(type(x) is float for row in first["params"] for x in row)


def test_ex1_expands_custom_gates() -> None:
    def echo(eta: float, delta: float) -> QuantumCircuit:
        layer = QuantumCircuit(2, name="layer")
        layer.rx(eta, 0)
        layer.rzz(math.pi / 2, 0, 1)
        qc = QuantumCircuit(156)
        qc.append(layer.to_gate(), [69, 70])
        return qc

    answer = _sent(lab_ole.grade_lab_ole_ex1, echo)
    assert answer["circuits"][1]["names"] == ["rx", "rzz"]


def test_ex1_rejects_bad_returns() -> None:
    with pytest.raises(ValueError, match="Return a QuantumCircuit"):
        lab_ole.grade_lab_ole_ex1(lambda eta, delta: None)
    with pytest.raises(ValueError, match="free parameters"):
        lab_ole.grade_lab_ole_ex1(lambda eta, delta: _echo(Parameter("eta"), delta))


def test_ex1_reports_a_crashing_echo() -> None:
    def echo(eta: float, delta: float) -> QuantumCircuit:
        raise IndexError("index 156 is out of range")

    with pytest.raises(
        ValueError, match=r"Fix echo first: echo\(0.37, 0.21\) raised IndexError"
    ):
        lab_ole.grade_lab_ole_ex1(echo)


def test_ex2_packs_a_summary() -> None:
    isa = QuantumCircuit(156)
    isa.rz(Parameter("a"), 69)
    isa.sx(69)
    isa.cz(70, 69)
    isa.barrier()
    isa.cz(69, 78)
    answer = _sent(lab_ole.grade_lab_ole_ex2, isa, np.array([69, 70, 78]))
    assert answer == {
        "layout": [69, 70, 78],
        "num_qubits": 156,
        "num_parameters": 1,
        "operations": {"rz": 1, "sx": 1, "cz": 2, "barrier": 1},
        "two_qubit_gates": [[70, 69], [69, 78]],
    }
    assert all(type(q) is int for q in answer["layout"])


def test_ex2_rejects_unrouted_circuits() -> None:
    isa = QuantumCircuit(156)
    isa.ccx(0, 1, 2)
    with pytest.raises(ValueError, match="Transpile isa"):
        lab_ole.grade_lab_ole_ex2(isa, [0, 1, 2])
    with pytest.raises(ValueError, match="whole numbers"):
        lab_ole.grade_lab_ole_ex2(QuantumCircuit(156), np.array([0.5, 1.0]))
    with pytest.raises(TypeCheckError):
        lab_ole.grade_lab_ole_ex2(QuantumCircuit(156), _untyped([0.5, 1.0]))


def _job(
    job_id: str = "d0abc",
    backend: str = "ibm_boston",
    usage: float = 42.0,
    status: str = "DONE",
) -> Mock:
    job = Mock()
    job.job_id.return_value = job_id
    job.status.return_value = status
    job.backend.return_value.name = backend
    job.usage.return_value = usage
    return job


def test_ex3_packs_floats_and_job_records() -> None:
    answer = _sent(
        lab_ole.grade_lab_ole_ex3,
        list(lab_ole.POINTS),
        np.array([0.9, 0.8, 0.7, 0.6, 0.5]),
        [np.float64(0.05)] * 5,
        [_job("d0a"), _job("d0b", usage=np.float64(10))],
    )
    assert answer["estimates"] == [0.9, 0.8, 0.7, 0.6, 0.5]
    assert all(type(x) is float for x in answer["estimates"] + answer["errors"])
    assert answer["jobs"] == [
        {"job_id": "d0a", "backend": "ibm_boston", "usage_seconds": 42.0},
        {"job_id": "d0b", "backend": "ibm_boston", "usage_seconds": 10.0},
    ]


def test_ex3_resolves_job_ids() -> None:
    service = Mock()
    service.job.side_effect = lambda job_id: _job(job_id)
    with patch("qiskit_ibm_runtime.QiskitRuntimeService", return_value=service):
        answer = _sent(
            lab_ole.grade_lab_ole_ex3,
            lab_ole.POINTS,
            [1.0] * 5,
            [0.1] * 5,
            ["d0a", "d0b"],
        )
    assert [j["job_id"] for j in answer["jobs"]] == ["d0a", "d0b"]


@pytest.mark.parametrize(
    ("args", "words"),
    [
        ((lab_ole.POINTS[:4], [1.0] * 5, [0.1] * 5), "POINTS"),
        ((lab_ole.FOLD_POINTS, [1.0] * 5, [0.1] * 5), "POINTS"),
        ((lab_ole.POINTS, [1.0] * 4, [0.1] * 5), "5 numbers"),
    ],
)
def test_ex3_rejects_bad_inputs(args: tuple, words: str) -> None:
    points, estimates, errors = args
    with pytest.raises(ValueError, match=words):
        lab_ole.grade_lab_ole_ex3(points, estimates, errors, [_job()])


def test_ex3_wrong_types_are_type_errors() -> None:
    with pytest.raises(TypeCheckError):
        lab_ole.grade_lab_ole_ex3(
            lab_ole.POINTS, _untyped(["a"] * 5), [0.1] * 5, [_job()]
        )


def test_ex3_rejects_unfinished_and_missing_jobs() -> None:
    with pytest.raises(ValueError, match="status RUNNING"):
        lab_ole.grade_lab_ole_ex3(
            lab_ole.POINTS, [1.0] * 5, [0.1] * 5, [_job(status="RUNNING")]
        )
    with pytest.raises(ValueError, match="List the jobs"):
        lab_ole.grade_lab_ole_ex3(lab_ole.POINTS, [1.0] * 5, [0.1] * 5, [])
    with pytest.raises(ValueError, match="job objects or job id strings"):
        lab_ole.grade_lab_ole_ex3(lab_ole.POINTS, [1.0] * 5, [0.1] * 5, [42])


def test_ex4_packs_both_levels() -> None:
    answer = _sent(
        lab_ole.grade_lab_ole_ex4,
        lab_ole.FOLD_POINTS,
        [0.7, 0.6, 0.5],
        [0.02] * 3,
        np.array([0.75, 0.65, 0.5]),
        [0.04] * 3,
        np.float64(1.5),
        [_job()],
    )
    assert answer["noise_factor"] == 1.5 and type(answer["noise_factor"]) is float
    assert answer["amplified"] == [0.75, 0.65, 0.5]
    assert set(answer) == {
        "native",
        "native_errors",
        "amplified",
        "amplified_errors",
        "noise_factor",
        "jobs",
    }


def test_questions_are_normalized() -> None:
    answers = {key: " b" for key in lab_ole.QUESTIONS}
    answer = _sent(lab_ole.grade_lab_ole_questions, {**answers, "extra": "A"})
    assert answer == {key: "B" for key in lab_ole.QUESTIONS}


def test_questions_need_every_key() -> None:
    with pytest.raises(ValueError, match="cz"):
        lab_ole.grade_lab_ole_questions(
            {key: "A" for key in lab_ole.QUESTIONS if key != "cz"}
        )
