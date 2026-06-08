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
    "passed, score, msg, expected",
    [
        (
            True,
            1,
            "🎉 Correct!",
            "🎉 Correct!\nYou scored 1 on this exercise.",
        ),
        (
            True,
            2,
            "🎉 Both Circuit A and Circuit B have depth 3.",
            "🎉 Both Circuit A and Circuit B have depth 3.\nYou scored 2 on this exercise.",
        ),
        (
            False,
            0,
            "Circuit A: you said 2, but depth is 3.",
            "\nOops 😕! Circuit A: you said 2, but depth is 3.\nPlease review your answer and try again.",
        ),
        (
            False,
            1,
            "Incorrect basis operations.",
            "\nOops 😕! Incorrect basis operations.\nYou scored 1 on this exercise.\nPlease review your answer and try again.",
        ),
    ],
)
def test_determine_grade_response(
    passed: bool, score: int | float, msg: str, expected: str
) -> None:
    assert determine_grade_response(passed, score, msg) == expected
