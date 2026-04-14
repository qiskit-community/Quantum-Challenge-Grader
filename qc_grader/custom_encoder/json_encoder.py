#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


import json
import numpy

from networkx.classes import Graph
from fractions import Fraction
from typing import Any

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import SamplerResult, EstimatorResult, PrimitiveResult
from qiskit.quantum_info import Operator, Pauli, SparsePauliOp, Statevector
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit_aer.noise import NoiseModel

from . import serializer


def to_json(obj: Any, **kwargs) -> str:
    return json.dumps(obj, skipkeys=True, cls=GraderJSONEncoder, **kwargs)


class GraderJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        match type(o).__name__:
            case numpy.integer.__name__:
                return serializer.dump_numpy_integer(o)
            case numpy.floating.__name__:
                return serializer.dump_numpy_floating(o)
            case numpy.bool_.__name__:
                return serializer.dump_numpy_bool(o)
            case numpy.ndarray.__name__:
                return serializer.dump_numpy_ndarray(o)
            case numpy.complex128.__name__:
                return serializer.dump_numpy_complex(o)
            case complex.__name__:
                return serializer.dump_complex(o)
            case Fraction.__name__:
                return serializer.dump_fraction(o)
            case Parameter.__name__:
                return serializer.dump_parameter(o)
            case TwoLocal.__name__:
                return serializer.dump_two_local(o)
            case QuantumCircuit.__name__:
                return serializer.dump_quantum_circuit(o)
            case SamplerResult.__name__:
                return serializer.dump_sampler_result(o)
            case EstimatorResult.__name__:
                return serializer.dump_estimator_result(o)
            case PrimitiveResult.__name__:
                return serializer.dump_primitive_result(o)
            case QuasiDistribution.__name__:
                return serializer.dump_quasi_distribution(o)
            case ProbDistribution.__name__:
                return serializer.dump_prob_distribution(o)
            case Statevector.__name__:
                return serializer.dump_state_vector(o)
            case Operator.__name__:
                return serializer.dump_operator(o)
            case SparsePauliOp.__name__:
                return serializer.dump_sparse_pauli_op(o)
            case NoiseModel.__name__:
                return serializer.dump_noise_model(o)
            case Pauli.__name__:
                return serializer.dump_pauli(o)
            case Graph.__name__:
                return serializer.dump_graph(o)
            case "dict_keys":
                return serializer.dump_dict_keys(o)
            case _:
                return json.JSONEncoder.default(self, o)
