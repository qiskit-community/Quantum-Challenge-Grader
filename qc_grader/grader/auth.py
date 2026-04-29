# (C) Copyright IBM 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Token Management via IAM"""

import os

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from qiskit_ibm_runtime import QiskitRuntimeService

from qc_grader.grader.env import IAM_BASE_URL, IS_STAGING, IS_DEV

_AUTH_ENV_VAR_NAME = "QC_API_KEY"


class AuthenticationError(Exception):
    pass


def read_api_key() -> str | None:
    """Attempt to read the user's API key.

    The order of operations matters.

    1. Read the legacy `IBMCLOUD_API_KEY` env var, with fallback to `saved_accounts().get("qdc-2025")`.
       We start with this to avoid breaking Road To Practioner users still using qdc-2025.
    2. Read the `QC_API_KEY` env var.
    3. If it's staging or local development, read `saved_accounts().get("grader-staging")`.
    4. Read the default account with QiskitRuntimeService.

    Once qdc-2025 is no longer used, we can remove the legacy approach.
    """
    if key := os.environ.get("IBMCLOUD_API_KEY"):
        return key
    if key := QiskitRuntimeService.saved_accounts().get("qdc-2025", {}).get("token"):
        return key
    if key := os.environ.get(_AUTH_ENV_VAR_NAME):
        return key

    if (IS_STAGING or IS_DEV) and (
        key := QiskitRuntimeService.saved_accounts()
        .get("grader-staging", {})
        .get("token")
    ):
        return key

    if key := (QiskitRuntimeService().active_account() or {}).get("token"):
        return key
    return None


def get_access_token() -> str:
    api_key = read_api_key()
    if api_key is None:
        raise AuthenticationError(
            "Your IBM Quantum Platform API key is missing or not properly saved.\n\n"
            + "Save your account by following the instructions at "
            + "https://quantum.cloud.ibm.com/docs/en/guides/hello-world#install-and-authenticate "
            + "to use `QiskitRuntimeService.save_account()`.\n\nAlternatively, set the environment variable "
            + f"{_AUTH_ENV_VAR_NAME} with your IBM Quantum Platform API key."
        ).with_traceback(None)

    try:
        return IAMAuthenticator(
            api_key, url=f"{IAM_BASE_URL}/identity/token"
        ).token_manager.get_token()
    except Exception:
        raise AuthenticationError(
            "An authentication token could not be generated from your IBM Quantum Platform API key. Usually, "
            + "this means that your API key is invalid or expired.\n\nYou can try to set up a new API key "
            + "by following the instructions at "
            + "https://quantum.cloud.ibm.com/docs/en/guides/hello-world#install-and-authenticate "
            + "to use `QiskitRuntimeService.save_account()`.\n\nAlternatively, set the environment variable "
            + f"{_AUTH_ENV_VAR_NAME} with your IBM Quantum Platform API key."
        )
