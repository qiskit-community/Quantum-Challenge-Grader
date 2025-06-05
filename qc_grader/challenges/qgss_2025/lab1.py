import json

from typing import Callable, Type

from typeguard import typechecked


from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter
import numpy as np

from qc_grader.grader.grade import grade
from .utils import get_qc_in


_challenge_id = 'qgss_2025'

correct_message = 'Congratulations! 🎉 Your answer is correct.'
incorrect_message = 'Sorry, your answer is incorrect. Please try again.'

@typechecked
def grade_lab1_ex1_1(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex1-1', _challenge_id)


@typechecked
def grade_lab1_ex1_2(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex1-2', _challenge_id)

@typechecked
def grade_lab1_ex1_3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex1-3', _challenge_id)

@typechecked
def grade_lab1_ex1_4(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex1-4', _challenge_id)



# Check for cheating
@typechecked
def grade_lab1_ex2(answer_func: Callable) -> None:
    circuit=answer_func(np.pi/3)[1]
    grade(circuit, 'lab1-ex2', _challenge_id)

@typechecked
def grade_lab1_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex3', _challenge_id)

# Check for cheating
@typechecked
def grade_lab1_ex4(answer_func: Callable) -> None:
    circuit=answer_func(1,1)
    grade(circuit, 'lab1-ex4', _challenge_id)

@typechecked
#def grade_lab1_ex5(answer: tuple[list,float]) -> None:
def grade_lab1_ex5(counts_list: list, avg_win_prob: float) -> None:
    answer= tuple[counts_list,avg_win_prob]
    grade(answer, 'lab1-ex5', _challenge_id)

@typechecked
def grade_lab1_ex6(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex6', _challenge_id)



