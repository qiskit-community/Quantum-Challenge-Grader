from qiskit import QuantumCircuit
from typeguard import typechecked

from qc_grader.grader.grade import grade


_challenge_id = "qgss_2023"


@typechecked
def grade_lab4_ex1(circuit: QuantumCircuit) -> None:
    grade(circuit, "ex4-1", _challenge_id, byte_string=True)


@typechecked
def grade_lab4_ex2(circuit: QuantumCircuit) -> None:
    grade(circuit, "ex4-2", _challenge_id, byte_string=True)


@typechecked
def grade_lab4_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, "ex4-3", _challenge_id, byte_string=True)


@typechecked
def grade_lab4_ex4(step1_bit: int) -> None:
    grade(step1_bit, "ex4-4", _challenge_id)


@typechecked
def grade_lab4_ex5(circuit: QuantumCircuit) -> None:
    grade(circuit, "ex4-5", _challenge_id, byte_string=True)
