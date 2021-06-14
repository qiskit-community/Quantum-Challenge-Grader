from qiskit import QuantumCircuit

from qc_grader.grade import grade_and_submit


def grade_lab1_ex1(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab1', 'ex1')


def grade_lab1_ex2(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab1', 'ex2')


def grade_lab1_ex3(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab1', 'ex3')


def grade_lab1_ex4(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab1', 'ex4')


def grade_lab1_ex5(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab1', 'ex5')


def grade_lab1_ex6(circuit: QuantumCircuit) -> None:
    grade_and_submit(circuit, 'lab1', 'ex6')


def grade_lab1_ex7(answer: list) -> None:
    grade_and_submit(answer, 'lab1', 'ex7')


def grade_lab1_ex8(circuit: QuantumCircuit) -> None:
    decomposed_circuit = circuit.decompose()
    grade_and_submit(decomposed_circuit, 'lab1', 'ex8')
