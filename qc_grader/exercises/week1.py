from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, grade_number, submit_circuit, submit_number


def grade_ex1a(circuit: QuantumCircuit) -> None:
    grade_circuit(circuit, 'week1', 'exA')


def submit_ex1a(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'week1', 'exA')


def grade_ex1b(answer: int) -> None:
    grade_number(answer, 'week1', 'exB')


def submit_ex1b(answer: int) -> None:
    if submit_number(answer, 'week1', 'exB'):
        print('Have you ever wonder about the quantum realm? Ask Dr. Ryoko about it.')
