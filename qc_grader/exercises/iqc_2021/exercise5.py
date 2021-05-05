from typing import List

from qiskit import QuantumCircuit
from qiskit.algorithms.minimum_eigen_solvers.vqe import VQEResult
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.exercises import SubmissionError
from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json, paulisumop_to_json, to_json


criteria: dict = {}


def format_submission(
    ansatz: QuantumCircuit,
    qubit_op: PauliSumOp,
    vqe_result: VQEResult
) -> dict:
    return {
        'ansatz': circuit_to_json(ansatz, byte_string=True),
        'qubit_op': paulisumop_to_json(qubit_op),
        'vqe_result': to_json(vqe_result, skip=['data', 'optimal_parameters'])
    }


def validate_inputs(
    ansatz: QuantumCircuit,
    qubit_op: PauliSumOp,
    vqe_result: VQEResult
) -> None:
    if not isinstance(ansatz, QuantumCircuit):
        raise SubmissionError('First positional argument should be of type QuantumCircuit')
    if not isinstance(qubit_op, PauliSumOp):
        raise SubmissionError('Second positional argument should be of type PauliSumOp')
    if not isinstance(vqe_result, VQEResult):
        raise SubmissionError('Third positional argument should be of type VQEResult')


def grade_ex5(
    ansatz: QuantumCircuit,
    qubit_op: PauliSumOp,
    vqe_result: VQEResult
) -> None:
    try:
        validate_inputs(ansatz, qubit_op, vqe_result)
        submission = format_submission(ansatz, qubit_op, vqe_result)
        ok, _ = grade_json(submission, 'ex5')
        if ok:
            print('Feel free to submit your answer.\r\n')
    except SubmissionError as se:
        print(f'\nOops 😕! {str(se)}')
        print('Please review your answer and try again.')
    except Exception as err:
        print(err)


def submit_ex5(
    ansatz: QuantumCircuit,
    qubit_op: PauliSumOp,
    vqe_result: VQEResult
) -> None:
    try:
        validate_inputs(ansatz, qubit_op, vqe_result)
        submission = format_submission(ansatz, qubit_op, vqe_result)
        submit_json(submission, 'ex5')
    except SubmissionError as se:
        print(f'\nOops 😕! {str(se)}')
        print('Please review your answer and try again.')
    except Exception as err:
        print(err)
