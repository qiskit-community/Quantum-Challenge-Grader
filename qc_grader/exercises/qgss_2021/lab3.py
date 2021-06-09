from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, grade_json
from qc_grader.util import circuit_to_json


criteria: dict = {}


def grade_lab3_ex1(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab3', 'ex1', **criteria)


def grade_lab3_ex2(qc: QuantumCircuit, counts: dict) -> None:
    answer = {
        'qc': circuit_to_json(qc),
        'counts': counts
    }
    ok, _ = grade_json(answer, 'lab3', 'ex2', **criteria)
