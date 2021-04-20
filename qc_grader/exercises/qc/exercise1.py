from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex1(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'ex1', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex1(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex1', **criteria)
