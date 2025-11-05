from typeguard import typechecked, check_type
from typing import Callable, Optional, Dict, List
import tempfile
import os

import numpy as np

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
grade_kipu_function = make_validator("kipu-quantum")


@typechecked
def grade_lab7_ex1(parse_func: Callable) -> None:
    """
    Grade the parse_marketsplit_dat function implementation.

    Tests the function with a simple example to verify correct parsing logic.
    """

    # Create a simple test case
    test_content = """2 3
10 20 30 60
40 50 60 150
"""

    try:
        # Write test content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.dat') as f:
            f.write(test_content)
            temp_path = f.name

        try:
            # Test the parsing function
            A, b = parse_func(temp_path)

            answer_dict = {
                "A": A,
                "b": b,
            }

            grade(answer_dict, "lab7-ex1", _challenge_id)

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

    except Exception as e:
        return f"❌ Error testing your function: {str(e)}\nMake sure your function can handle the .dat format correctly."


@typechecked
def grade_lab7_ex2(A: Optional[np.ndarray], b: Optional[np.ndarray]) -> None:
    """
    Grade Exercise 2: Load and analyze problem instance.
    """
    answer_dict = {
        "A": A,
        "b": b,
    }

    grade(answer_dict, "lab7-ex2", _challenge_id)


@typechecked
def grade_lab7_ex3(qubo: OptimizationProblem, A: np.ndarray, b: np.ndarray) -> None:
    """
    Grade Exercise 3: Convert to QUBO matrix.

    Expected:
    - qubo: OptimizationProblem instance with proper objective function
    """

    answer_dict = {
        "qubo num vars": qubo.get_num_vars(),
        "qubo constant objective": qubo.objective.constant,
        "qubo linear objective": {idx: val for idx, val in enumerate(qubo.objective.linear)},
        "qubo quadratic objective": qubo.objective.quadratic.to_dict(),
        "A": A,
        "b": b,
    }

    grade(answer_dict, "lab7-ex3", _challenge_id)

@typechecked
def grade_lab7_ex4(problem: Dict[str, str], qubo: OptimizationProblem) -> None:
    """
    Grade Exercise 4: Convert QUBO to Iskay dictionary format.

    Expected:
    - problem: Dictionary with Iskay-formatted QUBO coefficients
    - qubo: OptimizationProblem instance for validation
    """

    answer_dict = {
        "problem": problem,
        "qubo num vars": qubo.get_num_vars(),
        "qubo constant objective": qubo.objective.constant,
        "qubo linear objective": {idx: val for idx, val in enumerate(qubo.objective.linear)},
        "qubo quadratic objective": {key: val for key, val in qubo.objective.quadratic.to_dict().items()},
        # TODO check the quad dict is identical to qubo.objective.quadratic.to_dict() or not
    }

    grade(answer_dict, "lab7-ex4", _challenge_id)


@typechecked
def grade_lab7_ex5(iskay_input: Dict) -> None:
    """
    Grade Exercise 5: Configure Iskay optimizer.

    Expected:
    - iskay_input: Dictionary with required fields for Iskay
    """

    grade(iskay_input, "lab7-ex5", _challenge_id)


@typechecked
def grade_lab7_ex6(quantum_solution: List[int]) -> str:
    """
    Grade Exercise 6: Validate solution.

    Expected:
    - quantum_solution: List of 0s and 1s with length matching A.shape[1]
    - Should be a valid binary solution
    """

    grade(quantum_solution, "lab7-ex6", _challenge_id)
