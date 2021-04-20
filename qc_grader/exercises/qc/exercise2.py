from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex2(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'ex2', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex2(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex2', **criteria)
