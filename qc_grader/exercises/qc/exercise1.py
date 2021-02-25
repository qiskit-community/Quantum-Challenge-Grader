from os import stat
from qiskit import QuantumCircuit

from qc_grader.grade import grade_circuit, submit_circuit, handle_grade_response
from qc_grader.exercises.qc.utils import precheck_exercise


criteria: dict = {}


def grade_ex1a(circuit: QuantumCircuit) -> None:
    ok, msg = precheck_exercise(circuit, 1, 1)
    if not ok:
        handle_grade_response('invalid', cause=msg)
    else:
        ok, _ = grade_circuit(circuit, 'ex1', 'partA', **criteria)
        if ok:
            print('Feel free to submit your answer.\r\n')


def grade_ex1b(circuit: QuantumCircuit) -> None:
    ok, msg = precheck_exercise(circuit, 1, 2)
    if not ok:
        handle_grade_response('invalid', cause=msg)
    else:
        ok, _ = grade_circuit(circuit, 'ex1', 'partB', **criteria)
        if ok:
            print('Feel free to submit your answer.\r\n')


def grade_ex1c(circuit: QuantumCircuit) -> None:
    ok, msg = precheck_exercise(circuit, 1, 3)
    if not ok:
        handle_grade_response('invalid', cause=msg)
    else:
        ok, _ = grade_circuit(circuit, 'ex1', 'partC', **criteria)
        if ok:
            print('Feel free to submit your answer.\r\n')


def submit_ex1a(circuit: QuantumCircuit) -> None:
    ok, msg = precheck_exercise(circuit, 1, 1)
    if not ok:
        handle_grade_response('invalid', cause=msg)
    else:
        submit_circuit(circuit, 'ex1', 'partA', **criteria)


def submit_ex1b(circuit: QuantumCircuit) -> None:
    ok, msg = precheck_exercise(circuit, 1, 2)
    if not ok:
        handle_grade_response('invalid', cause=msg)
    else:
        submit_circuit(circuit, 'ex1', 'partB', **criteria)


def submit_ex1c(circuit: QuantumCircuit) -> None:
    ok, msg = precheck_exercise(circuit, 1, 3)
    if not ok:
        handle_grade_response('invalid', cause=msg)
    else:
        submit_circuit(circuit, 'ex1', 'partC', **criteria)
