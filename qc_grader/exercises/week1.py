from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, grade_number, submit_circuit, submit_number


criteria: dict = {
    'max_qubits': 28,
    'min_cost': 30
}


def grade_ex1a(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'week1', 'exA', **criteria):
        print('Feel free to submit your answer.')


def submit_ex1a(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'week1', 'exA', **criteria)


def grade_ex1b(answer: int) -> None:
    if grade_number(answer, 'week1', 'exB'):
        print('Feel free to submit your answer.')


def submit_ex1b(answer: int) -> None:
    if submit_number(answer, 'week1', 'exB'):
        print('Have you ever wonder about the quantum realm? Ask Dr. Ryoko about it.')
