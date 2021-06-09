from qiskit import QuantumCircuit
from qiskit_optimization import QuadraticProgram

from qc_grader.grade import grade_circuit, grade_json


criteria: dict = {}


def grade_lab2_ex1(answer: list) -> None:
    ok, _ = grade_json(answer, 'lab2', 'ex1', **criteria)


def grade_lab2_ex2(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    ok, _ = grade_json(answer, 'lab2', 'ex2', **criteria)


def grade_lab2_ex3(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab2', 'ex3', **criteria)


def grade_lab2_ex4(optimum: dict) -> None:
    ok, _ = grade_json(optimum, 'lab2', 'ex4', **criteria)
