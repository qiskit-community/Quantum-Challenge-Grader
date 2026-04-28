# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Any, Dict, Optional, Tuple, Union


from qc_grader.custom_encoder import to_json
from qc_grader.grader.auth import get_access_token

from .api import GRADER_URL, send_request


def grade(
    answer: Any,
    question: str,
    challenge: str,
    return_response: Optional[bool] = False,
) -> Tuple[bool, Optional[Union[str, int, float]], Optional[Union[str, int, float]]]:  # ty: ignore[invalid-return-type]
    endpoint = f"{GRADER_URL}/challenges/{challenge}/validate/{question}"
    payload = {"answer": to_json(answer)}

    print("Grading your answer. Please wait...")
    result = grade_answer(
        payload,
        endpoint,
        return_response=return_response,
    )

    if return_response:
        return result


def grade_answer(
    payload: Dict[str, str],
    endpoint: str,
    return_response: Optional[bool] = False,
) -> Tuple[bool, Optional[Union[str, int, float]], Optional[Union[str, int, float]]]:  # ty: ignore[invalid-return-type]
    try:
        header = {"Authorization": f"Bearer {get_access_token()}"}
        answer_response = send_request(endpoint, body=payload, header=header)

        status = answer_response.get("status", None)
        cause = answer_response.get("cause", None)
        score = answer_response.get("score", None)

        if return_response:
            s = status == "valid" or status is True
            return s, score, cause

        handle_grade_response(status, score=score, cause=cause)  # ty: ignore[invalid-argument-type]

    except Exception as err:
        print(f"Failed: {err}")
        return False, None, str(err)


def display_special_message(message: str, preamble="") -> None:
    if message.startswith("data:image/"):
        from IPython.display import display
        from ipywidgets import HTML

        print(preamble)
        display(HTML(f'<img src="{message}" />'))
    else:
        print(message)


def handle_grade_response(
    status: Optional[str],
    score: Optional[Union[int, float]] = None,
    cause: Optional[str] = None,
) -> None:
    if status == "valid" or status is True:
        if cause is not None:
            display_special_message(
                cause, preamble="\nCongratulations 🎉! Your answer is correct."
            )
        else:
            print("\nCongratulations 🎉! Your answer is correct.")
        if score is not None:
            print(f"Your score is {score}.")
    elif status == "invalid":
        print(f"\nOops 😕! {'Your answer is incorrect' if cause is None else cause}")
        print("Please review your answer and try again.")
    elif status == "notFinished":
        print(f"Job has not finished: {cause}")
        print("Please wait for the job to complete then try again.")
    else:
        print(f"Failed: {cause}")
        print("Unable to grade your answer.")
