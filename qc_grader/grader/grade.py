# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Any, Optional, Union


from qc_grader.custom_encoder import to_json

from .api import send_request


def submit_team_name(answer: str, challenge_id: str) -> None:
    """Send the team name to the validate endpoint's submit-name question and print the result."""

    print("Submitting your team name. Please wait...")
    try:
        answer_response = send_request(
            f"/challenges/{challenge_id}/validate/submit-name",
            body={"answer": to_json(answer)},
        )
    except Exception as e:
        print(f"Failed: {e}")
        return

    if answer_response.get("status") == "valid":
        print("🎉 Team name submitted.")
        return

    cause = answer_response.get("cause")
    print(f"Failed to submit team name. {'' if cause is None else cause}")


def grade(answer: Any, question: str, challenge: str) -> None:
    """Send the answer to the validate endpoint and print the result."""

    print("Grading your answer. Please wait...")
    try:
        answer_response = send_request(
            f"/challenges/{challenge}/validate/{question}",
            body={"answer": to_json(answer)},
        )
    except Exception as e:
        print(f"Failed: {e}")
        return

    handle_grade_response(
        answer_response.get("status"),
        score=answer_response.get("score"),  # ty: ignore[invalid-argument-type]
        cause=answer_response.get("cause"),
    )


def handle_grade_response(
    status: Optional[str],
    score: Optional[Union[int, float]],
    cause: Optional[str],
) -> None:
    if status == "valid":
        if cause is not None:
            print(cause)
        else:
            print("\nCongratulations 🎉! Your answer is correct.")
        if score is not None:
            print(f"Your score is {score}.")
    elif status == "invalid":
        print(f"\nOops 😕! {'Your answer is incorrect' if cause is None else cause}")
        print("Please review your answer and try again.")
    else:
        print(f"Failed: {cause}")
        print("Unable to grade your answer.")
