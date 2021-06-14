from qiskit import QuantumCircuit
from qiskit.providers.aer.noise import NoiseModel

from qc_grader.grade import grade_and_submit
from qc_grader.util import noisemodel_to_json


criteria: dict = {}


def grade_lab5_ex1(
    qc: QuantumCircuit,
) -> None:
    grade_and_submit(qc, 'lab5', 'ex1')


def grade_lab5_ex2(answer: float) -> None:
    grade_and_submit(answer, 'lab5', 'ex2')


def grade_lab5_ex3(noise_model: NoiseModel) -> None:
    answer = {
        'noise_model': noisemodel_to_json(noise_model)
    }
    grade_and_submit(answer, 'lab5', 'ex3')


def grade_lab5_ex4(answer: float) -> None:
    grade_and_submit(answer, 'lab5', 'ex4')


def grade_lab5_ex5(answer: float) -> None:
    grade_and_submit(answer, 'lab5', 'ex5')
