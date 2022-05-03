#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2022
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import os
import requests

from telnetlib import STATUS
from urllib.parse import urljoin

from typing import Dict, List, Mapping, Optional, Union

from qc_grader import __version__
from .common import MaxContentError, normalize_slash


is_staging: bool = 'auth-dev' in os.getenv('QXAuthURL', 'auth-dev')

# possible challenge grading endpoints: https://qac-grading-dev.quantum-computing.ibm.com
grading_endpoints: List[str] = [
    'http://127.0.0.1:5000',
    f'https://qac-grading{"-dev" if is_staging else ""}.quantum-computing.ibm.com'
]

# possible challenge api endpoints: https://challenges-api-dev.quantum-computing.ibm.com
submission_endpoints: List[str] = [
    'http://127.0.0.1:1337',
    f'https://challenges-api{"-dev" if is_staging else ""}.quantum-computing.ibm.com'
]

_api_auth_url: Optional[str] = os.getenv('QXAuthURL')
_api_grade_url: Optional[str] = os.getenv('QC_GRADING_ENDPOINT')
_api_submit_url: Optional[str] = os.getenv('QC_API_ENDPOINT')


def get_auth_endpoint() -> Optional[str]:
    # https://auth-dev.quantum-computing.ibm.com/api
    global _api_auth_url
    if not _api_auth_url:
        _api_auth_url = f'https://auth{"-dev" if is_staging else ""}.quantum-computing.ibm.com/api'
    return normalize_slash(_api_auth_url)


def get_problem_set_endpoint(
    question_id: Union[str, int], challenge_id: str
) -> Optional[str]:
    # https://qac-grading-dev.quantum-computing.ibm.com
    global _api_grade_url
    if not _api_grade_url:
        for endpoint in grading_endpoints:
            try:
                response = requests.get(url=endpoint)
                response.raise_for_status()
                if response.ok:
                    _api_grade_url = endpoint
                    break
            except Exception as err:
                pass

    if not _api_grade_url:
        print('Could not find a valid problem set server or '
              'the servers are down right now.')
        return None

    return f'{normalize_slash(_api_grade_url)}challenges/{challenge_id}/problem-set/{question_id}'


def get_grading_endpoint(
    question_id: Union[str, int], challenge_id: str
) -> Optional[str]:
    # https://qac-grading-dev.quantum-computing.ibm.com
    global _api_grade_url
    if not _api_grade_url:
        for endpoint in grading_endpoints:
            try:
                response = requests.get(url=endpoint)
                response.raise_for_status()
                if response.ok:
                    _api_grade_url = endpoint
                    break
            except Exception as err:
                pass

    if not _api_grade_url:
        print('Could not find a valid grading server or '
              'the grading servers are down right now.')
        return None

    return f'{normalize_slash(_api_grade_url)}challenges/{challenge_id}/validate/{question_id}'


def get_submission_endpoint(
    question_id: Union[str, int], challenge_id: str
) -> Optional[str]:
    # https://challenges-api-dev.quantum-computing.ibm.com
    global _api_submit_url
    if not _api_submit_url:
        for endpoint in submission_endpoints:
            try:
                response = requests.get(url=endpoint)
                response.raise_for_status()
                if response.status_code == 200:
                    _api_submit_url = endpoint
                    break
            except Exception as err:
                pass

    if not _api_submit_url:
        print('Could not find a valid API server or '
              'the API servers are down right now.')
        return None

    return f'{normalize_slash(_api_submit_url)}challenges/{challenge_id}/validate/{question_id}'


def get_access_token() -> str:
    iqx_token = os.getenv('QXToken')
    baseurl = get_auth_endpoint()
    endpoint = urljoin(baseurl, './users/loginWithToken')
    response = requests.post(endpoint, json={'apiToken': iqx_token})
    response.raise_for_status()
    return response.json()['id']


def get_question_set(
    challenge_id: str
) -> List[Dict[str, str]]:
    global _api_grade_url
    if not _api_grade_url:
        get_grading_endpoint('', challenge_id)

    exercises = []
    if _api_grade_url:
        try:
            response = requests.get(url=_api_grade_url)
            response.raise_for_status()

            challenges_metadata = response.json().get('challenges')
            if challenges_metadata:
                for challenge in challenges_metadata:
                    if challenge['id'] == challenge_id:
                        exercises = challenge['validations']
                        break
        except Exception as err:
            pass

    return exercises


def compute_content_length(
    endpoint: str,
    query: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, str]] = None,
    method: str = 'POST',
    header: Optional[Mapping[str, str]] = None
) -> int:
    from requests import Request
    header = header if header else {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Client-Version': __version__
    }

    req = Request(
        method,
        url=endpoint,
        params=query,
        json=body,
        headers=header
    )
    prepped = req.prepare()
    return int(prepped.headers['Content-Length'])


def send_request(
    endpoint: str,
    query: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, str]] = None,
    method: str = 'POST',
    header: Optional[Mapping[str, str]] = None,
    max_content_length: Optional[int] = None
) -> Dict[str, str]:
    default_header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Client-Version': __version__
    }
    additional_header = header or {}
    header = {**default_header, **additional_header}

    if max_content_length:
        content_length = compute_content_length(endpoint, body=body)
        if content_length >= max_content_length:
            raise MaxContentError(content_length, max_content_length)

    response = requests.request(
        method,
        url=endpoint,
        params=query,
        json=body,
        headers=header
    )

    if not response.ok:
        if response.status_code == 403:
            result = f'Unable to access service ({response.reason})'
        else:
            try:
                result = response.json()
                if 'error' in result:
                    result = result['error']
                if 'message' in result:
                    result = result['message']
            except Exception:
                result = response.reason
        raise Exception(result)

    return response.json()


def notify_provider(access_token: str, challenge_id: str) -> None:
    global _api_grade_url
    if not _api_grade_url:
        get_grading_endpoint('', challenge_id)

    if _api_grade_url:
        response = send_request(
            urljoin(_api_grade_url, './provider'),
            header={
                'X-Access-Token': access_token
            }
        )
