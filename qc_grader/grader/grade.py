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
from typing import Any, Callable, TypedDict, cast
from functools import partial

from typeguard import check_type, typechecked

from qc_grader.custom_encoder import to_json
from .api import send_request

# ------------------------------------------------------------------------------------------------------
# Teams
# ------------------------------------------------------------------------------------------------------


@typechecked
def _join_team(team_name: str, challenge_name: str) -> None:
    """Register the user with the provided team, then print a confirmation."""

    print(f'Trying to join "{team_name}", please wait...\n')

    try:
        send_request(
            "/register-team",
            body={
                "challenge_name": challenge_name,
                "team_name": team_name,
            },
        )
    except Exception as e:
        print(f"Failed: {e}")
        return

    print(
        f'You have joined "{team_name}" 🎉\n'
        "Any answers you submit from now on will be associated with this team."
    )


@typechecked
def create_join_team_function(challenge_name: str) -> Callable[[str], None]:
    return partial(_join_team, challenge_name=challenge_name)


# ------------------------------------------------------------------------------------------------------
# Submissions
# ------------------------------------------------------------------------------------------------------


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
    score_line = f"\nYou scored {score} on this exercise."
    if passed:
        return msg + score_line
    if score > 0:
        return f"\nOops 😕! {msg}{score_line}\nPlease review your answer and try again."
    return f"\nOops 😕! {msg}\nPlease review your answer and try again."


# ------------------------------------------------------------------------------------------------------
# Progress
# ------------------------------------------------------------------------------------------------------


class ExerciseSummary(TypedDict):
    name: str
    score: int | float
    passed: bool


class LabSummary(TypedDict):
    name: str
    score_total: int | float
    num_exercises_passed: int
    num_exercises: int
    per_exercise: list[ExerciseSummary]


class ChallengeAggregate(TypedDict):
    score_total: int | float
    num_exercises_passed: int
    num_exercises: int


class ProgressResponse(TypedDict):
    challenge_aggregate: ChallengeAggregate
    per_lab: list[LabSummary]


@typechecked
def _check_progress(challenge_name: str) -> None:
    """Fetch the user's progress for a challenge and print a summary."""

    print("Fetching your progress. Please wait...\n")
    try:
        response = send_request(f"/progress/{challenge_name}", method="GET")
        check_type(response, ProgressResponse)
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

    print(determine_progress_response(cast(ProgressResponse, response)))


@typechecked
def create_check_progress_function(challenge_name: str) -> Callable[[], None]:
    return partial(_check_progress, challenge_name=challenge_name)


def determine_progress_response(response: ProgressResponse) -> str:
    """Format a human-readable progress summary."""
    aggregate = response["challenge_aggregate"]
    lines = [
        "📊 Your progress",
        "",
        f"Exercises passed: {aggregate['num_exercises_passed']}/{aggregate['num_exercises']}",
        f"Total score: {aggregate['score_total']}",
    ]
    for lab in response["per_lab"]:
        lines.append("")
        lines.append(
            f'Lab "{lab["name"]}" — '
            f"{lab['num_exercises_passed']}/{lab['num_exercises']} passed, "
            f"score {lab['score_total']}"
        )
        for exercise in lab["per_exercise"]:
            icon = "✅" if exercise["passed"] else "⬜"
            lines.append(f"  {icon} {exercise['name']} — score {exercise['score']}")
    return "\n".join(lines)
