from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, grade_json


criteria: dict = {}


def grade_lab1_ex1(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab1', 'ex1', **criteria)


def grade_lab1_ex2(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab1', 'ex2', **criteria)


def grade_lab1_ex3(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab1', 'ex3', **criteria)


def grade_lab1_ex4(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab1', 'ex4', **criteria)


def grade_lab1_ex5(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab1', 'ex5', **criteria)


def grade_lab1_ex6(circuit: QuantumCircuit) -> None:
    ok, _ = grade_circuit(circuit, 'lab1', 'ex6', **criteria)


def grade_lab1_ex7(answer: list) -> None:
    ok, _ = grade_json(answer, 'lab1', 'ex7', **criteria)


def grade_lab1_ex8(circuit: QuantumCircuit) -> None:
    decomposed_circuit = circuit.decompose()
    ok, _ = grade_circuit(decomposed_circuit, 'lab1', 'ex8', **criteria)
