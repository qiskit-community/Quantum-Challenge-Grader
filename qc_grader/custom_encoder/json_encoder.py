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
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.qobj import PulseQobj
from qiskit.quantum_info import Operator, SparsePauliOp, Statevector
from qiskit.quantum_info.operators import Pauli as PauliOp
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit_aer.noise import NoiseModel
from qiskit_algorithms.minimum_eigensolvers.vqe import VQEResult

from . import serializer


def to_json(obj: Any, **kwargs) -> str:
    return json.dumps(obj, skipkeys=True, cls=GraderJSONEncoder, **kwargs)


class GraderJSONEncoder(json.JSONEncoder):

    def __init__(
        self,
        byte_string=False,
        **kwargs
    ):
        super(GraderJSONEncoder, self).__init__(**kwargs)
        self.byte_string = byte_string


    def default(self, obj: Any) -> Any:
        if self.byte_string:
            _json = serializer.serialize_object(obj)
            _json['__class__'] = type(obj).__name__
            return _json

        if isinstance(obj, numpy.integer):
            return serializer.dump_np_int(obj)
        elif isinstance(obj, numpy.floating):
            return serializer.dump_np_floating(obj)
        elif isinstance(obj, numpy.ndarray):
            return serializer.dump_np_ndarray(obj)
        elif isinstance(obj, complex):
            return serializer.dump_complex(obj)
        elif isinstance(obj, Fraction):
            return serializer.dump_fraction(obj)
        elif isinstance(obj, Parameter):
            return serializer.dump_parameter(obj)
        elif isinstance(obj, TwoLocal):
            return serializer.dump_two_local(obj)
        elif isinstance(obj, QuantumCircuit):
            return serializer.dump_quantum_circuit(obj)
        elif isinstance(obj, SamplerResult):
            return serializer.dump_sampler_result(obj)
        elif isinstance(obj, EstimatorResult):
            return serializer.dump_estimator_result(obj)
        elif isinstance(obj, QuasiDistribution):
            return serializer.dump_quasi_distribution(obj)
        elif isinstance(obj, ProbDistribution):
            return serializer.dump_prob_distribution(obj)
        elif isinstance(obj, VQEResult):
            return serializer.dump_vqe_result(obj)
        elif isinstance(obj, Statevector):
            return serializer.dump_state_vector(obj)
        elif isinstance(obj, Operator):
            return serializer.dump_operator(obj)
        elif isinstance(obj, SparsePauliOp):
            return serializer.dump_sparse_pauli_op(obj)
        elif isinstance(obj, NoiseModel):
            return serializer.dump_noise_model(obj)
        elif isinstance(obj, PauliOp):
            return serializer.dump_pauli_op(obj)
        elif isinstance(obj, PulseQobj):
            return serializer.dump_pulse_qobj(obj)
        elif isinstance(obj, Graph):
            return serializer.dump_graph(obj)

        return json.JSONEncoder.default(self, obj)
