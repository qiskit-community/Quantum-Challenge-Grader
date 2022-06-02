from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade, get_problem_set


_challenge_id = 'qgss_2022'


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
def grade_lab1_ex7(numberOfGatesFnc: Callable) -> None:
    _, inputs = get_problem_set('ex1-7', _challenge_id)

    answer = []
    for i in inputs:
        result = numberOfGatesFnc(i)
        answer.append((i, result))

    grade(answer, 'ex1-7', _challenge_id, max_content_length=2*1024*1024)


@typechecked
def grade_lab1_ex8(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-8', _challenge_id)   
