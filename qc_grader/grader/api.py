# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Any

import requests

from qc_grader import __version__
from qc_grader.grader.auth import get_access_token
from qc_grader.grader.env import GRADER_BASE_URL


def send_request(
    endpoint: str,
    body: dict[str, Any] | None = None,
    method: str = "POST",
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Version": __version__,
        "Authorization": f"Bearer {get_access_token()}",
    }

    response = requests.request(
        method, url=f"{GRADER_BASE_URL}{endpoint}", json=body, headers=headers
    )

    if response.status_code == 200:
        return response.json()

    if response.status_code == 204:
        return {}

    raise Exception(response.text)
