"""QDC 2026, "Operator Loschmidt echo" (lab ``lab_ole``): the grading functions.

One ``grade_lab_ole_<ex>`` function per exercise of the notebook. Each function packs the
notebook variables it receives into one JSON-serialisable answer and sends it with
``grade_answer``; the server validator of the same exercise grades it.

- ``echo``, the participant's function, is called here at fixed probe points; its circuits are
  sent as lists of standard gates (a circuit as QPY would be about 1.6 MB).
- The compiled template of Exercise 2 is summarized: its operation counts, number of free
  parameters and the qubits of its two-qubit gates, in circuit order.
- Hardware jobs are reduced to plain data: job id, backend name and QPU usage. These numbers
  are self-reported: the server cannot reach IBM Quantum, and the organizers may audit the job
  ids after the event.

The section "Shared definitions" holds the constants that the server module
``validations/qdc_2026/lab_ole.py`` defines identically. The server uses its own copy and never
trusts probe values echoed in an answer.

Ids (proposed until the maintainer confirms them): challenge ``qdc_2026``, lab ``lab_ole``,
exercises ``ex1 ex2 ex3 ex4 questions``.
"""

# The client contract raises ValueError, with the fix first, for every bad input, type
# problems included (spec section 4.2), so ruff's TypeError preference does not apply.
# ruff: noqa: TRY004

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import get_standard_gate_name_mapping
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"  # the id the maintainer assigns; identical on the server
_LAB = "lab_ole"  # the lab id; identical on the server


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


# ------------------------------------------------------------------------------------------
# Shared definitions (identical in the server module; the server uses its own copy)
# ------------------------------------------------------------------------------------------
NUM_QUBITS = 156  # the published qubit labels are ibm_boston's physical qubits
PROBES_EX1 = ((0.37, 0.21), (1.05, 0.6))  # (eta, delta) at which echo is called
# Off the paper's eta grid (multiples of 3pi/40), where no published or tutorial results exist.
ETA_SWEEP = 11 * math.pi / 40
POINTS = (
    (0.0, 0.3),
    (ETA_SWEEP, 0.0),
    (ETA_SWEEP, 0.1),
    (ETA_SWEEP, 0.2),
    (ETA_SWEEP, 0.3),
)
FOLD_POINTS = ((math.pi / 8, 0.3), (ETA_SWEEP, 0.3), (13 * math.pi / 40, 0.3))
QUESTIONS = ("eta0", "cz", "repdelay", "control", "errors", "drift", "canary")

_STANDARD = set(get_standard_gate_name_mapping()) - {
    "barrier",
    "delay",
    "id",
    "global_phase",
}
_DROPPED = {"barrier", "delay", "id", "global_phase"}
_MAX_GATES = 20_000
_MAX_JOBS = 50


# ------------------------------------------------------------------------------------------
# Exercise 1: build the echo
# ------------------------------------------------------------------------------------------
def _standard_gates(qc: QuantumCircuit, where: str) -> QuantumCircuit:
    """``qc`` with custom gates expanded until only standard gates remain."""
    for _ in range(8):
        custom = sorted(
            {i.operation.name for i in qc.data}
            - _STANDARD
            - _DROPPED
            - {"measure", "reset"}
        )
        if not custom:
            return qc
        qc = qc.decompose(gates_to_decompose=custom)
    raise ValueError(
        f"Build {where} from standard gates (rx, rz, rzz): it contains {custom}, which do not decompose."
    )


def _gate_list(qc: QuantumCircuit, where: str) -> dict[str, Any]:
    """The circuit as columns of standard gates, without barriers, delays and identities."""
    qc = _standard_gates(qc, where)
    names: list[str] = []
    qubits: list[list[int]] = []
    params: list[list[float]] = []
    for inst in qc.data:
        name = inst.operation.name
        if name in _DROPPED:
            continue
        names.append(str(name))
        qubits.append([int(qc.find_bit(q).index) for q in inst.qubits])
        params.append([float(p) for p in inst.operation.params])
        if len(names) > _MAX_GATES:
            raise ValueError(
                f"Return a smaller circuit from {where}: it has more than {_MAX_GATES} gates."
            )
    return {
        "num_qubits": int(qc.num_qubits),
        "names": names,
        "qubits": qubits,
        "params": params,
    }


