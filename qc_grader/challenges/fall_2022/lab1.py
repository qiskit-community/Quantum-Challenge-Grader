from typeguard import typechecked

from typing import Callable, List, Union

from qiskit import Aer, execute

from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.providers.aer.jobs import AerJob

from qiskit_ibm_runtime.qiskit.primitives import (
    SamplerResult as sampler_result,
    EstimatorResult as estimator_result
)

from qc_grader.grader.grade import grade, get_problem_set

_challenge_id = 'fall_2022'


def prepare_lab1_ex1(func: Callable) -> AerJob:
    _, inputs = get_problem_set('ex1-1', _challenge_id)

    circuits = []
    for i in inputs:
        qc = func(i)
        qc.metadata = {
            'qc_input': i
        }
        circuits.append(qc)

    backend = Aer.get_backend('qasm_simulator')
    job = execute(circuits, backend, shots=1024)
    return job

def grade_lab1_ex1(job: AerJob):
    grade(job, 'ex1-1', _challenge_id)


@typechecked
def grade_lab1_ex2(
    result: SamplerResult
) -> None:
    grade(result, 'ex1-2', _challenge_id)


@typechecked
def grade_lab1_ex3(
    result: EstimatorResult
) -> None:
    grade(result, 'ex1-3', _challenge_id)


@typechecked
def grade_lab1_ex4(result: List) -> None:
    grade(result, 'ex1-4', _challenge_id)


@typechecked
def grade_lab1_ex5(result: List) -> None:
    grade(result, 'ex1-5', _challenge_id)

@typechecked
def grade_lab1_ex6(message: str) -> None:
    grade(message, 'ex1-6', _challenge_id)
