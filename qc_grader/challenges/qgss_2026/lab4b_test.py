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
Unit tests for lab4b helper functions, particularly _dict_contains.

These tests focus on validating the _dict_contains function with real-world
SamplerOptions usage patterns, as this is the primary use case in the grading code.
"""

# pyright: reportAttributeAccessIssue=false

from dataclasses import asdict
from unittest.mock import Mock, patch

import numpy as np
import pytest
from qiskit_ibm_runtime import RuntimeJobV2
from qiskit_ibm_runtime.fake_provider.local_runtime_job import LocalRuntimeJob
from qiskit_ibm_runtime.options import EstimatorOptions, SamplerOptions

from qc_grader.challenges.qgss_2026.lab4b import (
    _dict_contains,
    _extract_qpu_usage_seconds,
    _find_best_result,
    _reconstruct_exp_map,
    grade_lab4b_ex4,
    grade_lab4b_exbonus,
)


# ------------------------------------------------------------------------------------------------------
# Core functionality tests
# ------------------------------------------------------------------------------------------------------


def test_dict_contains_nested_subset():
    """Test nested dicts where subset has fewer nested keys."""
    full = {"a": 1, "b": {"x": 10, "y": 20, "z": 30}}
    subset = {"b": {"x": 10, "y": 20}}
    assert _dict_contains(full, subset) is True


def test_dict_contains_nested_missing_key():
    """Test nested dicts with missing key in nested dict."""
    full = {"a": 1, "b": {"x": 10}}
    subset = {"b": {"x": 10, "y": 20}}
    assert _dict_contains(full, subset) is False


# ------------------------------------------------------------------------------------------------------
# SamplerOptions: Configuration tests (consolidated)
# ------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "full_config,subset_config,expected",
    [
        # Basic shots mismatch
        (
            {"default_shots": 1000},
            {"default_shots": 2000},
            False,
        ),
        # DD: enable only (match)
        (
            {"dynamical_decoupling": {"enable": True, "sequence_type": "XY4"}},
            {"dynamical_decoupling": {"enable": True}},
            True,
        ),
        # DD: full config (match)
        (
            {"dynamical_decoupling": {"enable": True, "sequence_type": "XY4"}},
            {"dynamical_decoupling": {"enable": True, "sequence_type": "XY4"}},
            True,
        ),
        # DD: enable mismatch
        (
            {"dynamical_decoupling": {"enable": True}},
            {"dynamical_decoupling": {"enable": False}},
            False,
        ),
        # DD: sequence type mismatch
        (
            {"dynamical_decoupling": {"enable": True, "sequence_type": "XY4"}},
            {"dynamical_decoupling": {"enable": True, "sequence_type": "XX"}},
            False,
        ),
        # Twirling: gates only (match)
        (
            {"twirling": {"enable_gates": True, "enable_measure": False}},
            {"twirling": {"enable_gates": True}},
            True,
        ),
        # Twirling: full config (match)
        (
            {"twirling": {"enable_gates": True, "enable_measure": True}},
            {"twirling": {"enable_gates": True, "enable_measure": True}},
            True,
        ),
        # Twirling: gates mismatch
        (
            {"twirling": {"enable_gates": True}},
            {"twirling": {"enable_gates": False}},
            False,
        ),
        # Twirling: measure mismatch
        (
            {"twirling": {"enable_gates": True, "enable_measure": True}},
            {"twirling": {"enable_gates": True, "enable_measure": False}},
            False,
        ),
        # Combined: DD and twirling (match)
        (
            {
                "default_shots": 1000,
                "dynamical_decoupling": {"enable": True, "sequence_type": "XY4"},
                "twirling": {"enable_gates": True},
            },
            {
                "dynamical_decoupling": {"enable": True},
                "twirling": {"enable_gates": True},
            },
            True,
        ),
        # Combined: all settings (match)
        (
            {
                "default_shots": 2000,
                "dynamical_decoupling": {"enable": True, "sequence_type": "XY4"},
                "twirling": {"enable_gates": True, "enable_measure": True},
            },
            {
                "default_shots": 2000,
                "dynamical_decoupling": {"enable": True},
                "twirling": {"enable_gates": True},
            },
            True,
        ),
        # Combined: partial mismatch
        (
            {
                "dynamical_decoupling": {"enable": True},
                "twirling": {"enable_gates": True},
            },
            {
                "dynamical_decoupling": {"enable": True},
                "twirling": {"enable_gates": False},
            },
            False,
        ),
    ],
)
def test_sampler_options_configurations(full_config, subset_config, expected):
    """Test various SamplerOptions configurations with _dict_contains."""
    full_options = SamplerOptions()
    subset_options = SamplerOptions()

    # Apply configurations
    for key, value in full_config.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                setattr(getattr(full_options, key), subkey, subvalue)
        else:
            setattr(full_options, key, value)

    for key, value in subset_config.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                setattr(getattr(subset_options, key), subkey, subvalue)
        else:
            setattr(subset_options, key, value)

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    # Filter subset_dict to only include configured keys
    subset_dict_filtered = {}
    for key, value in subset_config.items():
        if isinstance(value, dict):
            subset_dict_filtered[key] = {k: subset_dict[key][k] for k in value.keys()}
        else:
            subset_dict_filtered[key] = subset_dict[key]

    assert _dict_contains(full_dict, subset_dict_filtered) is expected


# ------------------------------------------------------------------------------------------------------
# Tests for _find_best_result
# ------------------------------------------------------------------------------------------------------


def test_find_best_result_single_method() -> None:
    """Test with a single method in results."""
    results_dict = {
        "No EM": {
            "set0": [1, 2, 3],
            "set1": [4, 5, 6],
            "difference": 10.5,
        }
    }

    best_diff, best_method, total_sum = _find_best_result(results_dict)  # type: ignore

    assert best_diff == 10.5
    assert best_method == "No EM"
    assert total_sum == 21  # 1+2+3+4+5+6


def test_find_best_result_multiple_methods() -> None:
    """Test finding the best result among multiple methods."""
    results_dict = {
        "No EM": {
            "set0": [1, 2],
            "set1": [3, 4],
            "difference": 15.0,
        },
        "TREX": {
            "set0": [1, 2],
            "set1": [3, 4],
            "difference": 5.0,
        },
        "ZNE": {
            "set0": [1, 2],
            "set1": [3, 4],
            "difference": 10.0,
        },
    }

    best_diff, best_method, total_sum = _find_best_result(results_dict)  # type: ignore

    assert best_diff == 5.0
    assert best_method == "TREX"
    assert total_sum == 10  # Same for all methods


def test_find_best_result_negative_difference() -> None:
    """Test that negative differences are handled correctly."""
    results_dict = {
        "No EM": {
            "set0": [1],
            "set1": [2],
            "difference": -5.0,
        },
        "TREX": {
            "set0": [1],
            "set1": [2],
            "difference": 10.0,
        },
    }

    best_diff, best_method, total_sum = _find_best_result(results_dict)  # type: ignore

    assert best_diff == -5.0
    assert best_method == "No EM"


# ------------------------------------------------------------------------------------------------------
# Tests for _reconstruct_exp_map
# ------------------------------------------------------------------------------------------------------


def test_reconstruct_exp_map_empty_result() -> None:
    """Test with a job that has no pub_results."""
    mock_job = Mock()
    mock_job.result.return_value = []

    exp_map = _reconstruct_exp_map(mock_job)

    assert exp_map == {}


def test_reconstruct_exp_map_single_pub_result() -> None:
    """Test with a single pub_result containing multiple evs."""
    mock_job = Mock()
    mock_pub_result = Mock()
    mock_data = Mock()
    mock_data.evs = [1.5, 2.5, 3.5]
    mock_pub_result.data = mock_data
    mock_job.result.return_value = [mock_pub_result]

    exp_map = _reconstruct_exp_map(mock_job)

    assert exp_map == {0: 1.5, 1: 2.5, 2: 3.5}


def test_reconstruct_exp_map_multiple_pub_results() -> None:
    """Test with multiple pub_results, each with multiple evs."""
    mock_job = Mock()

    mock_pub_result1 = Mock()
    mock_data1 = Mock()
    mock_data1.evs = [1.0, 2.0]
    mock_pub_result1.data = mock_data1

    mock_pub_result2 = Mock()
    mock_data2 = Mock()
    mock_data2.evs = [3.0, 4.0]
    mock_pub_result2.data = mock_data2

    mock_job.result.return_value = [mock_pub_result1, mock_pub_result2]

    exp_map = _reconstruct_exp_map(mock_job)

    assert exp_map == {0: 1.0, 1: 2.0, 2: 3.0, 3: 4.0}


def test_reconstruct_exp_map_numpy_values() -> None:
    """Test that numpy floating point values are converted to float."""
    mock_job = Mock()
    mock_pub_result = Mock()
    mock_data = Mock()
    mock_data.evs = [np.float64(1.5), np.float32(2.5)]
    mock_pub_result.data = mock_data
    mock_job.result.return_value = [mock_pub_result]

    exp_map = _reconstruct_exp_map(mock_job)

    assert exp_map == {0: 1.5, 1: 2.5}
    # Verify they are Python floats, not numpy types
    assert isinstance(exp_map[0], float)
    assert isinstance(exp_map[1], float)


# ------------------------------------------------------------------------------------------------------
# Tests for grade_lab4b_ex4 (integration-style tests focusing on edge cases)
# ------------------------------------------------------------------------------------------------------


def _create_base_result(exp_map=None):
    """Helper to create a complete base result dict with all required fields."""
    if exp_map is None:
        exp_map = {0: np.float64(1.0), 1: np.float64(2.0)}
    return {
        "loss": np.float64(0.0),
        "par0": [0, 1],
        "par1": [2, 3],
        "par0_size": 2,
        "par1_size": 2,
        "best_cut": np.float64(1.0),
        "best_index": 0,
        "set0": [1, 2],
        "set1": [3, 4],
        "difference": 5.0,
        "exp_map": exp_map,
    }


def _create_mock_job(evs):
    """Helper to create a mock job with specified evs."""
    mock_job = Mock()
    mock_pub_result = Mock()
    mock_data = Mock()
    mock_data.evs = evs
    mock_pub_result.data = mock_data
    mock_job.result.return_value = [mock_pub_result]
    return mock_job


def test_grade_lab4b_ex4_exp_map_mismatch_raises_error() -> None:
    """Test that mismatched exp_map raises ValueError."""
    mock_job = _create_mock_job([1.0, 2.0])
    base_result = _create_base_result()

    results_dict = {
        "No EM": {
            **base_result,
            "exp_map": {0: np.float64(999.0), 1: np.float64(888.0)},
        },
        "TREX": {**base_result, "difference": 10.0},
        "ZNE": {**base_result, "difference": 15.0},
        "PEC": {**base_result, "difference": 20.0},
    }

    options_list = [EstimatorOptions() for _ in range(4)]
    job_list = [mock_job] * 4

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        with pytest.raises(ValueError, match="exp_map.*does not match"):
            grade_lab4b_ex4(options_list, results_dict, job_list)  # type: ignore


def test_grade_lab4b_ex4_matching_exp_map_no_error() -> None:
    """Test that matching exp_map doesn't raise an error and emits expected warnings."""
    mock_job = _create_mock_job([1.0, 2.0])
    base_result = _create_base_result()

    results_dict = {
        "No EM": base_result,
        "TREX": {**base_result, "difference": 10.0},
        "ZNE": {**base_result, "difference": 15.0},
        "PEC": {**base_result, "difference": 20.0},
    }

    options_list = [EstimatorOptions() for _ in range(4)]
    job_list = [mock_job] * 4

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        with pytest.warns(UserWarning, match="simulator"):
            grade_lab4b_ex4(options_list, results_dict, job_list)  # type: ignore


