# (C) Copyright IBM 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typeguard import typechecked
from typing import Callable
import os

import networkx as nx

from qiskit_serverless.core import QiskitFunction
from qiskit_addon_opt_mapper import OptimizationProblem
from qc_grader.grader.grade import grade

_challenge_id = "qdc_2025"


def validate_function(
    function_provider: str,
    function_title: str,
) -> None:
    grade(function_title, function_provider, _challenge_id)


def make_validator(function_provider: str):
    @typechecked
    def validator(function: QiskitFunction) -> None:
        validate_function(
            function_provider=function_provider,
            function_title=function.title,
        )

    return validator


# Generate and assign the validators
grade_qctrl_function = make_validator("q-ctrl")


@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status is False:
        print(message)
    else:
        print("Team name submitted.")


@typechecked
def grade_lab8_ex1(parse_func: Callable) -> None:

    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, "es60fst02.gph")
    graph = parse_func(full_path)
    answer_dict = {
        "vertices": len(graph.nodes),
        "edges": len(graph.edges),
        "density": nx.density(graph),
    }
    grade(answer_dict, "lab8-ex1", _challenge_id)


@typechecked
def grade_lab8_ex2(qubo: OptimizationProblem) -> None:
    linear_dict = {idx: val for idx, val in enumerate(qubo.objective.linear)}  # ty: ignore[invalid-argument-type]
    # convert tuple key to string for serialization, e.g. (0, 0) => '(0, 0)'
    quadratic_dict = {str(k): v for k, v in qubo.objective.quadratic.to_dict().items()}

    answer_dict = {
        "qubo num vars": qubo.get_num_vars(),
        "qubo constant objective": qubo.objective.constant,
        "qubo linear objective": linear_dict,
        "qubo quadratic objective": quadratic_dict,
    }

    grade(answer_dict, "lab8-ex2", _challenge_id)


@typechecked
def grade_lab8_ex3(solution_bitstring: str) -> None:
    grade(solution_bitstring, "lab8-ex3", _challenge_id)
