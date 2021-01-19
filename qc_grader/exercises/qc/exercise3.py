from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex3(circuit: QuantumCircuit, m: int) -> None:
    if grade_circuit(circuit, 'ex3', str(m), **criteria):
        print('Feel free to submit your answer.')


def submit_ex3(circuit: QuantumCircuit, m: int) -> None:
    submit_circuit(circuit, 'ex3', str(m), **criteria)
