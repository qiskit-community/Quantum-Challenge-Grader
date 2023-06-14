from typeguard import typechecked
from typing import Dict, Sequence, Union

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.opflow import PauliSumOp
from qiskit.quantum_info import SparsePauliOp
from qiskit.result.result import Result

from qc_grader.grader.grade import grade
from qc_grader.grader.common import circuit_to_json, serialize_answer


_challenge_id = "qgss_2023"


@typechecked
def grade_lab2_ex1(obsv: Union[PauliSumOp, SparsePauliOp]) -> None:
    answer = {
        'obsv': serialize_answer(obsv),
        'obsv_type': type(obsv).__name__
    }

    grade(answer, "ex2-1", _challenge_id)


@typechecked
def grade_lab2_ex2(
    obsv: Union[PauliSumOp, SparsePauliOp],
    angles: Union[Sequence[float], Sequence[Sequence[float]]]
) -> None:
    answer = {
        'obsv': serialize_answer(obsv),
        'obsv_type': type(obsv).__name__,
        'angles': angles
    }
    grade(answer, "ex2-2", _challenge_id)


@typechecked
def grade_lab2_ex3(
    tele_qc: QuantumCircuit,
    theta: Parameter,
    angle: float,
) -> None:
    answer = {
        'tele_qc': circuit_to_json(tele_qc, byte_string=True),
        'param': theta,
        'angle': angle
    }
    grade(answer, "ex2-3", _challenge_id)


@typechecked
def grade_lab2_ex4(tele_counts: Dict, result: Result) -> None:
    answer = {
        'tele_counts': tele_counts,
        'result': result
    }
    grade(answer, "ex2-4", _challenge_id)
