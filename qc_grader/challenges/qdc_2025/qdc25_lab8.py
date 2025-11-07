from typeguard import typechecked
from typing import Callable, Optional, Dict, List
import tempfile
import os

import numpy as np
import networkx as nx

from qiskit_serverless.core import QiskitFunction
from qiskit_addon_opt_mapper import OptimizationProblem
from qc_grader.grader.grade import grade

_challenge_id = "qdc_2025"

@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status == False:
        print(message)
    else:
        print("Team name submitted.")

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
def grade_lab8_ex1(parse_func: Callable) -> None:
    graph = parse_func("es60fst02.gph")
    answer_dict = {
        "vertices": len(graph.nodes),
        "edges": len(graph.edges),
        "density": nx.density(graph)
    }
    grade(answer_dict, "lab8-ex1", _challenge_id)


@typechecked
def grade_lab8_ex2(parse_func: Callable) -> None:
    # TODO: To be implemented
    answer_dict = ""
    grade(answer_dict, "lab8-ex2", _challenge_id)


@typechecked
def grade_lab8_ex3(solution_bitstring: str) -> None:
    grade(solution_bitstring, "lab8-ex3", _challenge_id)
