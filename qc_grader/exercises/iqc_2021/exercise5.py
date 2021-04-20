from typing import List
from qiskit import QuantumCircuit

from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json


criteria: dict = {}


def format_submission(circuit: QuantumCircuit, parameters: dict) -> dict:
    return {
        'qc': circuit_to_json(circuit),
        'parameters': parameters
    }


def grade_ex5(circuit: QuantumCircuit, parameters: dict) -> None:
    try:
        submission = format_submission(circuit, parameters)
        ok, _ = grade_json(submission, 'ex5')
        if ok:
            print('Feel free to submit your answer.\r\n')
    except Exception as err:
        print(err)


def submit_ex5(circuit: QuantumCircuit, parameters: dict) -> None:
    try:
        submission = format_submission(circuit, parameters)
        submit_json(submission, 'ex5')
    except Exception as err:
        print(err)
