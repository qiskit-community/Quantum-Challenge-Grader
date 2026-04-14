#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2024
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

from typing import Dict, List, Mapping, Optional, Union

from qc_grader import __version__
from qc_grader.grader.common import normalize_slash, remove_slash


is_staging: bool = os.getenv("TARGET_ENV", "production").lower() == "staging"

# possible challenge grading endpoints: https://qac-grading-dev.quantum.ibm.com
grading_endpoints: List[str] = [
    "http://127.0.0.1:5000",
    f"https://qac-grading{'-dev' if is_staging else ''}.quantum.ibm.com",
]


_api_grade_url: Optional[str] = os.getenv("QC_GRADING_ENDPOINT")
_api_iam_token_url: Optional[str] = os.getenv("QC_IAM_TOKEN_ENDPOINT")


class MaxContentError(BaseException):
    def __init__(self, content_length: int, max_content_length: int) -> None:
        self.message = (
            f"Max content length ({max_content_length}) exceeded: {content_length}"
        )

    def __str__(self) -> str:
        return self.message


def get_iam_token_endpoint() -> Optional[str]:
    # https://iam.cloud.ibm.com/identity/token
    global _api_iam_token_url
    if not _api_iam_token_url:
        _api_iam_token_url = "https://iam.cloud.ibm.com/identity/token"
    return remove_slash(_api_iam_token_url)


def get_grading_endpoint(
    question_id: Union[str, int], challenge_id: str
) -> Optional[str]:
    # https://qac-grading-dev.quantum.ibm.com
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
        print(
            "Could not find a valid grading server or "
            "the grading servers are down right now."
        )
        return None

    return f"{normalize_slash(_api_grade_url)}challenges/{challenge_id}/validate/{question_id}"


def compute_content_length(
    endpoint: str,
    query: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, str]] = None,
    method: str = "POST",
    header: Optional[Mapping[str, str]] = None,
) -> int:
    from requests import Request

    header = (
        header
        if header
        else {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Client-Version": __version__,
        }
    )

    req = Request(method, url=endpoint, params=query, json=body, headers=header)
    prepped = req.prepare()
    return int(prepped.headers["Content-Length"])


def send_request(
    endpoint: str,
    query: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, str]] = None,
    method: str = "POST",
    header: Optional[Mapping[str, str]] = None,
    max_content_length: Optional[int] = None,
) -> Dict[str, str]:
    default_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Version": __version__,
    }
    additional_header = header or {}
    header = {**default_header, **additional_header}

    if max_content_length:
        content_length = compute_content_length(endpoint, body=body)
        if content_length >= max_content_length:
            raise MaxContentError(content_length, max_content_length)

    response = requests.request(
        method, url=endpoint, params=query, json=body, headers=header
    )

    if response.status_code != 200:
        if response.status_code == 403:
            result = f"Unable to access service ({response.reason})"
        else:
            try:
                result = response.json()
                if "error" in result:
                    result = result["error"]
                if "message" in result:
                    result = result["message"]
            except Exception:
                result = f" Not successful - {response.reason}"
        raise Exception(result)

    return response.json()
