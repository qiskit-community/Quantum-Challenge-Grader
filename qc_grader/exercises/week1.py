from qiskit import QuantumCircuit

from qc_grader.grade import grade, submit


def grade_ex1a(circuit: QuantumCircuit) -> None:
    grade(circuit, 'week1', 'exA')


def submit_ex1a(circuit: QuantumCircuit) -> None:
    submit(circuit, 'week1', 'exA')


def grade_ex1b(answer: int) -> None:
    grade(answer, 'week1', 'exB')


def submit_ex1b(answer: int) -> None:
    submit(answer, 'week1', 'exB')
