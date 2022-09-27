from typeguard import typechecked
from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade, get_problem_set

_challenge_id = 'fall_2022'

@typechecked
def grade_lab4_ex1(qc: QuantumCircuit) -> None:
    grade(qc, 'ex4-1', _challenge_id)


@typechecked
def grade_lab4_ex2(qc: QuantumCircuit) -> None:
    grade(qc, 'ex4-2', _challenge_id)


@typechecked
def grade_lab4_ex3(qc: QuantumCircuit) -> None:
    grade(qc, 'ex4-3', _challenge_id)
