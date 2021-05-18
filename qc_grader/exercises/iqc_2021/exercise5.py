from typing import Optional

from qiskit import QuantumCircuit
from qiskit.algorithms.minimum_eigen_solvers.vqe import VQEResult
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.api import MaxContentError
from qc_grader.exercises import SubmissionError
from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json, paulisumop_to_json, to_json


criteria: dict = {
    'max_content_length': 2 * 1024 * 1024  # 2mb
}


def format_submission(
    ansatz: QuantumCircuit,
    qubit_op: PauliSumOp,
    vqe_result: VQEResult,
    freeze_core: bool
) -> dict:
    return {
        'ansatz': circuit_to_json(ansatz, byte_string=True),
        'qubit_op': paulisumop_to_json(qubit_op),
        'vqe_result': to_json(vqe_result, skip=['data', 'optimal_parameters']),
        'freeze_core': freeze_core
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
    vqe_result: VQEResult,
    freeze_core: Optional[bool] = False
) -> None:
    try:
        validate_inputs(ansatz, qubit_op, vqe_result)
        submission = format_submission(ansatz, qubit_op, vqe_result, freeze_core)
        ok, _ = grade_json(submission, 'ex5', **criteria)
        if ok:
            print('Feel free to submit your answer.\r\n')
    except MaxContentError as mce:
        print(f'\nOops 😕! Your solution is larger than expected.')
        print('Please review your answer and see if you can improve it by'
              ' decreasing the number of parameters or making the circuit smaller.')
    except SubmissionError as se:
        print(f'\nOops 😕! {str(se)}')
        print('Please review your answer and try again.')
    except Exception as err:
        print(err)


def submit_ex5(
    ansatz: QuantumCircuit,
    qubit_op: PauliSumOp,
    vqe_result: VQEResult,
    freeze_core: Optional[bool] = False
) -> None:
    try:
        validate_inputs(ansatz, qubit_op, vqe_result)
        submission = format_submission(ansatz, qubit_op, vqe_result, freeze_core)
        submit_json(submission, 'ex5', **criteria)
    except MaxContentError as mce:
        print(f'\nOops 😕! Your solution is larger than expected.')
        print('Please review your answer and see if you can improve it by'
              ' decreasing the number of parameters or making the circuit smaller.')
    except SubmissionError as se:
        print(f'\nOops 😕! {str(se)}')
        print('Please review your answer and try again.')
    except Exception as err:
        print(err)