@typechecked
def grade_lab_ole_ex1(echo: Callable[..., Any]) -> None:
    """Submit your function ``echo(eta, delta)``. It is called here at two fixed points with
    floats, and must return a ``QuantumCircuit(NUM_DEVICE_QUBITS)`` without free parameters."""
    circuits = []
    for eta, delta in PROBES_EX1:
        where = f"echo({eta}, {delta})"
        try:
            qc = echo(eta, delta)
        except Exception as err:  # noqa: BLE001 - the participant's code; reported as a hint
            raise ValueError(
                f"Fix echo first: {where} raised {type(err).__name__}: {err}. "
                f"Run {where} in a cell to see the full traceback."
            ) from None
        if not isinstance(qc, QuantumCircuit):
            raise ValueError(
                f"Return a QuantumCircuit from echo: {where} returned {type(qc).__name__}."
            )
        if qc.num_parameters:
            names = sorted(p.name for p in qc.parameters)
            raise ValueError(
                f"Use eta and delta for every angle: {where} has free parameters {names}."
            )
        circuits.append(_gate_list(qc, where))
    _grade({"circuits": circuits}, "ex1")


# ------------------------------------------------------------------------------------------
# Exercise 2: place and compile
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_ole_ex2(isa: QuantumCircuit, layout: Sequence[int] | np.ndarray) -> None:
    """Submit ``isa``, your compiled template (input preparation and echo, with free
    parameters), and ``layout``, where ``layout[k]`` is the physical qubit of ``QUBITS[k]``."""
    places = np.asarray(layout).ravel()
    if places.dtype.kind not in "iu":
        raise ValueError(
            "Give layout as whole numbers: the physical qubit of each entry of QUBITS."
        )
    gates: list[list[int]] = []
    for inst in isa.data:
        op = inst.operation
        if op.name == "barrier" or op.num_qubits < 2:
            continue
        if op.num_qubits > 2:
            raise ValueError(
                f"Transpile isa for the backend: it contains '{op.name}' on {op.num_qubits} qubits."
            )
        gates.append([int(isa.find_bit(q).index) for q in inst.qubits])
        if len(gates) > _MAX_GATES:
            raise ValueError(
                f"Submit a smaller isa: it has more than {_MAX_GATES} two-qubit gates."
            )
    answer = {
        "layout": [int(q) for q in places],
        "num_qubits": int(isa.num_qubits),
        "num_parameters": int(isa.num_parameters),
        "operations": {str(k): int(v) for k, v in isa.count_ops().items()},
        "two_qubit_gates": gates,
    }
    _grade(answer, "ex2")


# ------------------------------------------------------------------------------------------
# Exercises 3 and 4: hardware estimates (self-reported)
# ------------------------------------------------------------------------------------------
def _check_points(points: Any, expected: tuple, name: str) -> None:
    try:
        given = np.asarray(points, dtype=float)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Pass {name} as defined in the setup cell.") from err
    if given.shape != (len(expected), 2) or not np.allclose(given, expected, atol=1e-9):
        raise ValueError(
            f"Pass {name} as defined in the setup cell, unchanged: the grader scores those points."
        )


def _floats(values: Any, n: int, name: str) -> list[float]:
    try:
        out = [float(x) for x in np.asarray(values, dtype=float).ravel()]
    except (TypeError, ValueError) as err:
        raise ValueError(f"Give {name} as {n} numbers.") from err
    if len(out) != n:
        raise ValueError(f"Give {name} as {n} numbers, one per point; got {len(out)}.")
    return out


