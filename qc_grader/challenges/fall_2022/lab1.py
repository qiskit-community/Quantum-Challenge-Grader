from typeguard import typechecked
from typing import Callable, List
from qiskit import Aer, execute
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade, get_problem_set

_challenge_id = 'fall_2022'

@typechecked
def grade_lab1_ex1(func: Callable) -> None:
    _, inputs = get_problem_set('ex1-1', _challenge_id)

    backend = Aer.get_backend('qasm_simulator')

    answer = []
    for i in inputs:
        circuit = func(i)
        job = execute(circuit, backend, shots=1024)
        answer.append([i, job])

    grade(answer, 'ex1-1', _challenge_id)

@typechecked
def grade_lab1_ex2(result: SamplerResult) -> None:
    grade(result, 'ex1-2', _challenge_id)

@typechecked
def grade_lab1_ex3(result: EstimatorResult) -> None:
    grade(result, 'ex1-3', _challenge_id)

@typechecked
def grade_lab1_ex4(answer: List) -> None:
    grade(answer, 'ex1-4', _challenge_id)

@typechecked
def grade_lab1_ex5(result: SamplerResult) -> None:
    grade(result.quasi_dists[0], 'ex1-5', _challenge_id)

@typechecked
def grade_lab1_ex6(message: str) -> None:
    grade(message, 'ex1-6', _challenge_id)
