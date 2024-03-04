import networkx as nx

from typeguard import typechecked

from typing import Callable, Dict

from qiskit import QuantumCircuit

from qc_grader.grader.grade import (
    grade, get_problem_set
)
from qc_grader.common.serializer import (
    circuit_to_json
)

from qiskit.algorithms.minimum_eigensolvers.sampling_vqe import SamplingVQEResult
from qiskit_optimization.applications import Tsp

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
        distance, order = tsp_function(inputs[i], int(i))
        answer[i] = {
            'distance': distance,
            'order': order
        }

    grade(answer, 'prob2-ex1', _challenge_id)


@typechecked
def grade_prob2_ex2(result: SamplingVQEResult) -> None:
    
    tsp = Tsp.create_random_instance(3, seed=123)
    adj_matrix = nx.to_numpy_array(tsp.graph)
    
    x = tsp.sample_most_likely(result.eigenstate)
    solution_order = tsp.interpret(x)
    solution_distance = tsp.tsp_value(solution_order, adj_matrix)
    
    answer = {
        'solution_order': solution_order,
        'solution_distance': solution_distance
    }

    grade(answer, 'prob2-ex2', _challenge_id)
