from typing import Callable, List
from typeguard import typechecked

import numpy as np
from scipy.optimize._optimize import OptimizeResult

from qiskit_serverless.core import QiskitFunction, Job

from qc_grader.grader.grade import grade


_challenge_id = 'qdc_2024'


@typechecked
def grade_day1a_ex1(qiskit_cf: QiskitFunction, job: Job) -> None:
    grade(
        [
            qiskit_cf.title,
            job.status()
        ],
        "day1a-ex1",
        _challenge_id,
    )