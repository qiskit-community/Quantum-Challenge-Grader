from qiskit import QuantumCircuit
from qiskit.providers.aer.noise import NoiseModel

from qc_grader.grade import grade_circuit, grade_json, grade_number
from qc_grader.util import noisemodel_to_json


criteria: dict = {}


def grade_lab5_ex1(
    qc: QuantumCircuit,
) -> None:
    ok, _ = grade_circuit(qc, 'lab5', 'ex1', **criteria)


def grade_lab5_ex2(answer: float) -> None:
    ok, _ = grade_number(answer, 'lab5', 'ex2', **criteria)


def grade_lab5_ex3(noise_model: NoiseModel) -> None:
    answer = {
        'noise_model': noisemodel_to_json(noise_model)
    }
    ok, _ = grade_json(answer, 'lab5', 'ex3', **criteria)


def grade_lab5_ex4(answer: float) -> None:
    ok, _ = grade_number(answer, 'lab5', 'ex4', **criteria)


def grade_lab5_ex5(answer: float) -> None:
    ok, _ = grade_number(answer, 'lab5', 'ex5', **criteria)
