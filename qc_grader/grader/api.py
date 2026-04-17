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

from typing import Dict, Mapping, Optional

from qc_grader import __version__


GRADER_URL = os.environ.get("QC_GRADER_URL", "https://qac-grading.quantum.ibm.com")
IAM_URL = os.environ.get("QC_IAM_URL", default="https://iam.cloud.ibm.com")


class MaxContentError(BaseException):
    def __init__(self, content_length: int, max_content_length: int) -> None:
        self.message = (
            f"Max content length ({max_content_length}) exceeded: {content_length}"
        )

    def __str__(self) -> str:
        return self.message


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
