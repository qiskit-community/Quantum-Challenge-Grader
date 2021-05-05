from typing import List
from qiskit import QuantumCircuit

from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json


criteria: dict = {}


def format_submission(
    qc_init: QuantumCircuit,
    qc_syn: QuantumCircuit,
    error_qubits: List[int],
    initial_layout: dict
) -> dict:
    return {
        'qc_init': circuit_to_json(qc_init),
        'qc_syn': circuit_to_json(qc_syn),
        'error_qubits': error_qubits,
        'initial_layout': initial_layout
    }


def grade_ex3(
    qc_init: QuantumCircuit,
    qc_syn: QuantumCircuit,
    error_qubits: List[int],
    initial_layout: dict
) -> None:
    try:
        submission = format_submission(
            qc_init,
            qc_syn,
            error_qubits,
            initial_layout
        )
        ok, _ = grade_json(submission, 'ex3')
        if ok:
            print('Feel free to submit your answer.\r\n')
    except Exception as err:
        print(err)


def submit_ex3(
    qc_init: QuantumCircuit,
    qc_syn: QuantumCircuit,
    error_qubits: List[int],
    initial_layout: dict
) -> None:
    try:
        submission = format_submission(
            qc_init,
            qc_syn,
            error_qubits,
            initial_layout
        )
        submit_json(submission, 'ex3')
    except Exception as err:
        print(err)
