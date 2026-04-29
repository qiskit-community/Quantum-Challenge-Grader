# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import os

IS_STAGING = os.environ.get("STAGING") == "1"
IS_DEV = os.environ.get("DEV") == "1"

if IS_STAGING:
    GRADER_BASE_URL = "https://qac-grading-dev.quantum.ibm.com"
    IAM_BASE_URL = "https://iam.test.cloud.ibm.com"
elif IS_DEV:
    GRADER_BASE_URL = "http://127.0.0.1:5000"
    IAM_BASE_URL = "https://iam.test.cloud.ibm.com"
else:
    GRADER_BASE_URL = "https://qac-grading.quantum.ibm.com"
    IAM_BASE_URL = "https://iam.cloud.ibm.com"
