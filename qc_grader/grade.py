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
import os
import requests

from typing import Optional, Union
from urllib.parse import urljoin

from qiskit import QuantumCircuit
from qiskit.providers import JobStatus
from qiskit.providers.ibmq.job import IBMQJob

from .api import get_server_endpoint, send_request, get_access_token, get_auth_endpoint
from .exercises import get_question_id
from .util import get_job, get_job_status, circuit_to_json, get_job_urls


def grade(
    answer: Union[str, int, IBMQJob, QuantumCircuit],
    lab_id: str,
    ex_id: str,
    server_url: Optional[str] = None
) -> None:
    server = server_url if server_url else get_server_endpoint(lab_id, ex_id)
    if not server:
        print('Could not find a valid grading server or the grading servers are down right now.')
        return

    payload = make_payload(answer, lab_id, ex_id)

    if payload:
        score = None
        if isinstance(answer, IBMQJob) or isinstance(answer, str):
            job = get_job(answer) if isinstance(answer, str) else answer
            if job:
                qobj_header = job.result().header.to_dict() if job else {}
                score = qobj_header['qc_cost'] if 'qc_cost' in qobj_header else None

        print('Grading your answer. Please wait...')
        check_answer(
            payload,
            server + 'validate-answer',
            cost=score
        )


def submit(
    answer: Union[str, int, IBMQJob, QuantumCircuit],
    lab_id: str,
    ex_id: str
) -> None:
    payload = make_payload(answer, lab_id, ex_id)
    payload['questionNumber'] = payload['question_id']
    del payload['question_id']

    if payload:
        print('Submitting your answer. Please wait...')
        submit_answer(payload)


def make_payload(
    answer: Union[str, int, IBMQJob, QuantumCircuit],
    lab_id: str,
    ex_id: str
) -> Optional[dict]:
    if not lab_id:
        print('Missing lab id. Please include the lab id.')
        return None
    if not ex_id:
        print('Missing exercise id. Please include the exercise id.')
        return None

    payload = {
        'question_id': get_question_id(lab_id, ex_id)
    }

    if isinstance(answer, IBMQJob) or isinstance(answer, str):
        job_id, status = get_job_status(answer)
        if status is JobStatus.DONE:
            ok, download_url, result_url = get_job_urls(job_id)
            if ok:
                payload['answer'] = json.dumps({
                    'download_url': download_url,
                    'result_url': result_url
                })
            else:
                print('An invalid or non-existent job was specified.')
                return None
        else:
            if status is None:
                print('An invalid or non-existent job was specified.')
            elif status in [JobStatus.CANCELLED, JobStatus.ERROR]:
                print(f'Job did not successfully complete: {status.value}.')
            else:
                print(f'Job has not yet completed: {status.value}.')
                print(f'Please wait for the job (id: {job_id}) to complete then try again.')
            return None
    elif isinstance(answer, QuantumCircuit):
        payload['answer'] = circuit_to_json(answer)
    elif isinstance(answer, int):
        payload['answer'] = str(answer)
    else:
        print(f'Unsupported answer type: {type(answer)}')
        return None

    return payload


def check_answer(payload: dict, endpoint: str, cost: Optional[int] = None) -> None:
    try:
        answer_response = send_request(endpoint, body=payload)

        status = answer_response.get('status', None)
        cause = answer_response.get('cause', None)
        score = cost if cost else answer_response.get('score', None)

        handle_grade_response(status, score=score, cause=cause)
    except Exception as err:
        print(f'Failed: {err}')


def submit_answer(payload: dict) -> None:
    try:
        access_token = get_access_token()

        baseurl = get_auth_endpoint()
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
    except Exception as err:
        print(f'Failed: {err}')


def handle_grade_response(
    status: Optional[str], score: Optional[int] = None, cause: Optional[str] = None
) -> None:
    if status == 'valid':
        print('\nCongratulations 🎉! Your answer is correct.')
        if score is not None:
            print(f'Your score is {score}. The lower, the better!')
        print('Feel free to submit your answer.')
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
    status: str, cause: Optional[str] = None
) -> None:
    if status == 'valid' or status == True:
        print('\nSuccess 🎉! Your answer has been submitted.')
    elif status == 'invalid' or status == False:
        print(f'\nOops 😕! {"Your answer is incorrect" if cause is None else cause}')
        print('Make sure your answer is correct and successfully graded before submitting.')
    elif status == 'notFinished':
        print(f'Job has not finished: {cause}')
        print(f'Please wait for the job to complete, grade it, and then try to submit again.')
    else:
        print(f'Failed: {cause}')
        print('Unable to submit your answer at this time.')
