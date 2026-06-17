# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
QGSS 2026 Lab 4c - Grading Functions
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any, Sequence
from typeguard import typechecked, CollectionCheckStrategy

import numpy as np

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2026"
_LAB = "lab4c"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked(collection_check_strategy=CollectionCheckStrategy.ALL_ITEMS)
def grade_lab4c_ex1a(
    alpha_beta_indices: Sequence[Sequence[int]],
) -> None:
    """
    Grade Exercise 1a: Verify alpha-beta interaction pairs.

    Args:
        alpha_beta_indicies: A list of interaction pair indices
    """
    _grade(alpha_beta_indices, "ex1a")


@typechecked(collection_check_strategy=CollectionCheckStrategy.ALL_ITEMS)
def grade_lab4c_ex1b(
    initial_layout: Sequence[int],
) -> None:
    """
    Grade Exercise 1b: Verify initial layout.

    Args:
        initial_layout: A list of qubit layout
    """
    _grade(initial_layout, "ex1b")


@typechecked()
def grade_lab4c_ex2a(
    reshape_bitstring: Callable[[np.ndarray, int], np.ndarray],
    raw_bitstrings: np.ndarray,
) -> None:
    """
    Grade Exercise 2a: Verify bitstring reshape function.

    Args:
        reshape_bitstring: A bitstrign reshape function
        raw_bitstrings: Raw bitstring samples
    """
    output = reshape_bitstring(raw_bitstrings, 26)
    rng = np.random.default_rng(seed=42)
    test_bitstrings = rng.binomial(1, 0.25, (25, 12)).astype(bool)
    test_output = reshape_bitstring(test_bitstrings, 6)
    _grade((raw_bitstrings, output, test_bitstrings, test_output), "ex2a")


@typechecked()
def grade_lab4c_ex2b(
    hamming_weight: Callable[[np.ndarray], np.ndarray],
) -> None:
    """
    Grade Exercise 2b: Verify hamming weight function.

    Args:
        hamming_weight: A hamming weight function
    """
    rng = np.random.default_rng(seed=42)
    test_bitstrings = rng.binomial(1, 0.25, (25, 2, 6)).astype(bool)
    test_output = hamming_weight(test_bitstrings)
    _grade((test_bitstrings, test_output), "ex2b")


@typechecked()
def grade_lab4c_ex3a(
    prob_flip_0_to_1: Callable[[np.ndarray], np.ndarray],
) -> None:
    """
    Grade Exercise 3a: Verify probability weight function.

    Args:
        prob_flip_0_to_1: A probability weight function
    """
    rng = np.random.default_rng(seed=42)
    test_occupancy = rng.random((25, 24))
    test_output = np.array([prob_flip_0_to_1(occ) for occ in test_occupancy])
    _grade((test_occupancy, test_output), "ex3a")


@typechecked()
def grade_lab4c_ex3b(
    recover_configurations: Callable[
        [
            np.ndarray,
            np.ndarray,
            np.ndarray,
            int,
            tuple[int, int],
            np.random.Generator,
        ],
        tuple[np.ndarray, np.ndarray],
    ],
) -> None:
    """
    Grade Exercise 3b: Verify configuration recovery function.

    Args:
        recover_configurations: A configuration recovery function
    """
    rng = np.random.default_rng(seed=42)
    num_samples = 50
    probs = np.array([1 / num_samples] * num_samples)
    num_orbitals = 12
    num_elec = (6, 6)
    _utils = Path(__file__).parent / "utils"
    samples = np.load(_utils / "lab4c_test_samples.npy")
    occs = np.load(_utils / "lab4c_test_occ.npy")

    recovered_bitstrings, _ = recover_configurations(
        samples,
        probs,
        occs,
        num_orbitals,
        num_elec,
        rng,
    )
    _grade(recovered_bitstrings, "ex3b")


@typechecked()
def grade_lab4c_ex4(
    hf_like_ci_strings: np.ndarray,
) -> None:
    """
    Grade Exercise 4: Verify the ci string.

    Args:
        hf_like_ci_strings: An integer array that specifies the HF-like subspace. (Wrapped in a list)
    """
    _grade(hf_like_ci_strings, "ex4")


@typechecked()
def grade_lab4c_exbonus(
    best_energy: float,
    best_subspace: tuple[np.ndarray, np.ndarray],
) -> None:
    """
    Grade Exercise Bonus: Verify the ci string.

    Args:
        best_energy: A float value energy
        best_subspace: A pair of subsamples that specifies the diagonalization subspace
    """
    _grade((best_energy, best_subspace), "exbonus")
