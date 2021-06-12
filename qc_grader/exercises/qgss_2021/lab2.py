from typing import List

from qiskit import QuantumCircuit
from qiskit_optimization import QuadraticProgram

from qc_grader.grade import grade_and_submit


def grade_lab2_ex1(answer: List[int]) -> None:
    grade_and_submit(answer, 'lab2', 'ex1')


def grade_lab2_ex2(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, 'lab2', 'ex2')


def grade_lab2_ex3(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab2', 'ex3')


def grade_lab2_ex4(optimum: dict) -> None:
    grade_and_submit(optimum, 'lab2', 'ex4')
