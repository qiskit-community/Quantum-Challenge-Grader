from qiskit import QuantumCircuit

from qc_grader.grade import grade, submit


def grade_ex1a(circuit: QuantumCircuit) -> None:
    if isinstance(circuit, QuantumCircuit):
        grade(circuit, 'week1', 'exA')
    else:
        print(f'Expected a QuantumCircuit, but was given {type(circuit)}')
        print(f'Please submit a circuit as your answer.')


def submit_ex1a(circuit: QuantumCircuit) -> None:
    if isinstance(circuit, QuantumCircuit):
        submit(circuit, 'week1', 'exA')
    else:
        print(f'Expected a QuantumCircuit, but was given {type(circuit)}')
        print(f'Please submit a circuit as your answer.')


def grade_ex1b(answer: int) -> None:
    if isinstance(answer, int):
        grade(answer, 'week1', 'exB')
    else:
        print(f'Expected a integer, but was given {type(answer)}')
        print(f'Please submit a number as your answer.')


def submit_ex1b(answer: int) -> None:
    if isinstance(answer, int):
        submit(answer, 'week1', 'exB')
    else:
        print(f'Expected a integer, but was given {type(answer)}')
        print(f'Please submit a number as your answer.')
