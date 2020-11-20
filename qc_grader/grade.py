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

from typing import Any, Callable, Optional, Tuple, Union
from urllib.parse import urljoin

from qiskit import QuantumCircuit, execute
from qiskit.providers import JobStatus
from qiskit.providers.ibmq.job import IBMQJob

from .api import get_server_endpoint, send_request, get_access_token, get_submission_endpoint
from .exercises import get_question_id
from .util import compute_cost, get_provider, get_job, circuit_to_json, get_job_urls, uses_multiqubit_gate


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

        cost = compute_cost(circuit)
        if min_cost is not None and cost < min_cost:
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
    ex_id: str,
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
        server = get_server_endpoint(lab_id, ex_id)
        if not server:
            print('Could not find a valid grading server or '
                  'the grading servers are down right now.')
            return None, None
    else:
        server = None

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

        if is_submit:
            payload['questionNumber'] = get_question_id(lab_id, ex_id)
        else:
            payload['question_id'] = get_question_id(lab_id, ex_id)

    return payload, server


def _job_grading(
    job_or_id: Union[IBMQJob, str],
    lab_id: str,
    ex_id: str,
    is_submit: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    if not isinstance(job_or_id, IBMQJob) and not isinstance(job_or_id, str):
        print(f'Expected an IBMQJob or a job ID, but was given {type(job_or_id)}')
        print(f'Please submit a job as your answer.')
        return None, None

    if not is_submit:
        server = get_server_endpoint(lab_id, ex_id)
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

    header = job.result().header.to_dict()
    if 'qc_cost' not in header:
        if is_submit:
            print('An unprepared answer was specified. '
                  'Please prepare() and grade() answer before submitting.')
        else:
            print('An unprepared answer was specified. Please prepare() answer before grading.')
        return None, None

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

    if is_submit:
        payload['questionNumber'] = get_question_id(lab_id, ex_id)
    else:
        payload['question_id'] = get_question_id(lab_id, ex_id)

    return payload, server


def _number_grading(
    answer: int,
    lab_id: str,
    ex_id: str,
    is_submit: Optional[bool] = False
) -> Tuple[Optional[dict], Optional[str]]:
    if not isinstance(answer, int):
        print(f'Expected a integer, but was given {type(answer)}')
        print(f'Please provide a number as your answer.')
        return None, None

    if not is_submit:
        server = get_server_endpoint(lab_id, ex_id)
        if not server:
            print('Could not find a valid grading server '
                  'or the grading servers are down right now.')
            return None, None
    else:
        server = None

    payload = {
        'answer': str(answer)
    }

    if is_submit:
        payload['questionNumber'] = get_question_id(lab_id, ex_id)
    else:
        payload['question_id'] = get_question_id(lab_id, ex_id)

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
    if cost is not None:
        if 'backend' not in kwargs:
            kwargs['backend'] = get_provider().get_backend('ibmq_qasm_simulator')

        # execute experiments
        print('Starting experiment. Please wait...')
        job = execute(
            circuit,
            qobj_header={
                'qc_cost': cost
            },
            **kwargs
        )

        print(f'You may monitor the job (id: {job.job_id()}) status '
            'and proceed to grading when it successfully completes.')
        
    return job


def prepare_solver(
    solver_func: Callable,
    lab_id: str,
    ex_id: str,
    problem_set: Optional[Any] = None,
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None,
    check_gates: Optional[bool] = False,
    **kwargs
) -> Optional[IBMQJob]:
    job = None

    if not callable(solver_func):
        print(f'Expected a function, but was given {type(solver_func)}')
        print(f'Please provide a function that returns a QuantumCircuit.')
        return None

    server = get_server_endpoint(lab_id, ex_id)
    if not server:
        print('Could not find a valid grading server or the grading servers are down right now.')
        return

    endpoint = server + 'problem-set'
    index, value = get_problem_set(lab_id, ex_id, endpoint)

    print(f'Running {solver_func.__name__}...')
    qc_1 = solver_func(problem_set)

    _, cost = _circuit_criteria(
        qc_1,
        max_qubits=max_qubits,
        min_cost=min_cost,
        check_gates=check_gates
    )

    if value and index is not None and index >= 0 and cost is not None:
        qc_2 = solver_func(value)

        if 'backend' not in kwargs:
            kwargs['backend'] = get_provider().get_backend('ibmq_qasm_simulator')

        # execute experiments
        print('Starting experiments. Please wait...')
        job = execute(
            [qc_1, qc_2],
            qobj_header={
                'qc_index': [None, index],
                'qc_cost': cost
            },
            **kwargs
        )

        print(f'You may monitor the job (id: {job.job_id()}) status '
              'and proceed to grading when it successfully completes.')

    return job


def grade_circuit(
    circuit: QuantumCircuit,
    lab_id: str,
    ex_id: str,
    max_qubits: Optional[int] = 28,
    min_cost: Optional[int] = None
) -> bool:
    payload, server = _circuit_grading(
        circuit,
        lab_id,
        ex_id,
        is_submit=False,
        max_qubits=max_qubits,
        min_cost=min_cost
    )
    if payload:
        print('Grading your answer. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False


def grade_job(
    job_or_id: Union[IBMQJob, str],
    lab_id: str,
    ex_id: str
) -> bool:
    payload, server = _job_grading(job_or_id, lab_id, ex_id, is_submit=False)
    if payload:
        print('Grading your answer. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False


def grade_number(
    answer: int,
    lab_id: str,
    ex_id: str
) -> bool:
    payload, server = _number_grading(answer, lab_id, ex_id, is_submit=False)
    if payload:
        print('Grading your answer. Please wait...')
        return grade_answer(
            payload,
            server + 'validate-answer'
        )
    return False


def submit_circuit(
    circuit: QuantumCircuit,
    lab_id: str,
    ex_id: str,
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
        print('Submitting your answer. Please wait...')
        return submit_answer(payload)
    return False


def submit_job(
    job_or_id: IBMQJob,
    lab_id: str,
    ex_id: str,
) -> bool:
    payload, _ = _job_grading(job_or_id, lab_id, ex_id, is_submit=True)
    if payload:
        print('Submitting your answer. Please wait...')
        return submit_answer(payload)
    return False


def submit_number(
    answer: int,
    lab_id: str,
    ex_id: str
) -> bool:
    payload, _ = _number_grading(answer, lab_id, ex_id, is_submit=True)
    if payload:
        print('Submitting your answer. Please wait...')
        return submit_answer(payload)
    return False


def get_problem_set(
    lab_id: str, ex_id: str, endpoint: str
) -> Tuple[Optional[int], Optional[Any]]:
    problem_set_response = None

    try:
        payload = {'question_id': get_question_id(lab_id, ex_id)}
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


def grade_answer(payload: dict, endpoint: str, cost: Optional[int] = None) -> bool:
    try:
        answer_response = send_request(endpoint, body=payload)

        status = answer_response.get('status', None)
        cause = answer_response.get('cause', None)
        score = cost if cost else answer_response.get('score', None)

        handle_grade_response(status, score=score, cause=cause)
        return status == 'valid' or status is True
    except Exception as err:
        print(f'Failed: {err}')
        return False


def submit_answer(payload: dict) -> bool:
    try:
        access_token = get_access_token()

        baseurl = get_submission_endpoint()
        endpoint = urljoin(baseurl, './challenges/answers')

        submit_response = send_request(
            endpoint,
            body=payload,
            query={'access_token': access_token}
        )

        status = submit_response.get('status', None)
        if status is None:
            status = submit_response.get('valid', None)
        cause = submit_response.get('cause', None)

        handle_submit_response(status, cause=cause)
        return status == 'valid' or status is True
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
    status: Union[str, bool], cause: Optional[str] = None
) -> None:
    if status == 'valid' or status is True:
        print('\nSuccess 🎉! Your answer has been submitted.')
    elif status == 'invalid' or status is False:
        print(f'\nOops 😕! {"Your answer is incorrect" if cause is None else cause}')
        print('Make sure your answer is correct and successfully graded before submitting.')
    elif status == 'notFinished':
        print(f'Job has not finished: {cause}')
        print(f'Please wait for the job to complete, grade it, and then try to submit again.')
    else:
        print(f'Failed: {cause}')
        print('Unable to submit your answer at this time.')
