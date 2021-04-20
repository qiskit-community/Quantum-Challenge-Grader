from typing import List
from qiskit import QuantumCircuit

from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json


criteria: dict = {}


def format_submission(circuit: QuantumCircuit, initial_layout: List) -> dict:
    return {
        'qc': circuit_to_json(circuit),
        'initial_layout': initial_layout
    }


def grade_ex3(circuit: QuantumCircuit, initial_layout: List) -> None:
    try:
        submission = format_submission(circuit, initial_layout)
        ok, _ = grade_json(submission, 'ex3')
        if ok:
            print('Feel free to submit your answer.\r\n')
    except Exception as err:
        print(err)


def submit_ex3(circuit: QuantumCircuit, initial_layout: List) -> None:
    try:
        submission = format_submission(circuit, initial_layout)
        submit_json(submission, 'ex3')
    except Exception as err:
        print(err)
