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

import pytest
from qiskit_ibm_runtime.options import SamplerOptions

from qc_grader.challenges.qgss_2026.lab4b import _dict_contains


# ------------------------------------------------------------------------------------------------------
# Core functionality tests
# ------------------------------------------------------------------------------------------------------


def test_dict_contains_empty_dicts():
    """Test that empty subset matches empty full dict."""
    assert _dict_contains({}, {}) is True


def test_dict_contains_empty_subset():
    """Test that empty subset matches any full dict."""
    assert _dict_contains({"a": 1, "b": 2}, {}) is True


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


def test_dict_contains_deeply_nested():
    """Test deeply nested dictionaries."""
    full = {"a": {"b": {"c": {"d": 1, "e": 2}, "f": 3}, "g": 4}}
    subset = {"a": {"b": {"c": {"d": 1}}}}
    assert _dict_contains(full, subset) is True


def test_dict_contains_type_mismatch_dict_vs_value():
    """Test when subset expects dict but full has non-dict value."""
    full = {"a": 1, "b": 2}
    subset = {"a": {"nested": "value"}}
    assert _dict_contains(full, subset) is False


# ------------------------------------------------------------------------------------------------------
# SamplerOptions: Basic configuration tests
# ------------------------------------------------------------------------------------------------------


def test_sampler_options_identical():
    """Test identical SamplerOptions configurations."""
    options1 = SamplerOptions()
    options1.default_shots = 1000

    options2 = SamplerOptions()
    options2.default_shots = 1000

    dict1 = asdict(options1)
    dict2 = asdict(options2)

    assert _dict_contains(dict1, dict2) is True


def test_sampler_options_default_shots_only():
    """Test matching only default_shots field."""
    full_options = SamplerOptions()
    full_options.default_shots = 1000

    subset_options = SamplerOptions()
    subset_options.default_shots = 1000

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    # Only check the specific field we set
    subset_dict_filtered = {"default_shots": subset_dict["default_shots"]}

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_default_shots_mismatch():
    """Test that mismatched default_shots returns False."""
    options1 = SamplerOptions()
    options1.default_shots = 1000

    options2 = SamplerOptions()
    options2.default_shots = 2000

    dict1 = asdict(options1)
    dict2 = asdict(options2)

    assert _dict_contains(dict1, dict2) is False


def test_sampler_options_subset_with_extra_fields():
    """Test that full dict can have extra fields not in subset."""
    full_options = SamplerOptions()
    full_options.default_shots = 1000
    full_options.dynamical_decoupling.enable = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.default_shots = 1000

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)
    subset_dict_filtered = {"default_shots": subset_dict["default_shots"]}

    assert _dict_contains(full_dict, subset_dict_filtered) is True


# ------------------------------------------------------------------------------------------------------
# SamplerOptions: Dynamical Decoupling tests
# ------------------------------------------------------------------------------------------------------


def test_sampler_options_dd_enable_only():
    """Test matching only dynamical_decoupling.enable."""
    full_options = SamplerOptions()
    full_options.dynamical_decoupling.enable = True  # type: ignore
    full_options.dynamical_decoupling.sequence_type = "XY4"  # type: ignore

    subset_options = SamplerOptions()
    subset_options.dynamical_decoupling.enable = True  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"]
        }
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_dd_full_config():
    """Test matching full dynamical_decoupling configuration."""
    full_options = SamplerOptions()
    full_options.dynamical_decoupling.enable = True  # type: ignore
    full_options.dynamical_decoupling.sequence_type = "XY4"  # type: ignore

    subset_options = SamplerOptions()
    subset_options.dynamical_decoupling.enable = True  # type: ignore
    subset_options.dynamical_decoupling.sequence_type = "XY4"  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"],
            "sequence_type": subset_dict["dynamical_decoupling"]["sequence_type"],
        }
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_dd_enable_mismatch():
    """Test that mismatched dynamical_decoupling.enable returns False."""
    full_options = SamplerOptions()
    full_options.dynamical_decoupling.enable = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.dynamical_decoupling.enable = False  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"]
        }
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is False


def test_sampler_options_dd_sequence_type_mismatch():
    """Test that mismatched sequence_type returns False."""
    full_options = SamplerOptions()
    full_options.dynamical_decoupling.enable = True  # type: ignore
    full_options.dynamical_decoupling.sequence_type = "XY4"  # type: ignore

    subset_options = SamplerOptions()
    subset_options.dynamical_decoupling.enable = True  # type: ignore
    subset_options.dynamical_decoupling.sequence_type = "XX"  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"],
            "sequence_type": subset_dict["dynamical_decoupling"]["sequence_type"],
        }
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is False


# ------------------------------------------------------------------------------------------------------
# SamplerOptions: Twirling tests
# ------------------------------------------------------------------------------------------------------


