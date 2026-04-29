# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import pytest

from qc_grader.grader.grade import determine_grade_response


@pytest.mark.parametrize(
    "status, score, cause, expected",
    [
        ("valid", None, None, "\nCongratulations 🎉! Your answer is correct."),
        (
            "valid",
            "95",
            None,
            "\nCongratulations 🎉! Your answer is correct.\nYour score is 95.",
        ),
        ("valid", None, "Well done!", "Well done!"),
        ("valid", "100", "Perfect!", "Perfect!\nYour score is 100."),
        (
            "invalid",
            None,
            None,
            "\nOops 😕! Your answer is incorrect\nPlease review your answer and try again.",
        ),
        (
            "invalid",
            None,
            "Off by one",
            "\nOops 😕! Off by one\nPlease review your answer and try again.",
        ),
        (
            "invalid",
            "50",
            "Wrong",
            "\nOops 😕! Wrong\nPlease review your answer and try again.",
        ),
        (
            "failed",
            None,
            "Server error",
            "Failed: Server error\nUnable to grade your answer.",
        ),
        (
            "failed",
            None,
            None,
            "Failed: Unexpected error\nUnable to grade your answer.",
        ),
        (None, None, None, "Failed: Unexpected error\nUnable to grade your answer."),
    ],
)
def test_determine_grade_response(
    status: str | None, score: str | None, cause: str | None, expected: str
) -> None:
    assert determine_grade_response(status, score, cause) == expected
