import json

from typeguard import typechecked
from typing import Callable, List, Union

from qiskit.primitives import SamplerResult, EstimatorResult

from qiskit_ibm_runtime.qiskit.primitives import (
    SamplerResult as sampler_result,
    EstimatorResult as estimator_result
)

from qc_grader.grader.grade import (
    grade, get_problem_set,
    handle_submit_response,
    display_special_message
)
from qc_grader.grader.common import (
    circuit_to_json,
    samplerresult_to_json,
    estimatorresult_to_json
)


_challenge_id = 'fall_2022'


@typechecked
def grade_lab1_ex1(func: Callable) -> None:
    _, inputs = get_problem_set('ex1-1', _challenge_id)

    answer = []
    for i in inputs:
        circuit = func(i)
        answer.append({
            'qc': circuit_to_json(circuit),
            'input': i
        })

    grade(answer, 'ex1-1', _challenge_id)


@typechecked
def grade_lab1_ex2(
    result: Union[SamplerResult, sampler_result]
) -> None:
    grade(result, 'ex1-2', _challenge_id)


@typechecked
def grade_lab1_ex3(
    result: Union[EstimatorResult, estimator_result]
) -> None:
    grade(result, 'ex1-3', _challenge_id)


@typechecked
def grade_lab1_ex4(answer: List) -> None:
    grade(answer, 'ex1-4', _challenge_id)


# TODO: the circuit is not defined yet so the type might be changed
@typechecked
def grade_lab1_ex5(
    result: List
) -> None:
    answer = {
        'sampler_result': samplerresult_to_json(result[0]),
        'estimator_result': [estimatorresult_to_json(r) for r in result[1]]
    }
    status, _, resp = grade(answer, 'ex1-5', _challenge_id, return_response=True)
    try:
        info = json.loads(str(resp))
        if status:
            handle_submit_response(status, cause=info['img'])
        else:
            handle_submit_response(status, cause=info['msg'])
            if 'img' in info:
                display_special_message(info['img'])
    except Exception:
        handle_submit_response(status, cause=str(resp))


@typechecked
def grade_lab1_ex6(message: str) -> None:
    grade(message, 'ex1-6', _challenge_id)
