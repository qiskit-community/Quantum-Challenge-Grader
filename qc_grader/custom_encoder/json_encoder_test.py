# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from fractions import Fraction
from qiskit.result.distributions.probability import ProbDistribution
from qiskit.result.distributions.quasi import QuasiDistribution
import json

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library import GR
from qiskit.quantum_info import SparsePauliOp, Statevector

from qc_grader.custom_encoder import to_json

# ------------------------------------------------------------------------------------------------------
# Std lib
# ------------------------------------------------------------------------------------------------------


def test_stdlib_primitives() -> None:
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


def test_complex() -> None:
    result = json.loads(to_json(1 + 2j))
    assert result == {"__class__": "complex", "re": 1.0, "im": 2.0}


def test_fraction() -> None:
    result = json.loads(to_json(Fraction(3, 4)))
    assert result == {"__class__": "Fraction", "numerator": 3, "denominator": 4}


def test_unrecognized_type() -> None:
    class Unrecognized:
        pass

    with pytest.raises(TypeError, match="not JSON serializable"):
        to_json(Unrecognized())


# ------------------------------------------------------------------------------------------------------
# NumPy
# ------------------------------------------------------------------------------------------------------


def test_numpy_ndarray() -> None:
    result = json.loads(to_json(np.array([1.0, 2.0, 3.0])))
    assert result["__class__"] == "numpy.ndarray"
    assert "ndarray" in result


def test_numpy_complex128() -> None:
    result = json.loads(to_json(np.complex128(1 + 2j)))
    assert result == {"__class__": "numpy.complex128", "re": 1.0, "im": 2.0}


# ------------------------------------------------------------------------------------------------------
# Qiskit
# ------------------------------------------------------------------------------------------------------


def test_quantum_circuit() -> None:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    result = json.loads(to_json(qc))
    assert result["__class__"] == "QuantumCircuit"
    assert "qc" in result


def test_quantum_circuit_subclass() -> None:
    qc = GR(2, 1, 1)
    result = json.loads(to_json(qc))
    assert result["__class__"] == "QuantumCircuit"
    assert "qc" in result


def test_statevector() -> None:
    sv = Statevector.from_label("0")
    result = json.loads(to_json(sv))
    assert result["__class__"] == "Statevector"
    assert "data" in result


def test_sparse_pauli_op() -> None:
    op = SparsePauliOp.from_list([("XX", 1.0), ("ZZ", -0.5)])
    result = json.loads(to_json(op))
    assert result["__class__"] == "SparsePauliOp"
    assert len(result["op"]) == 2


def test_quasi_distribution() -> None:
    result = json.loads(to_json(QuasiDistribution({0: 0.5, 1: 0.5})))
    assert result == {"0": 0.5, "1": 0.5}


def test_prob_distribution() -> None:
    result = json.loads(to_json(ProbDistribution({0: 0.5, 1: 0.5})))
    assert result == {"0": 0.5, "1": 0.5}
