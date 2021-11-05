#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import json

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

from qiskit import QuantumCircuit, execute
from qiskit.providers import JobStatus
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.providers.ibmq.runtime import RuntimeJob
from qiskit.qobj import PulseQobj, QasmQobj
from qiskit.opflow import PauliSumOp
from qiskit.quantum_info import SparsePauliOp

from qiskit_nature.runtime import VQEProgram
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem

from .api import (
    get_server_endpoint,
    send_request,
    get_access_token,
    get_submission_endpoint,
    notify_provider,
    is_staging
)
from .exercises import get_question_id
from .util import (
    QObjEncoder,
    calc_depth,
    circuit_to_json,
    compute_cost,
    get_job,
    get_job_urls,
    get_provider,
    get_challenge_provider,
    qobj_to_json,
    uses_multiqubit_gate
)


def grade_and_submit(
    answer: Any,
    lab_id: str,
    ex_id: Optional[str] = None,
    is_job_id: Optional[bool] = False
) -> Tuple[bool, Optional[Any]]:
    connected = False  # 'qac-grading' in get_server_endpoint()

    if isinstance(answer, QuantumCircuit):
        grade_function = submit_circuit if connected else grade_circuit
    elif isinstance(answer, (complex, float, int)):
        grade_function = submit_number if connected else grade_number
    elif isinstance(answer, IBMQJob) or (isinstance(answer, str) and is_job_id):
        grade_function = submit_job if connected else grade_job
    else:
        grade_function = submit_json if connected else grade_json

    return grade_function(answer, lab_id, ex_id)


def _circuit_criteria(
    circuit: QuantumCircuit,
    max_qubits: Optional[int] = None,
    min_cost: Optional[int] = None,
    check_gates: Optional[bool] = False
) -> Tuple[Optional[int], Optional[int]]:
    if max_qubits is not None and circuit.num_qubits > max_qubits:
        print(f'Your circuit has {circuit.num_qubits} qubits, which exceeds the maximum allowed.')
        print(f'Please reduce the number of qubits in your circuit to below {max_qubits}.')
        return None, None

    try:
        if check_gates and not uses_multiqubit_gate(circuit):
            print('Your circuit appears to not use any multi-quibit gates.')
            print('Please review your circuit and try again.')
            return None, None

        cost = -1
        if min_cost is not None:
            cost = compute_cost(circuit)
            if cost < min_cost:
                print(f'Your circuit cost ({cost}) is too low. But if you are convinced that your circuit\n'
                    'is correct, please let us know in the `#ibm-quantum-challenge-2020` Slack channel.')
                return None, None

        return circuit.num_qubits, cost
    except Exception as err:
        print(f'Unable to compute cost: {err}')
        return None, None


