import numpy as np 
from typeguard import typechecked

from typing import List, Dict

from qiskit.quantum_info import Statevector, Operator
from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2023'


@typechecked
def grade_lab1_ex1(braket_list: List[List]) -> None:
    grade(braket_list, 'ex1-1', _challenge_id)

@typechecked
def grade_lab1_ex2(sv_valid: Statevector) -> None:
    grade(sv_valid.data, 'ex1-2', _challenge_id)

@typechecked
def grade_lab1_ex3(braket_list: List) -> None:
    grade(braket_list, 'ex1-3', _challenge_id)

@typechecked
def grade_lab1_ex4(answer_list: List) -> None:
    grade(answer_list, 'ex1-4', _challenge_id)

@typechecked
def grade_lab1_ex5(answer_list: List[Operator]) -> None:
    answer_data = [answer_list[0].data, answer_list[1].data]
    grade(answer_data, 'ex1-5', _challenge_id)

@typechecked
def grade_lab1_ex6(op: Operator) -> None:
    grade(op.data, 'ex1-6', _challenge_id)

@typechecked
def grade_lab1_ex7(result: np.ndarray) -> None:
    grade(result, 'ex1-7', _challenge_id)

@typechecked
def grade_lab1_ex8(qc: QuantumCircuit) -> None:
    grade(qc, 'ex1-8', _challenge_id)

@typechecked
def grade_lab1_ex9(answer_list: List[Dict]) -> None:
    grade(answer_list, 'ex1-9', _challenge_id)
