
from typeguard import typechecked

from typing import Callable, Dict, Tuple

from qiskit import QuantumCircuit

from qc_grader.grader.grade import (
    grade, get_problem_set
)
from qc_grader.grader.common import (
    circuit_to_json
)


_challenge_id = 'programming_challenge_aus'


@typechecked
def grade_prob1_ex3(qc: QuantumCircuit, counts: Dict[str, int]) -> None:
    answer = {
        'qc': circuit_to_json(qc),
        'counts': counts
    }

    grade(answer, 'prob1-ex3', _challenge_id)


@typechecked
def grade_prob2_ex1(tsp_function: Callable) -> None:
    _, inputs = get_problem_set('prob2-ex1', _challenge_id)

    answer = {}
    for i in inputs.keys():
        distance, order = tsp_function(inputs[i], i)
        answer[i] = {
            'distance': distance,
            'order': order
        }

    grade(answer, 'prob2-ex1', _challenge_id)


@typechecked
def grade_prob2_ex2(result, solution_order: Tuple, solution_distance: float) -> None:
    answer = {
        'vqe_energy': result.eigenvalue,
        'solution_order': solution_order,
        'solution_distance': solution_distance
    }

    grade(answer, 'prob2-ex2', _challenge_id)
