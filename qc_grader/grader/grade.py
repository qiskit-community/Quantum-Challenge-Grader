# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import typeguard
from typing import Any, TypedDict

from typeguard import check_type

from qc_grader.custom_encoder import to_json

from .api import send_request


def submit_team_name(answer: str, challenge_id: str) -> None:
    """Register the user to the provided team, then print the result."""

    print("Submitting your team name. Please wait...\n")


class GradeResponse(TypedDict):
    passed: bool
    score: int | float
    msg: str


def grade_answer(answer: Any, lab: str, exercise: str, challenge: str) -> None:
    """Send the answer to the validate endpoint and print the result."""

    print("Grading your answer. Please wait...\n")
    try:
        response = send_request(
            f"/submissions/{challenge}/{lab}/{exercise}",
            body={"answer": to_json(answer)},
        )
        check_type(response, GradeResponse)
    except typeguard.TypeCheckError as e:
        print(
            "Server returned an unexpected response format. Try upgrading the "
            + "Quantum-Challenge-Grader dependency by following the instructions "
            + "at https://github.com/Qiskit-community/quantum-challenge-grader. "
            + f"Error: {e}"
        )
        return
    except Exception as e:
        print(f"Failed: {e}")
        return

    print(
        determine_grade_response(
            passed=response["passed"], score=response["score"], msg=response["msg"]
        )
    )


def determine_grade_response(
    passed: bool,
    score: int | float,
    msg: str,
) -> str:
    """Format a human-readable message from a grade response."""
    if passed:
        return msg + f"\nYour score is {score}."
    return f"\nOops 😕! {msg}\nPlease review your answer and try again."
