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
from qiskit.qobj import PulseQobj, QasmQobj

from .api import get_server_endpoint, send_request, get_access_token, get_submission_endpoint, notify_provider
from .exercises import get_question_id
from .util import (
    QObjEncoder,
    circuit_to_json,
    compute_cost,
    get_job,
    get_job_urls,
    get_provider,
    qobj_to_json,
    uses_multiqubit_gate
)


def grade_and_submit(
    answer: Any,
    lab_id: str,
    ex_id: Optional[str] = None,
    is_job_id: Optional[bool] = False
) -> Tuple[bool, Optional[Any]]:
    connected = 'qac-grading' in get_server_endpoint()

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
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None,
    check_gates: Optional[bool] = False,
    **kwargs
) -> Optional[IBMQJob]:
    job = None
    params_order=['L1', 'L2', 'C1', 'C2', 'C_max']
    num_circuits = 5
    qc = []
    indices = []
    costs = []

    if not callable(solver_func):
        print(f'Expected a function, but was given {type(solver_func)}')
        print(f'Please provide a function that returns a QuantumCircuit.')
        return None

    server = get_server_endpoint()
    if not server:
        print('Could not find a valid grading server or the grading servers are down right now.')
        return None

    endpoint = server + 'problem-set'

    for n in range(num_circuits):
        index, inputs = get_problem_set(lab_id, endpoint)
        indices.append(index)

        if inputs and index is not None and index >= 0:
            print(f'Running {solver_func.__name__}... problem set #{index}')
            if not params_order:
                qc.append(solver_func(*inputs))
            else:
                ins = [inputs[x] for x in params_order]
                qc.append(solver_func(*ins))
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
            qc, 
            qobj_header={
            'qc_index': indices
            # 'qc_cost': costs
        },
        **kwargs
    )

    print(f'You may monitor the job (id: {job.job_id()}) status '
          'and proceed to grading when it successfully completes.')

    return job


def run_using_problem_set(
    solver_func: Callable,
    lab_id: str,
    ex_id: Optional[str] = None,
    params_order: Optional[List[str]] = None,
    execute_result: bool = False,
    **kwargs
) -> Optional[Union[Dict[str, Any], IBMQJob]]:
    if not callable(solver_func):
        print(f'Expected a function, but was given {type(solver_func)}')
        return None

    server = get_server_endpoint()
    if not server:
        print('Could not find a valid grading server or the grading servers are down right now.')
        return None

    endpoint = server + 'problem-set'
    index, inputs = get_problem_set(lab_id, endpoint)

    if inputs and index is not None and index >= 0:
        print(f'Running {solver_func.__name__}...', index, len(inputs))
        if not params_order:
            function_result = solver_func(*inputs)
        else:
            ins = [inputs[x] for x in params_order]
            function_results = solver_func(*ins)
        return {
            'index': index,
            'problem-set': inputs,
            'result': function_results
        }
    else:
        print('Failed to obtain a valid problem set')
        return None


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
) -> Tuple[Optional[int], Optional[Any]]:
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
        # if success:
        #     notify_provider(access_token)

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