def test_sampler_options_twirling_gates_only():
    """Test matching only twirling.enable_gates."""
    full_options = SamplerOptions()
    full_options.twirling.enable_gates = True  # type: ignore
    full_options.twirling.enable_measure = False  # type: ignore

    subset_options = SamplerOptions()
    subset_options.twirling.enable_gates = True  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "twirling": {"enable_gates": subset_dict["twirling"]["enable_gates"]}
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_twirling_full_config():
    """Test matching full twirling configuration."""
    full_options = SamplerOptions()
    full_options.twirling.enable_gates = True  # type: ignore
    full_options.twirling.enable_measure = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.twirling.enable_gates = True  # type: ignore
    subset_options.twirling.enable_measure = True  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "twirling": {
            "enable_gates": subset_dict["twirling"]["enable_gates"],
            "enable_measure": subset_dict["twirling"]["enable_measure"],
        }
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_twirling_gates_mismatch():
    """Test that mismatched twirling.enable_gates returns False."""
    full_options = SamplerOptions()
    full_options.twirling.enable_gates = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.twirling.enable_gates = False  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "twirling": {"enable_gates": subset_dict["twirling"]["enable_gates"]}
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is False


def test_sampler_options_twirling_measure_mismatch():
    """Test that mismatched twirling.enable_measure returns False."""
    full_options = SamplerOptions()
    full_options.twirling.enable_gates = True  # type: ignore
    full_options.twirling.enable_measure = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.twirling.enable_gates = True  # type: ignore
    subset_options.twirling.enable_measure = False  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "twirling": {
            "enable_gates": subset_dict["twirling"]["enable_gates"],
            "enable_measure": subset_dict["twirling"]["enable_measure"],
        }
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is False


# ------------------------------------------------------------------------------------------------------
# SamplerOptions: Combined configuration tests
# ------------------------------------------------------------------------------------------------------


def test_sampler_options_combined_dd_and_twirling():
    """Test matching both dynamical_decoupling and twirling settings."""
    full_options = SamplerOptions()
    full_options.default_shots = 1000
    full_options.dynamical_decoupling.enable = True  # type: ignore
    full_options.dynamical_decoupling.sequence_type = "XY4"  # type: ignore
    full_options.twirling.enable_gates = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.dynamical_decoupling.enable = True  # type: ignore
    subset_options.twirling.enable_gates = True  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"]
        },
        "twirling": {"enable_gates": subset_dict["twirling"]["enable_gates"]},
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_combined_all_settings():
    """Test matching all major settings together."""
    full_options = SamplerOptions()
    full_options.default_shots = 2000
    full_options.dynamical_decoupling.enable = True  # type: ignore
    full_options.dynamical_decoupling.sequence_type = "XY4"  # type: ignore
    full_options.twirling.enable_gates = True  # type: ignore
    full_options.twirling.enable_measure = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.default_shots = 2000
    subset_options.dynamical_decoupling.enable = True  # type: ignore
    subset_options.twirling.enable_gates = True  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "default_shots": subset_dict["default_shots"],
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"]
        },
        "twirling": {"enable_gates": subset_dict["twirling"]["enable_gates"]},
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is True


def test_sampler_options_combined_partial_mismatch():
    """Test that partial mismatch in combined settings returns False."""
    full_options = SamplerOptions()
    full_options.dynamical_decoupling.enable = True  # type: ignore
    full_options.twirling.enable_gates = True  # type: ignore

    subset_options = SamplerOptions()
    subset_options.dynamical_decoupling.enable = True  # type: ignore
    subset_options.twirling.enable_gates = False  # type: ignore

    full_dict = asdict(full_options)
    subset_dict = asdict(subset_options)

    subset_dict_filtered = {
        "dynamical_decoupling": {
            "enable": subset_dict["dynamical_decoupling"]["enable"]
        },
        "twirling": {"enable_gates": subset_dict["twirling"]["enable_gates"]},
    }

    assert _dict_contains(full_dict, subset_dict_filtered) is False


# ------------------------------------------------------------------------------------------------------
# Parametrized tests for comprehensive edge cases
# ------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "full_dict,subset_dict,expected",
    [
        # Basic nested cases
        ({"a": {"b": 1}}, {"a": {"b": 1}}, True),
        ({"a": {"b": 1, "c": 2}}, {"a": {"b": 1}}, True),
        ({"a": {"b": 1}}, {"a": {"b": 2}}, False),
        ({"a": {"b": 1}}, {"a": {"c": 1}}, False),
        # Deep nesting
        ({"a": {"b": {"c": 1}}}, {"a": {"b": {"c": 1}}}, True),
        ({"a": {"b": {"c": 1, "d": 2}}}, {"a": {"b": {"c": 1}}}, True),
        ({"a": {"b": {"c": 1}}}, {"a": {"b": {"c": 2}}}, False),
        # Mixed types
        ({"a": 1, "b": {"c": 2}}, {"a": 1}, True),
        ({"a": 1, "b": {"c": 2}}, {"b": {"c": 2}}, True),
        ({"a": 1, "b": {"c": 2}}, {"a": 1, "b": {"c": 2}}, True),
    ],
)
def test_dict_contains_parametrized(
    full_dict: dict, subset_dict: dict, expected: bool
) -> None:
    """Parametrized tests for various dict comparison scenarios."""
    assert _dict_contains(full_dict, subset_dict) is expected
