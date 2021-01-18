from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex1a(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'ex1', 'partA', **criteria):
        print('Feel free to submit your answer.')


def grade_ex1b(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'ex1', 'partB', **criteria):
        print('Feel free to submit your answer.')


def grade_ex1c(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'ex1', 'partC', **criteria):
        print('Feel free to submit your answer.')


def submit_ex1a(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex1', 'partA', **criteria)


def submit_ex1b(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex1', 'partB', **criteria)


def submit_ex1c(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex1', 'partC', **criteria)
