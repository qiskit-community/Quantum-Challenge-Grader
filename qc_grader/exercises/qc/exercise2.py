from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex2a(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'ex2', 'partA', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex2b(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'ex2', 'partB', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex2a(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex2', 'partA', **criteria)


def submit_ex2b(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex2', 'partB', **criteria)