def test_grade_lab4b_ex4_local_runtime_job_warning() -> None:
    """Test that LocalRuntimeJob triggers a warning."""
    mock_job = Mock(spec=LocalRuntimeJob)
    mock_pub_result = Mock()
    mock_data = Mock()
    mock_data.evs = [1.0]
    mock_pub_result.data = mock_data
    mock_job.result.return_value = [mock_pub_result]

    base_result = _create_base_result({0: np.float64(1.0)})

    results_dict = {
        "No EM": base_result,
        "TREX": {**base_result, "difference": 10.0},
        "ZNE": {**base_result, "difference": 15.0},
        "PEC": {**base_result, "difference": 20.0},
    }

    options_list = [EstimatorOptions() for _ in range(4)]
    job_list = [mock_job] * 4

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        with pytest.warns(UserWarning, match="simulator"):
            grade_lab4b_ex4(options_list, results_dict, job_list)  # type: ignore


def test_grade_lab4b_ex4_stored_exp_map_none_raises_error() -> None:
    """Test that when stored_exp_map is None, a validation error is raised."""
    mock_job = _create_mock_job([1.0, 2.0])
    base_result = _create_base_result()

    # Create a mock results_dict where .get() returns None for exp_map
    mock_results_dict = Mock()
    mock_results_dict.items.return_value = [
        ("No EM", base_result),
        ("TREX", {**base_result, "difference": 10.0}),
        ("ZNE", {**base_result, "difference": 15.0}),
        ("PEC", {**base_result, "difference": 20.0}),
    ]

    # Mock the .get() chain to return None for exp_map
    mock_result_entry = Mock()
    mock_result_entry.get.return_value = None  # exp_map is None
    mock_results_dict.get.return_value = mock_result_entry

    options_list = [EstimatorOptions() for _ in range(4)]
    job_list = [mock_job] * 4

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        with pytest.raises(ValueError, match="exp_map.*does not match"):
            grade_lab4b_ex4(options_list, mock_results_dict, job_list)  # type: ignore


