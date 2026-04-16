# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import json

import numpy as np
import pytest

from qc_grader.custom_encoder import to_json

# ------------------------------------------------------------------------------------------------------
# Std lib
# ------------------------------------------------------------------------------------------------------


def test_stdlib_primitives():
    assert json.loads(to_json([1, "two", 3.0])) == [1, "two", 3.0]
    assert json.loads(to_json({"key": "value", "num": 42})) == {
        "key": "value",
        "num": 42,
    }
    assert json.loads(to_json("hello")) == "hello"
    assert json.loads(to_json(42)) == 42
    assert json.loads(to_json(3.14)) == pytest.approx(3.14)
    assert json.loads(to_json(True)) is True
    assert json.loads(to_json(False)) is False
    assert json.loads(to_json(None)) is None


def test_complex():
    result = json.loads(to_json(1 + 2j))
    assert result == {"__class__": "complex", "re": 1.0, "im": 2.0}


# ------------------------------------------------------------------------------------------------------
# NumPy
# ------------------------------------------------------------------------------------------------------


def test_numpy_bool():
    result = json.loads(to_json(np.bool_(True)))
    assert result == {"__class__": "numpy.bool)", "float": True}


def test_numpy_ndarray():
    result = json.loads(to_json(np.array([1.0, 2.0, 3.0])))
    assert result["__class__"] == "numpy.ndarray"
    assert "ndarray" in result


def test_numpy_complex128():
    result = json.loads(to_json(np.complex128(1 + 2j)))
    assert result == {"__class__": "numpy.complex128", "re": 1.0, "im": 2.0}
