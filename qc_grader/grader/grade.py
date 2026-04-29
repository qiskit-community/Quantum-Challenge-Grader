# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Any


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
    print(f"Failed to submit team name. {cause or ''}")


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

    print(
        determine_grade_response(
            answer_response.get("status"),
            score=answer_response.get("score"),
            cause=answer_response.get("cause"),
        )
    )


def determine_grade_response(
    status: str | None,
    score: str | None,
    cause: str | None,
) -> str:
    """Format a human-readable message from a grade response.

    Args:
        status: 'valid', 'invalid', or 'failed'.
        score: Numeric score, serialized as a string.
        cause: Server-provided message explaining the result.
    """
    if status == "valid":
        msg = (
            cause
            if cause is not None
            else "\nCongratulations 🎉! Your answer is correct."
        )
        if score is not None:
            msg += f"\nYour score is {score}."
        return msg

    if status == "invalid":
        return f"\nOops 😕! {cause or 'Your answer is incorrect'}\nPlease review your answer and try again."

    return f"Failed: {cause or 'Unexpected error'}\nUnable to grade your answer."
