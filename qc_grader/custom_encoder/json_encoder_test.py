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
from fractions import Fraction

import numpy as np
import pytest
from networkx.classes import Graph
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import Operator, Pauli, SparsePauliOp, Statevector
from qiskit.result import ProbDistribution, QuasiDistribution

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


# ------------------------------------------------------------------------------------------------------
# NumPy
# ------------------------------------------------------------------------------------------------------


def test_numpy_bool() -> None:
    result = json.loads(to_json(np.bool_(True)))
    assert result == {"__class__": "numpy.bool)", "float": True}


def test_numpy_ndarray() -> None:
    result = json.loads(to_json(np.array([1.0, 2.0, 3.0])))
    assert result["__class__"] == "numpy.ndarray"
    assert "ndarray" in result


def test_numpy_complex128() -> None:
    result = json.loads(to_json(np.complex128(1 + 2j)))
    assert result == {"__class__": "numpy.complex128", "re": 1.0, "im": 2.0}


# ------------------------------------------------------------------------------------------------------
# Fractions
# ------------------------------------------------------------------------------------------------------


def test_fraction() -> None:
    result = json.loads(to_json(Fraction(3, 4)))
    assert result == {"__class__": "Fraction", "numerator": 3, "denominator": 4}


# ------------------------------------------------------------------------------------------------------
# Qiskit circuits
# ------------------------------------------------------------------------------------------------------


def test_parameter() -> None:
    p = Parameter("theta")
    result = json.loads(to_json(p))
    assert result["__class__"] == "Parameter"
    assert result["name"] == "theta"
    assert "uuid" in result


def test_quantum_circuit() -> None:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    result = json.loads(to_json(qc))
    assert result["__class__"] == "QuantumCircuit"
    assert "qc" in result


def test_two_local() -> None:
    tl = TwoLocal(2, "ry", "cx", reps=1)
    result = json.loads(to_json(tl))
    assert result["__class__"] == "TwoLocal"
    assert "qc" in result


# ------------------------------------------------------------------------------------------------------
# Qiskit quantum info
# ------------------------------------------------------------------------------------------------------


def test_statevector() -> None:
    sv = Statevector.from_label("0")
    result = json.loads(to_json(sv))
    assert result["__class__"] == "Statevector"
    assert "data" in result


def test_operator() -> None:
    op = Operator.from_label("X")
    result = json.loads(to_json(op))
    assert result["__class__"] == "Operator"
    assert "data" in result


def test_pauli() -> None:
    result = json.loads(to_json(Pauli("XYZ")))
    assert result == {"__class__": "Pauli", "label": "XYZ"}


def test_sparse_pauli_op() -> None:
    op = SparsePauliOp.from_list([("XX", 1.0), ("ZZ", -0.5)])
    result = json.loads(to_json(op))
    assert result["__class__"] == "SparsePauliOp"
    assert len(result["op"]) == 2


# ------------------------------------------------------------------------------------------------------
# Qiskit distributions
# ------------------------------------------------------------------------------------------------------


def test_quasi_distribution() -> None:
    result = json.loads(to_json(QuasiDistribution({0: 0.5, 1: 0.5})))
    assert result == {"0": 0.5, "1": 0.5}


def test_prob_distribution() -> None:
    result = json.loads(to_json(ProbDistribution({0: 0.5, 1: 0.5})))
    assert result == {"0": 0.5, "1": 0.5}


# ------------------------------------------------------------------------------------------------------
# Misc
# ------------------------------------------------------------------------------------------------------


def test_graph() -> None:
    g = Graph()
    g.add_node(1, color="red")
    g.add_edge(1, 2, weight=3.5)
    result = json.loads(to_json(g))
    assert result["__class__"] == "Graph"
    assert result["nodes"] == [[1, {"color": "red"}], [2, {}]]
    assert result["edges"] == [[1, 2, {"weight": 3.5}]]


def test_dict_keys() -> None:
    result = json.loads(to_json({"a": 1, "b": 2}.keys()))
    assert result == {"__class__": "dict_keys", "items": ["a", "b"]}


def test_unrecognized_type() -> None:
    class Unrecognized:
        pass

    with pytest.raises(TypeError, match="not JSON serializable"):
        to_json(Unrecognized())