# ------------------------------------------------------------------------------------------------------
# Tests for _extract_qpu_usage_seconds
# ------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "metrics,expected",
    [
        # Valid metrics dict
        ({"usage": {"quantum_seconds": 123.45}}, 123.45),
        # Valid metrics callable
        (Mock(return_value={"usage": {"quantum_seconds": 67.89}}), 67.89),
        # Missing quantum_seconds key
        ({"usage": {"other_key": 123}}, None),
    ],
)
def test_extract_qpu_usage_seconds(metrics, expected) -> None:
    """Test extracting QPU usage from various metrics formats."""
    mock_job = Mock()
    if callable(metrics):
        mock_job.metrics = metrics
    else:
        mock_job.metrics = metrics

    result = _extract_qpu_usage_seconds(mock_job)
    assert result == expected


def test_extract_qpu_usage_seconds_no_metrics() -> None:
    """Test when metrics attribute is missing."""
    mock_job = Mock(spec=[])
    del mock_job.metrics
    assert _extract_qpu_usage_seconds(mock_job) is None


# ------------------------------------------------------------------------------------------------------
# Tests for grade_lab4b_exbonus
# ------------------------------------------------------------------------------------------------------


def _create_bonus_result(set0, set1, exp_map):
    """Helper to create a complete bonus result dict with all required fields."""
    return {
        "loss": np.float64(0.0),
        "par0": list(range(len(set0))),
        "par1": list(range(len(set0), len(set0) + len(set1))),
        "par0_size": len(set0),
        "par1_size": len(set1),
        "best_cut": np.float64(1.0),
        "best_index": 0,
        "set0": set0,
        "set1": set1,
        "difference": abs(sum(set0) - sum(set1)),
        "exp_map": exp_map,
    }


