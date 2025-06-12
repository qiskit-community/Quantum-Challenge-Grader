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
# from qiskit_algorithms.minimum_eigensolvers.vqe import VQEResult

from . import serializer


def to_json(obj: Any, **kwargs) -> str:
    return json.dumps(obj, skipkeys=True, cls=GraderJSONEncoder, **kwargs)


class GraderJSONEncoder(json.JSONEncoder):

    def __init__(
        self,
        to_bytes=False,
        **kwargs
    ):
        super(GraderJSONEncoder, self).__init__(**kwargs)
        self.to_bytes = to_bytes

    def default(self, obj: Any) -> Any:
        if self.to_bytes:
            _json = serializer.serialize_object(obj)
            _json['__class__'] = type(obj).__name__
            return _json

        match type(obj).__name__:
            case numpy.integer.__name__:
                return serializer.dump_numpy_integer(obj)
            case numpy.floating.__name__:
                return serializer.dump_numpy_floating(obj)
            case numpy.bool_.__name__:
                return serializer.dump_numpy_bool(obj)
            case numpy.ndarray.__name__:
                return serializer.dump_numpy_ndarray(obj)
            case numpy.complex128.__name__:
                return serializer.dump_numpy_complex(obj)
            case complex.__name__:
                return serializer.dump_complex(obj)
            case Fraction.__name__:
                return serializer.dump_fraction(obj)
            case Parameter.__name__:
                return serializer.dump_parameter(obj)
            case TwoLocal.__name__:
                return serializer.dump_two_local(obj)
            case QuantumCircuit.__name__:
                return serializer.dump_quantum_circuit(obj)
            case SamplerResult.__name__:
                return serializer.dump_sampler_result(obj)
            case EstimatorResult.__name__:
                return serializer.dump_estimator_result(obj)
            case PrimitiveResult.__name__:
                return serializer.dump_primitive_result(obj)
            case QuasiDistribution.__name__:
                return serializer.dump_quasi_distribution(obj)
            case ProbDistribution.__name__:
                return serializer.dump_prob_distribution(obj)
            # case VQEResult.__name__:
            #     return serializer.dump_vqe_result(obj)
            case Statevector.__name__:
                return serializer.dump_state_vector(obj)
            case Operator.__name__:
                return serializer.dump_operator(obj)
            case SparsePauliOp.__name__:
                return serializer.dump_sparse_pauli_op(obj)
            case NoiseModel.__name__:
                return serializer.dump_noise_model(obj)
            case Pauli.__name__:
                return serializer.dump_pauli(obj)
            case Graph.__name__:
                return serializer.dump_graph(obj)
            case "dict_keys":
                return serializer.dump_dict_keys(obj)
            case _:
                return json.JSONEncoder.default(self, obj)
