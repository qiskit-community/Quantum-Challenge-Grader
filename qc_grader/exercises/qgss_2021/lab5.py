from qiskit import QuantumCircuit
from qiskit.quantum_info.operators.operator import Operator
from qiskit.providers.aer.noise import NoiseModel

from qc_grader.grade import grade_circuit, grade_json, grade_number
from qc_grader.util import circuit_to_json


criteria: dict = {}


def grade_lab5_ex1(
    qc: QuantumCircuit,
    u: Operator
) -> None:
    answer = {
        'qc': circuit_to_json(qc),
        'u': u
    }
    ok, _ = grade_json(answer, 'lab5', 'ex1', **criteria)


def grade_lab5_ex2(answer: float) -> None:
    ok, _ = grade_number(answer, 'lab5', 'ex2', **criteria)


def grade_lab5_ex3(nm: NoiseModel) -> None:
    answer = {
        'nm': nm
    }
    ok, _ = grade_json(answer, 'lab5', 'ex3', **criteria)


def grade_lab5_ex4(answer: float) -> None:
    ok, _ = grade_number(answer, 'lab5', 'ex4', **criteria)


def grade_lab5_ex5(answer: float) -> None:
    ok, _ = grade_number(answer, 'lab5', 'ex5', **criteria)
