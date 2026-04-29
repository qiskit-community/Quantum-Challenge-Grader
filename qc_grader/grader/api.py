# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import requests

from typing import Dict, Mapping, Optional

from qc_grader import __version__
from qc_grader.grader.auth import get_access_token
from qc_grader.grader.env import GRADER_BASE_URL


def send_request(
    endpoint: str,
    query: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, str]] = None,
    method: str = "POST",
    header: Optional[Mapping[str, str]] = None,
) -> Dict[str, str]:
    default_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Version": __version__,
        "Authorization": f"Bearer {get_access_token()}",
    }
    additional_header = header or {}
    header = {**default_header, **additional_header}

    response = requests.request(
        method,
        url=f"{GRADER_BASE_URL}{endpoint}",
        params=query,
        json=body,
        headers=header,
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
