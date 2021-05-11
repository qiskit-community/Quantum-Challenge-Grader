from typing import List
from qiskit import QuantumCircuit

from .. import SubmissionError
from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json


criteria: dict = {}


def verify_parameters(
    qc_init: QuantumCircuit,
    qc_syn: QuantumCircuit,
    error_qubits: List[int],
    initial_layout: List[int]
):
    if not isinstance(qc_init, QuantumCircuit):
        raise SubmissionError("The 'qc_init' parameter must be of type QuantumCircuit")
    if not isinstance(qc_syn, QuantumCircuit):
        raise SubmissionError("The 'qc_syn' parameter must be of type QuantumCircuit")
    if not isinstance(error_qubits, list) or len(error_qubits) == 0 or any(not isinstance(x, int) for x in error_qubits):
        raise SubmissionError("The 'error_qubits' parameter must be a list of integers that map to qubit index values.")
    if not isinstance(initial_layout, list) or len(initial_layout) == 0  or any(not isinstance(x, int) for x in initial_layout):
        raise SubmissionError("The 'initial_layout' parameter must be a list of integers that map to qubit index values.")

def format_submission(
    qc_init: QuantumCircuit,
    qc_syn: QuantumCircuit,
    error_qubits: List[int],
    initial_layout: List[int]
) -> dict:
    verify_parameters(
        qc_init,
        qc_syn,
        error_qubits,
        initial_layout
    )
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
    initial_layout: List[int]
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
    except SubmissionError as err:
        print(err)
    except Exception as err:
        print(err)


def submit_ex3(
    qc_init: QuantumCircuit,
    qc_syn: QuantumCircuit,
    error_qubits: List[int],
    initial_layout: List[int]
) -> None:
    try:
        submission = format_submission(
            qc_init,
            qc_syn,
            error_qubits,
            initial_layout
        )
        submit_json(submission, 'ex3')
    except SubmissionError as err:
        print(err)
    except Exception as err:
        print(err)
