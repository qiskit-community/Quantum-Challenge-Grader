from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, grade_json


criteria: dict = {}


def grade_lab3_ex1(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab3', 'ex1', **criteria)


def grade_lab3_ex2(counts: dict) -> None:
    ok, _ = grade_json(counts, 'lab3', 'ex2', **criteria)
