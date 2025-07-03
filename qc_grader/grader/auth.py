#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from qc_grader.grader.api import get_iam_token_endpoint


class IAMAuth:
    """
    Class for  Token Management via IAM
    """

    def __init__(self):
        self.token_url = get_iam_token_endpoint()
        self.api_key = os.getenv('IBMCLOUD_API_KEY')
        if self.api_key is None:
            from qiskit_ibm_runtime import QiskitRuntimeService
            self.api_key = QiskitRuntimeService.saved_accounts().get('qgss-2025', {}).get('token')

        if self.api_key is None:
            print("""
Account credentials missing or not properly saved.
Please save your account using `QiskitRuntimeService.save_account` following the instructions 
of QGSS 2025 Lab 0: https://github.com/qiskit-community/qgss-2025
""")
            raise ValueError("Account credentials missing or not properly saved. Please save your account using `QiskitRuntimeService.save_account` following the instructions of QGSS 2025 Lab 0: https://github.com/qiskit-community/qgss-2025")

        self.authenticator = IAMAuthenticator(self.api_key, url=self.token_url, disable_ssl_verification=True)

    def get_access_token(self):
        try:
            return self.authenticator.token_manager.get_token()
        except Exception as e:
            print("""
Account token is invalid or cannot be verified.
Please save a new account instance using `QiskitRuntimeService.save_account` following the
instructions of QGSS 2025 Lab 0: https://github.com/qiskit-community/qgss-2025
""")
            raise ValueError("""
Account token is invalid or cannot be verified.
Please save a new account instance using `QiskitRuntimeService.save_account` following the
instructions of QGSS 2025 Lab 0: https://github.com/qiskit-community/qgss-2025
""")

    def get_user_account(self):
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_OPTIONAL

        iam_service = IamIdentityV1(authenticator=self.authenticator)
        details = iam_service.get_api_keys_details(iam_api_key=self.api_key).get_result()
        return {
            "account_id": details.get("account_id"),
            "iam_id": details.get("iam_id")
        }
