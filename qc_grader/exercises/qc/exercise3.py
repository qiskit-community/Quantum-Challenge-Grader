from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex3a(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'ex3', 'partA', **criteria):
        print('Feel free to submit your answer.')


def grade_ex3b(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'ex3', 'partB', **criteria):
        print('Feel free to submit your answer.')


def grade_ex3c(circuit: QuantumCircuit) -> None:
    if grade_circuit(circuit, 'ex3', 'partC', **criteria):
        print('Feel free to submit your answer.')


def submit_ex3a(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex3', 'partA', **criteria)


def submit_ex3b(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex3', 'partB', **criteria)


def submit_ex3c(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex3', 'partC', **criteria)
