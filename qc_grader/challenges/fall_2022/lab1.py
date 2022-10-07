from typeguard import typechecked
from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade, get_problem_set

_challenge_id = 'fall_2022'

@typechecked
def grade_lab1_ex1(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-1', _challenge_id)


@typechecked
def grade_lab1_ex2(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-2', _challenge_id)


@typechecked
def grade_lab1_ex3(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-3', _challenge_id)


@typechecked
def grade_lab1_ex4(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-4', _challenge_id)


@typechecked
def grade_lab1_ex5(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-5', _challenge_id)


@typechecked
def grade_lab1_ex6(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-6', _challenge_id)


@typechecked
def grade_lab1_ex7(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-7',_challenge_id)


@typechecked
def grade_lab1_ex8(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-8', _challenge_id)   

@typechecked
def grade_lab1_ex9(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-9', _challenge_id)   
