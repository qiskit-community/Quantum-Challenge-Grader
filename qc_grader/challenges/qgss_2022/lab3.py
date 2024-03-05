import numpy

from typing import List, Dict
from typeguard import typechecked

from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

from qc_grader.custom_encoder.serializer import noisemodel_to_json
from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2022'


@typechecked
def grade_lab3_ex1(qc: QuantumCircuit) -> None:
    grade(qc, 'ex3-1', _challenge_id)


@typechecked
def grade_lab3_ex2(answer: Dict[str, int]) -> None:
    grade(answer, 'ex3-2', _challenge_id)


@typechecked
def grade_lab3_ex3(answer: List[float]) -> None:
    grade(answer, 'ex3-3', _challenge_id)


@typechecked
def grade_lab3_ex4(answer: List[float]) -> None:
    grade(answer, 'ex3-4', _challenge_id)


@typechecked
def grade_lab3_ex5(answer: List[float]) -> None:
    grade(answer, 'ex3-5', _challenge_id)


@typechecked
def grade_lab3_ex6(qc: QuantumCircuit) -> None:
    grade(qc, 'ex3-6', _challenge_id)


@typechecked
def grade_lab3_ex7(qc: QuantumCircuit) -> None:
    grade(qc, 'ex3-7', _challenge_id)


@typechecked
def grade_lab3_ex8(answer: numpy.ndarray) -> None:
    grade(answer, 'ex3-8', _challenge_id)


@typechecked
def grade_lab3_ex9(answer: numpy.ndarray) -> None:
    grade(answer, 'ex3-9', _challenge_id)


@typechecked
def grade_lab3_ex10(qc: QuantumCircuit) -> None:
    grade(qc, 'ex3-10', _challenge_id)


@typechecked
def grade_lab3_ex11(nm: NoiseModel) -> None:
    grade(noisemodel_to_json(nm), 'ex3-11', _challenge_id)
