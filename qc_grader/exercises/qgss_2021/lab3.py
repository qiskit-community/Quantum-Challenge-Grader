from qiskit import QuantumCircuit

from qc_grader.grade import grade_and_submit


def grade_lab3_ex1(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab3', 'ex1')


def grade_lab3_ex2(counts: dict) -> None:
    grade_and_submit(counts, 'lab3', 'ex2')
