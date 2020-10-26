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

import os

from typing import Callable, Optional, Union

from qiskit import IBMQ, execute, QuantumCircuit
from qiskit.providers import JobStatus
from qiskit.providers.ibmq.job import IBMQJob

from .api import get_server_endpoint, send_request
from .util import get_provider, get_job_status, circuit_to_json


def prepare_grading_job(
    solver_func: Callable,
    lab_id: str,
    ex_id: str,
    server_url: Optional[str] = None
) -> IBMQJob:
    if not callable(solver_func):
        print('🚫 Please provide a callable function that returns a qiskit.QuantumCircuit'
              ' that solves the problem set.')
    else:
        server = server_url if server_url else get_server_endpoint(lab_id, ex_id)
        if not server:
            print('🚫 Failed to find a valid grading server or the grading servers are down right now.')
            return

        # TODO get problem set
        problem_set_1 = None
        qc_1 = solver_func(problem_set_1)

        endpoint = _normalize_final_slash(server) + 'problem-set'
        index, value = get_problem_set(lab_id, ex_id, endpoint)
        if index and value:
            qc_2 = solver_func(value)

            backend = get_provider().get_backend('ibmq_qasm_simulator')

            # execute experiments
            print('Running...')
            job = execute(
                [qc_1, qc_2],
                backend=backend,
                shots=1000,
                qobj_header={
                    'qc_index': index
                }
            )

            print(f'Monitor job (id: {job.job_id()}) status, and grade when it is done.')
            return job


def grade(
    answer: Union[str, int, IBMQJob, QuantumCircuit],
    lab_id: str,
    ex_id: str,
    server_url: Optional[str] = None
) -> None:
    server = server_url if server_url else get_server_endpoint(lab_id, ex_id)
    if not server:
        print('🚫 Failed to find a valid grading server or the grading servers are down right now.')
        return

    payload = make_payload(answer, lab_id, ex_id)

    if payload:
        print('Grading...')

        result = check_answer(
            payload,
            _normalize_final_slash(server) + 'validate-answer'
        )

        print(result)


def submit(
    answer: Union[str, int, IBMQJob, QuantumCircuit],
    lab_id: str,
    ex_id: str,
    server_url: Optional[str] = None
) -> None:
    server = server_url if server_url else get_server_endpoint(lab_id, ex_id)
    if not server:
        print('🚫 Failed to find a valid grading server or the grading servers are down right now.')
        return

    payload = make_payload(answer, lab_id, ex_id)

    if payload:
        print('Submitting...')
        result = check_answer(
            payload,
            _normalize_final_slash(server) + 'submit-answer'
        )

        print(result)


def make_payload(
    answer: Union[str, int, IBMQJob, QuantumCircuit],
    lab_id: str,
    ex_id: str
) -> Optional[dict]:
    if not lab_id:
        print('🚫 In which lab are you?.')
        return {}
    if not ex_id:
        print('🚫 In which exercise are you?.')
        return {}

    payload = {
        'iqx_token': os.getenv('QXToken'),
        'question_id': f'{lab_id}/{ex_id}'
    }

    if isinstance(answer, IBMQJob):
        job_id, status = get_job_status(answer)
        if status is JobStatus.DONE:
            payload['answer'] = job_id
        elif status is None:
            print('🚫 Invalid or non-existent job specified.')
            return {}
        else:
            print(f'🚫 Job has not yet completed or was not successful (status: {status}).')
            print(f'Monitor job (id: {job_id}) and try again.')
            return {}
    elif isinstance(answer, QuantumCircuit):
        payload['answer'] = circuit_to_json(answer)
    elif isinstance(answer, int):
        payload['answer'] = str(answer)
    else:
        print(f'🚫 Unsupported answer type ({type(answer)})')
        return {}

    return payload


def check_answer(payload: dict, endpoint: str) -> str:
    try:
        answer_response = send_request(payload, endpoint)

        if answer_response.get('is_valid'):
            result_msg = '🎉 Correct'
            score = answer_response.get('score')
            result_msg += f'\nYour score is {score}.' if score is not None else ''
        else:
            cause = answer_response.get('cause')
            result_msg = f'❌ Failed: {cause}'

        return f'{payload["question_id"]} - {result_msg}'
    except Exception as err:
        return f'❌ Failed: {err}'


def get_problem_set(lab_id: str, ex_id: str, endpoint: str) -> dict:
    try:
        payload = {'question_id': f'{lab_id}/{ex_id}'}
        problem_set_response = send_request(payload, endpoint, method = 'GET')
        if problem_set_response.get('is_valid'):
            return problem_set_response['index'], problem_set_response['value']
        else:
            print(f'❌ Failed. Please confirm lab and exercise IDs.')
    except Exception as err:
        print(f'❌ Failed: {err}')


def _normalize_final_slash(url: str) -> str:
    if url[-1] != '/':
        url += '/'

    return url
