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
from unittest.mock import patch

from qc_grader.grader.grade import (
    ProgressResponse,
    determine_grade_response,
    determine_progress_response,
    grade_answer,
)


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
            "\nNot quite! Circuit A: you said 2, but depth is 3.\nPlease review your answer and try again.",
        ),
        (
            False,
            1,
            "Incorrect basis operations.",
            "\nNot quite! Incorrect basis operations.\nYou scored 1 on this exercise.\nPlease review your answer and try again.",
        ),
    ],
)
def test_determine_grade_response(
    passed: bool, score: int | float, msg: str, expected: str
) -> None:
    assert determine_grade_response(passed, score, msg) == expected


_MULTI_LAB_RESPONSE = ProgressResponse(
    challenge_aggregate={
        "score_total": 7,
        "num_exercises_passed": 3,
        "num_exercises": 5,
    },
    per_lab=[
        {
            "name": "lab_skqd",
            "score_total": 4,
            "num_exercises_passed": 2,
            "num_exercises": 3,
            "per_exercise": [
                {"name": "ex1", "score": 2, "passed": True},
                {"name": "ex2", "score": 2, "passed": True},
                {"name": "ex3", "score": 0, "passed": False},
            ],
        },
        {
            "name": "lab_qmoo",
            "score_total": 3,
            "num_exercises_passed": 1,
            "num_exercises": 2,
            "per_exercise": [
                {"name": "ex1", "score": 3, "passed": True},
                {"name": "ex2", "score": 0, "passed": False},
            ],
        },
    ],
)


@pytest.mark.parametrize(
    "response, lab_name, expected",
    [
        # Single lab, no filter
        (
            ProgressResponse(
                challenge_aggregate={
                    "score_total": 5,
                    "num_exercises_passed": 2,
                    "num_exercises": 3,
                },
                per_lab=[
                    {
                        "name": "lab_skqd",
                        "score_total": 5,
                        "num_exercises_passed": 2,
                        "num_exercises": 3,
                        "per_exercise": [
                            {"name": "ex1", "score": 3, "passed": True},
                            {"name": "ex2", "score": 2, "passed": True},
                            {"name": "ex3", "score": 0, "passed": False},
                        ],
                    },
                ],
            ),
            None,
            "📊 Your progress\n"
            "\n"
            "Exercises passed: 2/3\n"
            "Total score: 5\n"
            "\n"
            'Lab "lab_skqd" — 2/3 passed, score 5\n'
            "  ✅ ex1 — score 3\n"
            "  ✅ ex2 — score 2\n"
            "  ⬜ ex3 — score 0",
        ),
        # No labs, no filter
        (
            ProgressResponse(
                challenge_aggregate={
                    "score_total": 0,
                    "num_exercises_passed": 0,
                    "num_exercises": 0,
                },
                per_lab=[],
            ),
            None,
            "📊 Your progress\n\nExercises passed: 0/0\nTotal score: 0",
        ),
        # Multi-lab, no filter — shows aggregate + all labs
        (
            _MULTI_LAB_RESPONSE,
            None,
            "📊 Your progress\n"
            "\n"
            "Exercises passed: 3/5\n"
            "Total score: 7\n"
            "\n"
            'Lab "lab_skqd" — 2/3 passed, score 4\n'
            "  ✅ ex1 — score 2\n"
            "  ✅ ex2 — score 2\n"
            "  ⬜ ex3 — score 0\n"
            "\n"
            'Lab "lab_qmoo" — 1/2 passed, score 3\n'
            "  ✅ ex1 — score 3\n"
            "  ⬜ ex2 — score 0",
        ),
        # Multi-lab, filtered to first lab — no aggregate
        (
            _MULTI_LAB_RESPONSE,
            "lab_skqd",
            "📊 Your progress\n"
            "\n"
            'Lab "lab_skqd" — 2/3 passed, score 4\n'
            "  ✅ ex1 — score 2\n"
            "  ✅ ex2 — score 2\n"
            "  ⬜ ex3 — score 0",
        ),
        # Multi-lab, filtered to second lab — no aggregate
        (
            _MULTI_LAB_RESPONSE,
            "lab_qmoo",
            "📊 Your progress\n"
            "\n"
            'Lab "lab_qmoo" — 1/2 passed, score 3\n'
            "  ✅ ex1 — score 3\n"
            "  ⬜ ex2 — score 0",
        ),
    ],
)
def test_determine_progress_response(
    response: ProgressResponse, lab_name: str | None, expected: str
) -> None:
    assert determine_progress_response(response, lab_name=lab_name) == expected


def test_determine_progress_response_unknown_lab() -> None:
    with pytest.raises(ValueError, match='No lab named "lab_missing" found.'):
        determine_progress_response(_MULTI_LAB_RESPONSE, lab_name="lab_missing")


def test_grade_answer_too_large(capsys: pytest.CaptureFixture) -> None:
    with patch("qc_grader.grader.grade._MAX_ANSWER_BYTES", 10):
        grade_answer("this answer is definitely over 10 bytes", "lab1", "ex1", "ch1")
    out = capsys.readouterr().out
    assert "too large to submit" in out
    assert "MB" in out
