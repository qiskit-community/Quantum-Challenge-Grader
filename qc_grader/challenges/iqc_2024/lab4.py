from typing import List, Callable
from typeguard import typechecked
from qiskit.circuit import Parameter
from math import pi

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab4_ex1(answer: QuantumCircuit) -> None:
    grade(answer, 'lab4-ex1', _challenge_id)


@typechecked
def grade_lab4_ex2(answer: QuantumCircuit) -> None:
    answer_mod = answer.assign_parameters({"theta":pi})
    grade(answer_mod, 'lab4-ex2', _challenge_id)


@typechecked
def grade_lab4_ex3(fn: Callable) -> None:
    answer = fn(range(9),9)
    grade(answer, "lab4-ex3", _challenge_id)

@typechecked
def grade_lab4_ex4(good_qubits: list, layer_couplings: list) -> None:
    grade([good_qubits, layer_couplings], "lab4-ex4", _challenge_id)

@typechecked
def grade_lab4_ex5(pub: tuple) -> None:
    grade(pub, "lab4-ex5", _challenge_id)

@typechecked
def grade_lab4_ex6(options: dict) -> None:
    grade(options, "lab4-ex6", _challenge_id)

@typechecked
def grade_lab4_ex7(max_feasible_circuit_depth: int) -> None:
    grade(max_feasible_circuit_depth, "lab4-ex7", _challenge_id)