def _job_records(jobs: Sequence[Any], name: str) -> list[dict[str, Any]]:
    """Job id, backend name and QPU usage of each job (objects or job id strings)."""
    if isinstance(jobs, str) or len(jobs) == 0:
        raise ValueError(
            f"List the jobs in {name}: a list of job objects or job id strings."
        )
    if len(jobs) > _MAX_JOBS:
        raise ValueError(f"List at most {_MAX_JOBS} jobs in {name}.")
    service = None
    records = []
    for job in jobs:
        if isinstance(job, str):
            if service is None:
                from qiskit_ibm_runtime import (
                    QiskitRuntimeService,
                )  # only needed for job ids

                service = QiskitRuntimeService()
            job = service.job(job)
        if not callable(getattr(job, "job_id", None)):
            raise ValueError(
                f"List jobs in {name} as job objects or job id strings, not {type(job).__name__}."
            )
        status = job.status()
        status = getattr(status, "name", status)
        if str(status) != "DONE":
            raise ValueError(
                f"Grade jobs that finished: {job.job_id()} has status {status}."
            )
        backend = job.backend()
        usage = job.usage() if callable(getattr(job, "usage", None)) else 0.0
        records.append(
            {
                "job_id": str(job.job_id()),
                "backend": str(getattr(backend, "name", backend or "")),
                "usage_seconds": float(usage or 0.0),
            }
        )
    return records


@typechecked
def grade_lab_ole_ex3(
    points: Sequence[Sequence[float]] | np.ndarray,
    estimates: Sequence[float] | np.ndarray,
    errors: Sequence[float] | np.ndarray,
    jobs: Sequence[Any],
) -> None:
    """Submit ``estimates`` and ``errors`` (one per entry of ``POINTS``, in order) and ``jobs``,
    every runtime job of the run they come from (job objects or job id strings)."""
    _check_points(points, POINTS, "POINTS")
    answer = {
        "estimates": _floats(estimates, len(POINTS), "estimates"),
        "errors": _floats(errors, len(POINTS), "errors"),
        "jobs": _job_records(jobs, "jobs"),
    }
    _grade(answer, "ex3")


@typechecked
def grade_lab_ole_ex4(
    points: Sequence[Sequence[float]] | np.ndarray,
    native: Sequence[float] | np.ndarray,
    native_errors: Sequence[float] | np.ndarray,
    amplified: Sequence[float] | np.ndarray,
    amplified_errors: Sequence[float] | np.ndarray,
    noise_factor: float | np.floating,
    jobs: Sequence[Any],
) -> None:
    """Submit the estimates and errors at native and amplified noise (one per entry of
    ``FOLD_POINTS``, in order), the ``noise_factor`` and the jobs they come from."""
    _check_points(points, FOLD_POINTS, "FOLD_POINTS")
    n = len(FOLD_POINTS)
    answer = {
        "native": _floats(native, n, "native"),
        "native_errors": _floats(native_errors, n, "native_errors"),
        "amplified": _floats(amplified, n, "amplified"),
        "amplified_errors": _floats(amplified_errors, n, "amplified_errors"),
        "noise_factor": float(noise_factor),
        "jobs": _job_records(jobs, "fold_jobs"),
    }
    _grade(answer, "ex4")


# ------------------------------------------------------------------------------------------
# Questions
# ------------------------------------------------------------------------------------------
@typechecked
def grade_lab_ole_questions(answers: Mapping[str, str]) -> None:
    """Submit ``ANSWERS``, the letter of your answer to each of the seven questions."""
    missing = [key for key in QUESTIONS if key not in answers]
    if missing:
        raise ValueError(f"Keep every key of ANSWERS: {', '.join(missing)} is missing.")
    _grade({key: str(answers[key]).strip().upper() for key in QUESTIONS}, "questions")
