from typeguard import typechecked
from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade, get_problem_set

_challenge_id = 'fall_2022'

@typechecked
def grade_lab2_ex1(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-1', _challenge_id)


@typechecked
def grade_lab2_ex2(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-2', _challenge_id)


@typechecked
def grade_lab2_ex3(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-3', _challenge_id)


@typechecked
def grade_lab2_ex4(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-4', _challenge_id)


@typechecked
def grade_lab2_ex5(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-5', _challenge_id)


@typechecked
def grade_lab2_ex6(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-6', _challenge_id)