def _circuit_grading(
    circuit: QuantumCircuit,
    lab_id: str,
    ex_id: Optional[str] = None,
    is_submit: Optional[bool] = False,
    max_qubits: Optional[int] = None,
    min_cost: Optional[int] = None,
    check_gates: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    payload = None
    server = None

    if not isinstance(circuit, QuantumCircuit):
        print(f'Expected a QuantumCircuit, but was given {type(circuit)}')
        print(f'Please provide a circuit as your answer.')
        return None, None

    if not is_submit:
        server = get_server_endpoint()
        if not server:
            print('Could not find a valid grading server or '
                  'the grading servers are down right now.')
            return None, None
    else:
        server = None

    question_id = get_question_id(lab_id, ex_id)
    if question_id < 0:
        print('Invalid or unsupported argument')
        return None, None

    _, cost = _circuit_criteria(
        circuit,
        max_qubits=max_qubits,
        min_cost=min_cost,
        check_gates=check_gates
    )
    if cost is not None:
        payload = {
            'answer': circuit_to_json(circuit)
        }

        payload['questionNumber' if is_submit else 'question_id'] = question_id

    return payload, server


def _qobj_grading(
    qobj: Union[PulseQobj, QasmQobj],
    lab_id: str,
    ex_id: Optional[str] = None,
    is_submit: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    payload = None
    server = None

    if not isinstance(qobj, (PulseQobj, QasmQobj)):
        print(f'Expected a Qobj, but was given {type(qobj)}')
        print(f'Please provide a Qobj as your answer.')
        return None, None

    if not is_submit:
        server = get_server_endpoint()
        if not server:
            print('Could not find a valid grading server or '
                  'the grading servers are down right now.')
            return None, None
    else:
        server = None

    question_id = get_question_id(lab_id, ex_id)
    if question_id < 0:
        print('Invalid or unsupported argument')
        return None, None

    payload = {
        'answer': qobj_to_json(qobj)
    }

    payload['questionNumber' if is_submit else 'question_id'] = question_id

    return payload, server


def _job_grading(
    job_or_id: Union[IBMQJob, str],
    lab_id: str,
    ex_id: Optional[str] = None,
    is_submit: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    if not isinstance(job_or_id, IBMQJob) and not isinstance(job_or_id, str):
        print(f'Expected an IBMQJob or a job ID, but was given {type(job_or_id)}')
        print(f'Please submit a job as your answer.')
        return None, None

    if not is_submit:
        server = get_server_endpoint()
        if not server:
            print('Could not find a valid grading server or the grading '
                  'servers are down right now.')
            return None, None
    else:
        server = None

    job = get_job(job_or_id) if isinstance(job_or_id, str) else job_or_id
    if not job:
        print('An invalid or non-existent job was specified.')
        return None, None

    job_status = job.status()
    if job_status in [JobStatus.CANCELLED, JobStatus.ERROR]:
        print(f'Job did not successfully complete: {job_status.value}.')
        return None, None
    elif job_status is not JobStatus.DONE:
        print(f'Job has not yet completed: {job_status.value}.')
        print(f'Please wait for the job (id: {job.job_id()}) to complete then try again.')
        return None, None
    
    question_id = get_question_id(lab_id, ex_id)
    if question_id < 0:
        print('Invalid or unsupported argument')
        return None, None

    header = job.result().header.to_dict()
    # if 'qc_cost' not in header:
    #     if is_submit:
    #         print('An unprepared answer was specified. '
    #               'Please prepare() and grade() answer before submitting.')
    #     else:
    #         print('An unprepared answer was specified. Please prepare() answer before grading.')
    #     return None, None

    download_url, result_url = get_job_urls(job)
    if not download_url or not result_url:
        print('Unable to obtain job URLs')
        return None, None

    payload = {
        'answer': json.dumps({
            'download_url': download_url,
            'result_url': result_url
        })
    }

    payload['questionNumber' if is_submit else 'question_id'] = question_id

    return payload, server


def _number_grading(
    answer: Union[int, float, complex],
    lab_id: str,
    ex_id: Optional[str] = None,
    is_submit: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    if not isinstance(answer, (int, float, complex)):
        print(f'Expected a number, but was given {type(answer)}')
        print(f'Please provide a number as your answer.')
        return None, None

    if not is_submit:
        server = get_server_endpoint()
        if not server:
            print('Could not find a valid grading server '
                  'or the grading servers are down right now.')
            return None, None
    else:
        server = None


    question_id = get_question_id(lab_id, ex_id)
    if question_id < 0:
        print('Invalid or unsupported argument')
        return None, None

    payload = {
        'answer': str(answer)
    }

    payload['questionNumber' if is_submit else 'question_id'] = question_id

    return payload, server


def _json_grading(
    answer: Any,
    lab_id: str,
    ex_id: Optional[str] = None,
    is_submit: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    if not is_submit:
        server = get_server_endpoint()
        if not server:
            print('Could not find a valid grading server '
                  'or the grading servers are down right now.')
            return None, None
    else:
        server = None


    question_id = get_question_id(lab_id, ex_id)
    if question_id < 0:
        print(f'Invalid or unsupported lab/exercise ({lab_id}/{ex_id}) ID: {question_id}')
        return None, None

    payload = {
        'answer': json.dumps(answer, skipkeys=True, cls=QObjEncoder)
    }

    payload['questionNumber' if is_submit else 'question_id'] = question_id

    return payload, server


def prepare_circuit(
    circuit: QuantumCircuit,
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None,
    check_gates: Optional[bool] = False,
    **kwargs
) -> Optional[IBMQJob]:
    job = None

    if not isinstance(circuit, QuantumCircuit):
        print(f'Expected a QuantumCircuit, but was given {type(circuit)}')
        print(f'Please provide a circuit.')
        return None

    _, cost = _circuit_criteria(
        circuit,
        max_qubits=max_qubits,
        min_cost=min_cost,
        check_gates=check_gates
    )

    if 'backend' not in kwargs:
        kwargs['backend'] = get_provider().get_backend('ibmq_qasm_simulator')

    if 'qobj_header' not in kwargs:
        kwargs['qobj_header'] = {}

    if cost is not None:
        kwargs['qobj_header']['qc_cost'] = cost

    # execute experiments
    print('Starting experiment. Please wait...')
    job = execute(
        circuit,
        **kwargs
    )

    print(f'You may monitor the job (id: {job.job_id()}) status '
          'and proceed to grading when it successfully completes.')

    return job


def prepare_solver(
    solver_func: Callable,
    lab_id: str,
    ex_id: Optional[str] = None,
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None,
    check_gates: Optional[bool] = False,
    num_experiments: Optional[int] = 4,
    params_order: Optional[List[str]] = None,
    test_problem_set: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Optional[IBMQJob]:
    job = None
    circuits = []
    indices = []

    if not callable(solver_func):
        print(f'Expected a function, but was given {type(solver_func)}')
        print(f'Please provide a function that returns a QuantumCircuit.')
        return None

    server = get_server_endpoint()
    if not server:
        print('Could not find a valid grading server or the grading servers are down right now.')
        return None

    endpoint = server + 'problem-set'

    count = 0
    _, problem_sets = get_problem_set(lab_id, ex_id, endpoint)
    for problem_set in problem_sets:
        index = problem_set['index']
        inputs = problem_set['value']

        if inputs and index is not None and index >= 0:
            count += 1
            print(f'Running "{solver_func.__name__}" ({count}/{len(problem_sets)})... ')
            if not params_order:
                qc = solver_func(*inputs)
            else:
                ins = [inputs[x] for x in params_order]
                qc = solver_func(*ins)

            if qc.num_qubits > max_qubits:
                print(
                    f'Your circuit has {qc.num_qubits} qubits, '
                    'which exceeds the maximum allowed.\n'
                    f'Please reduce the number of qubits in your circuit to below {max_qubits}.'
                )
                return None

            indices.append(index)
            if count < 5:
                d, n = calc_depth(qc)

            qc.metadata = {
                'qc_index': index,
                'qc_depth': json.dumps([d, n]) if count < 5 else ''
            }
            circuits.append(qc)
        else:
            print('Failed to obtain a valid problem set')
            return None

        # _, cost = _circuit_criteria(
        #     qc[n],
        #     max_qubits=max_qubits,
        #     min_cost=min_cost,
        #     check_gates=check_gates
        # )
        # costs.append(cost)

    if 'backend' not in kwargs:
        kwargs['backend'] = get_provider().get_backend('ibmq_qasm_simulator')

    # execute experiments
    print('Starting experiments. Please wait...')
    job = execute(
            circuits,
            **kwargs
        )

    print(f'You may monitor the job (id: {job.job_id()}) status '
          'and proceed to grading when it successfully completes.')

    return job


# for prepare_vqe_runtime_program
# adapted from VQEProgram in Qiskit Nature
# https://github.com/Qiskit/qiskit-nature/blob/0.2.2/qiskit_nature/runtime/vqe_program.py
def _convert_to_paulisumop(operator):
    """Attempt to convert the operator to a PauliSumOp."""
    if isinstance(operator, PauliSumOp):
        return operator

    try:
        primitive = SparsePauliOp(operator.primitive)
        return PauliSumOp(primitive, operator.coeff)
    except Exception as exc:
        raise ValueError(
            f"Invalid type of the operator {type(operator)} "
            "must be PauliSumOp, or castable to one."
        ) from exc


def _wrap_vqe_callback(runtime_vqe) -> Optional[Callable]:
    """Wraps and returns the given callback to match the signature of the runtime callback."""

    def wrapped_callback(*args):
        _, data = args  # first element is the job id
        iteration_count = data[0]
        params = data[1]
        mean = data[2]
        sigma = data[3]
        return runtime_vqe.callback(iteration_count, params, mean, sigma)

    # if callback is set, return wrapped callback, else return None
    if runtime_vqe.callback:
        return wrapped_callback
    else:
        return None


def prepare_vqe_runtime_program(
    runtime_vqe: VQEProgram,
    qubit_converter: QubitConverter,
    problem: ElectronicStructureProblem,
    real_device: bool,
    **kwargs
) -> Optional[RuntimeJob]:
    # overwriting provider and backend if they are not challenge provider and simulator
    challenge_provider = get_challenge_provider()
    if challenge_provider:
        ibmq_qasm_simulator = challenge_provider.get_backend('ibmq_qasm_simulator')
        ibm_perth = challenge_provider.get_backend('ibm_perth')
    else:
        return None

    # check provider is challenge provider, overwrite if otherwise
    if runtime_vqe.provider != challenge_provider:
        print('You are not using the challenge provider. Overwriting provider...')
        runtime_vqe.provider = challenge_provider

    # 
    if real_device:
        if runtime_vqe.backend != ibm_perth:
            print('You are not using the ibm_perth backend, even though you set "real_device=True".\n'+\
                  'Please change your backend setting.')
            return None
    elif runtime_vqe.backend != ibmq_qasm_simulator:
        print('You are not using the ibmq_qasm_simulator backend. Overwriting backend...')
        runtime_vqe.backend = ibmq_qasm_simulator

    # execute experiments
    print('Starting experiment. Please wait...')
    second_q_ops = problem.second_q_ops()

    operator = qubit_converter.convert(
        second_q_ops[0],
        num_particles=problem.num_particles,
        sector_locator=problem.symmetry_sector_locator,
    )
    aux_operators = qubit_converter.convert_match(second_q_ops[1:])

    # try to convert the operators to a PauliSumOp, if it isn't already one
    operator = _convert_to_paulisumop(operator)
    if aux_operators is not None:
        aux_operators = [_convert_to_paulisumop(aux_op) for aux_op in aux_operators]

    # combine the settings with the given operator to runtime inputs
    inputs = {
        "operator": operator,
        "aux_operators": aux_operators,
        "ansatz": runtime_vqe.ansatz,
        "optimizer": runtime_vqe.optimizer,
        "initial_point": runtime_vqe.initial_point,
        "shots": runtime_vqe.shots,
        "measurement_error_mitigation": runtime_vqe.measurement_error_mitigation,
        "store_intermediate": runtime_vqe.store_intermediate,
    }

    # define runtime options
    options = {"backend_name": runtime_vqe.backend.name()}

    # send job to runtime and return result
    job = runtime_vqe.provider.runtime.run(
        program_id='vqe',
        inputs=inputs,
        options=options,
        callback=_wrap_vqe_callback(runtime_vqe),
    )

    print(f'You may monitor the job (id: {job.job_id()}) status '
          'and proceed to grading when it successfully completes.')

    return job


def run_using_problem_set(
    solver_func: Callable,
    lab_id: str,
    ex_id: Optional[str] = None,
    num_experiments: Optional[int] = 3,
    params_order: Optional[List[str]] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    if not callable(solver_func):
        print(f'Expected a function, but was given {type(solver_func)}')
        return None

    server = get_server_endpoint()
    if not server:
        print('Could not find a valid grading server or the grading servers are down right now.')
        return None

    endpoint = server + 'problem-set'

    count = 0
    indices = []
    result_dicts = []
    while count < num_experiments:
        index, inputs = get_problem_set(lab_id, ex_id, endpoint)
        if index not in indices:
            if inputs and index is not None and index >= 0:
                count += 1
                print(f'Running "{solver_func.__name__}" ({count}/{num_experiments})... ')
                if not params_order:
                    function_results = solver_func(*inputs)
                else:
                    ins = [inputs[x] for x in params_order]
                    function_results = solver_func(*ins)

                indices.append(index)
                result_dict = {
                    'index': index,
                    'problem-set': inputs,
                    'result': function_results
                }
                result_dicts.append(result_dict)
            else:
                print('Failed to obtain a valid problem set')
                return None

    return result_dicts


def grade_circuit(
    circuit: QuantumCircuit,
    lab_id: str,
    ex_id: Optional[str] = None,
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None
) -> Tuple[bool, Optional[Any]]:
    payload, server = _circuit_grading(
        circuit,
        lab_id,
        ex_id,
        is_submit=False,
        max_qubits=max_qubits,
        min_cost=min_cost
    )
    if payload:
        print(f'Grading your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False, None


def grade_qobj(
    qobj: Union[PulseQobj, QasmQobj],
    lab_id: str,
    ex_id: Optional[str] = None
) -> Tuple[bool, Optional[Any]]:
    payload, server = _qobj_grading(
        qobj,
        lab_id,
        ex_id,
        is_submit=False,
    )
    if payload:
        print(f'Grading your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False, None


def grade_job(
    job_or_id: Union[IBMQJob, str],
    lab_id: str,
    ex_id: Optional[str] = None
) -> Tuple[bool, Optional[Any]]:
    payload, server = _job_grading(job_or_id, lab_id, ex_id, is_submit=False)
    if payload:
        print(f'Grading your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False, None


def grade_number(
    answer: Union[int, float, complex],
    lab_id: str,
    ex_id: Optional[str] = None
) -> Tuple[bool, Optional[Any]]:
    payload, server = _number_grading(answer, lab_id, ex_id, is_submit=False)
    if payload:
        print(f'Grading your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False, None


def grade_json(
    answer: Any,
    lab_id: str,
    ex_id: Optional[str] = None,
    max_content_length: Optional[int] = None
) -> Tuple[bool, Optional[Any]]:
    payload, server = _json_grading(answer, lab_id, ex_id, is_submit=False)
    if payload:
        print(f'Grading your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer',
            max_content_length=max_content_length
        )
    return False, None


def submit_circuit(
    circuit: QuantumCircuit,
    lab_id: str,
    ex_id: Optional[str] = None,
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None
) -> bool:
    payload, _ = _circuit_grading(
        circuit,
        lab_id,
        ex_id,
        is_submit=True,
        max_qubits=max_qubits,
        min_cost=min_cost
    )
    if payload:
        print(f'Submitting your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return submit_answer(payload)
    return False


def submit_qobj(
    qobj: Union[PulseQobj, QasmQobj],
    lab_id: str,
    ex_id: Optional[str] = None
) -> bool:
    payload, _ = _qobj_grading(
        qobj,
        lab_id,
        ex_id,
        is_submit=True
    )
    if payload:
        print(f'Submitting your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return submit_answer(payload)
    return False


def submit_job(
    job_or_id: IBMQJob,
    lab_id: str,
    ex_id: Optional[str] = None
) -> bool:
    payload, _ = _job_grading(job_or_id, lab_id, ex_id, is_submit=True)
    if payload:
        print(f'Submitting your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return submit_answer(payload)
    return False


def submit_number(
    answer: Union[int, float, complex],
    lab_id: str,
    ex_id: Optional[str] = None
) -> bool:
    payload, _ = _number_grading(answer, lab_id, ex_id, is_submit=True)
    if payload:
        print(f'Submitting your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return submit_answer(payload)
    return False


def submit_json(
    answer: Any,
    lab_id: str,
    ex_id: Optional[str] = None,
    max_content_length: Optional[int] = None
) -> bool:
    payload, _ = _json_grading(answer, lab_id, ex_id, is_submit=True)
    if payload:
        print(f'Submitting your answer for {lab_id}{"/"+ex_id if ex_id else ""}. Please wait...')
        return submit_answer(payload, max_content_length=max_content_length)
    return False


def get_problem_set(
    lab_id: str, ex_id: Optional[str], endpoint: str
) -> Union[List[Dict[str, Any]], Tuple[int, Any]]:
    problem_set_response = None

    question_id = get_question_id(lab_id, ex_id)
    if question_id < 0:
        print('Invalid or unsupported argument')
        return None, None

    try:
        payload = {'question_id': question_id}
        problem_set_response = send_request(endpoint, query=payload, method='GET')
    except Exception as err:
        print('Unable to obtain the problem set')

    if problem_set_response:
        status = problem_set_response.get('status')
        if status == 'valid':
            try:
                index = problem_set_response.get('index')
                value = json.loads(problem_set_response.get('value'))
                return index, value
            except Exception as err:
                print(f'Problem set could not be processed: {err}')
        else:
            cause = problem_set_response.get('cause')
            print(f'Problem set failed: {cause}')

    return None, None


def grade_answer(
    payload: dict, endpoint: str, cost: Optional[int] = None, max_content_length: Optional[int] = None
) -> Tuple[bool, Optional[Any]]:
    try:
        answer_response = send_request(
            endpoint, body=payload, max_content_length=max_content_length
        )
        status = answer_response.get('status', None)
        cause = answer_response.get('cause', None)
        score = cost if cost else answer_response.get('score', None)

        handle_grade_response(status, score=score, cause=cause)
        s = status == 'valid' or status is True
        return s, score
    except Exception as err:
        print(f'Failed: {err}')
        return False, None


def submit_answer(payload: dict, max_content_length: Optional[int] = None) -> bool:
    try:
        access_token = get_access_token()

        baseurl = get_submission_endpoint()
        endpoint = urljoin(baseurl, './challenges/answers')

        submit_response = send_request(
            endpoint,
            body=payload,
            query={'access_token': access_token},
            max_content_length=max_content_length
        )

        status = submit_response.get('status', None)
        if status is None:
            status = submit_response.get('valid', None)
        cause = submit_response.get('cause', None)
        score = submit_response.get('score', None)

        success = status == 'valid' or status is True
        if success:
            notify_provider(access_token)

        handle_submit_response(status, cause=cause, score=score)
        return success
    except Exception as err:
        print(f'Failed: {err}')
        return False


def handle_grade_response(
    status: Optional[str], score: Optional[int] = None, cause: Optional[str] = None
) -> None:
    if status == 'valid':
        print('\nCongratulations 🎉! Your answer is correct.')
        if score is not None:
            print(f'Your score is {score}.')
    elif status == 'invalid':
        print(f'\nOops 😕! {cause}')
        print('Please review your answer and try again.')
    elif status == 'notFinished':
        print(f'Job has not finished: {cause}')
        print(f'Please wait for the job to complete then try again.')
    else:
        print(f'Failed: {cause}')
        print('Unable to grade your answer.')


def handle_submit_response(
    status: Union[str, bool], cause: Optional[str] = None, score: Optional[int] = None
) -> None:
    if status == 'valid' or status is True:
        print('Congratulations 🎉! Your answer is correct and has been submitted.')
        if score is not None:
            print(f'Your score is {score}.')
    elif status == 'invalid' or status is False:
        print(f'Oops 😕! {"Your answer is incorrect" if cause is None else cause}')
        # print('Make sure your answer is correct and successfully graded before submitting.')
        print('Please review your answer and try again.')
    elif status == 'notFinished':
        print(f'Job has not finished: {cause}')
        print(f'Please wait for the job to complete, grade it, and then try to submit again.')
    else:
        print(f'Failed: {cause}')
        print('Unable to submit your answer at this time.')
