from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit


criteria: dict = {}


def grade_ex2a(circuit: QuantumCircuit) -> None:
    grade_circuit(circuit, 'ex2', 'part1', **criteria)


def grade_ex2b(circuit: QuantumCircuit) -> None:
    grade_circuit(circuit, 'ex2', 'part2', **criteria)


def grade_ex2c(circuit: QuantumCircuit) -> None:
    grade_circuit(circuit, 'ex2', 'part3', **criteria)


def grade_ex2_final(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'ex2', 'part4', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex2_final(circuit: QuantumCircuit) -> None:
    submit_circuit(circuit, 'ex2', 'part4', **criteria)
