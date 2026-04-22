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
from ibm_platform_services import IamIdentityV1
from qiskit_ibm_runtime import QiskitRuntimeService

from qc_grader.grader.api import IAM_URL, IS_STAGING, IS_DEV

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


class IAMAuth:
    def __init__(self) -> None:
        self.api_key = read_api_key()
        if self.api_key is None:
            raise AuthenticationError(
                "Your IBM Quantum Platform API key is missing or not properly saved.\n\n"
                + "Save your account by following the instructions at "
                + "https://quantum.cloud.ibm.com/docs/en/guides/hello-world#install-and-authenticate "
                + "to use `QiskitRuntimeService.save_account()`.\n\nAlternatively, set the environment variable "
                + f"{_AUTH_ENV_VAR_NAME} with your IBM Quantum Platform API key."
            ).with_traceback(None)

        self.authenticator = IAMAuthenticator(
            self.api_key, url=f"{IAM_URL}/identity/token", disable_ssl_verification=True
        )

    def get_access_token(self) -> str:
        try:
            return self.authenticator.token_manager.get_token()
        except Exception:
            raise AuthenticationError(
                "An authentication token could not be generated from your IBM Quantum Platform API key. Usually, "
                + "this means that your API key is invalid or expired.\n\nYou can try to set up a new API key "
                + "by following the instructions at "
                + "https://quantum.cloud.ibm.com/docs/en/guides/hello-world#install-and-authenticate "
                + "to use `QiskitRuntimeService.save_account()`.\n\nAlternatively, set the environment variable "
                + f"{_AUTH_ENV_VAR_NAME} with your IBM Quantum Platform API key."
            )

    def get_user_account(self):
        import ssl

        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_OPTIONAL

        iam_service = IamIdentityV1(authenticator=self.authenticator)
        iam_service.service_url = IAM_URL

        details = iam_service.get_api_keys_details(
            iam_api_key=self.api_key
        ).get_result()
        return {
            "account_id": details.get("account_id"),  # ty: ignore[unresolved-attribute]
            "iam_id": details.get("iam_id"),  # ty: ignore[unresolved-attribute]
        }