def _create_runtime_job(evs, qpu_seconds=100.0):
    """Helper to create a RuntimeJobV2 mock."""
    mock_job = Mock(spec=RuntimeJobV2)
    mock_job.metrics.return_value = {"usage": {"quantum_seconds": qpu_seconds}}
    mock_job.job_id.return_value = "test-job-id"

    mock_pub_result = Mock()
    mock_data = Mock()
    mock_data.evs = evs
    mock_pub_result.data = mock_data
    mock_job.result.return_value = [mock_pub_result]

    return mock_job


def test_grade_lab4b_exbonus_correct_bit_reconstruction() -> None:
    """Test that correct bit reconstruction passes validation."""
    mock_job = _create_runtime_job([1.0, 2.0, 3.0])

    numbers_bonus = [10, 20, 30, 40, 50]
    best_bits = [1, 0, 1, 0, 1]  # set0=[10,30,50], set1=[20,40]

    result_bonus = _create_bonus_result(
        [10, 30, 50],
        [20, 40],
        {0: np.float64(1.0), 1: np.float64(2.0), 2: np.float64(3.0)},
    )

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_incorrect_bit_reconstruction() -> None:
    """Test that incorrect bit reconstruction raises ValueError."""
    mock_job = _create_runtime_job([1.0, 2.0])

    numbers_bonus = [10, 20, 30, 40]
    best_bits = [1, 0, 1, 0]  # Would give set0=[10,30], set1=[20,40]

    result_bonus = _create_bonus_result(
        [10, 40],  # Wrong! Should be [10, 30]
        [20, 30],  # Wrong! Should be [20, 40]
        {0: np.float64(1.0), 1: np.float64(2.0)},
    )

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        with pytest.raises(
            ValueError, match="best_bits does not reconstruct set0 and set1"
        ):
            grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_empty_sets() -> None:
    """Test with empty sets (all bits same value)."""
    mock_job = _create_runtime_job([1.0], qpu_seconds=50.0)

    numbers_bonus = [10, 20, 30]
    best_bits = [0, 0, 0]  # All in set1

    result_bonus = _create_bonus_result([], [10, 20, 30], {0: np.float64(1.0)})

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_not_runtime_job() -> None:
    """Test that non-RuntimeJobV2 raises ValueError."""
    mock_job = Mock(spec=LocalRuntimeJob)

    numbers_bonus = [10, 20]
    best_bits = [1, 0]

    result_bonus = _create_bonus_result([10], [20], {0: np.float64(1.0)})

    with pytest.raises(ValueError, match="not a RuntimeJobV2 instance"):
        grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_zero_qpu_usage() -> None:
    """Test that zero QPU usage raises ValueError."""
    mock_job = _create_runtime_job([1.0], qpu_seconds=0.0)

    numbers_bonus = [10, 20]
    best_bits = [1, 0]

    result_bonus = _create_bonus_result([10], [20], {0: np.float64(1.0)})

    with pytest.raises(ValueError, match="QPU usage greater than 0"):
        grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_exp_map_mismatch() -> None:
    """Test that mismatched exp_map raises ValueError."""
    mock_job = _create_runtime_job([1.0, 2.0])

    numbers_bonus = [10, 20]
    best_bits = [1, 0]

    result_bonus = _create_bonus_result(
        [10],
        [20],
        {0: np.float64(999.0), 1: np.float64(888.0)},  # Mismatched
    )

    with pytest.raises(ValueError, match="exp_map.*does not match"):
        grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_mismatched_lengths() -> None:
    """Test that mismatched lengths between best_bits and numbers_bonus causes IndexError."""
    mock_job = _create_runtime_job([1.0])

    numbers_bonus = [10, 20, 30]
    best_bits = [1, 0]  # Too short!

    result_bonus = _create_bonus_result([10], [20], {0: np.float64(1.0)})

    with patch("qc_grader.challenges.qgss_2026.lab4b.grade_answer"):
        with pytest.raises(IndexError):
            grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)


def test_grade_lab4b_exbonus_missing_required_field() -> None:
    """Test that passing result_bonus missing required field raises TypeCheckError."""
    from typeguard import TypeCheckError

    mock_job = _create_runtime_job([1.0])

    numbers_bonus = [10, 20]
    best_bits = [1, 0]

    # Create a dict that's missing the required 'exp_map' field
    result_bonus = {
        "loss": np.float64(0.0),
        "par0": [0],
        "par1": [1],
        "par0_size": 1,
        "par1_size": 1,
        "best_cut": np.float64(1.0),
        "best_index": 0,
        "set0": [10],
        "set1": [20],
        "difference": 10,
        # Missing 'exp_map' field
    }

    with pytest.raises(TypeCheckError, match='is missing required key.*"exp_map"'):
        grade_lab4b_exbonus(result_bonus, best_bits, numbers_bonus, mock_job)  # type: ignore
