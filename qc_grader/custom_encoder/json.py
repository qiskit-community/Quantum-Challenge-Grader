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
from qiskit.qobj import PulseQobj, QasmQobj
from qiskit.quantum_info import Operator, SparsePauliOp, Statevector
from qiskit.quantum_info.operators import Pauli as PauliOp
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit_aer.jobs import AerJob
from qiskit_aer.noise import NoiseModel
from qiskit_algorithms.minimum_eigensolvers.vqe import VQEResult
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob
# from qiskit_optimization.problems import QuadraticProgram

from qc_grader.custom_encoder import serializer


class GraderJSONEncoder(json.JSONEncoder):

    def __init__(
        self,
        parameter_binds=None,
        byte_string=False,
        **kwargs
    ):
        super(GraderJSONEncoder, self).__init__(**kwargs)
        self.byte_string = byte_string
        self.parameter_binds = parameter_binds


    def default(self, obj: Any) -> Any:
        byte_string = self.byte_string
        parameter_binds = self.parameter_binds

        if isinstance(obj, numpy.integer):
            return {'__class__': 'np.integer', 'int': int(obj)}
        elif isinstance(obj, numpy.floating):
            return {'__class__': 'np.floating', 'float': float(obj)}
        elif isinstance(obj, numpy.ndarray):
            return {'__class__': 'np.ndarray', 'list': obj.tolist()}
        elif isinstance(obj, complex):
            return {'__class__': 'complex', 're': obj.real, 'im': obj.imag}
        elif isinstance(obj, Fraction):
            return {'__class__': 'Fraction', 'numerator': obj.numerator, 'denominator': obj.denominator}
        elif isinstance(obj, Parameter):
            return {'__class__': 'Parameter', 'name': obj.name, 'uuid': str(obj._uuid)}
        elif isinstance(obj, QuantumCircuit):
            circuit = serializer.circuit_to_json(obj, byte_string=byte_string, parameter_binds=parameter_binds)
            circuit['__class__'] = 'QuantumCircuit'
            return circuit
        elif isinstance(obj, SamplerResult):
            sampler_result = serializer.samplerresult_to_json(obj)
            sampler_result['__class__'] = 'SamplerResult'
            return sampler_result
        elif isinstance(obj, EstimatorResult):
            estimator_result = serializer.estimatorresult_to_json(obj)
            estimator_result['__class__'] = 'EstimatorResult'
            return estimator_result
        elif isinstance(obj, TwoLocal):
            circuit = serializer.circuit_to_json(obj)
            circuit['__class__'] = 'TwoLocal'
            return circuit
        elif isinstance(obj, QuasiDistribution):
            quasi_distribution = serializer.quasidistribution_to_json(obj)
            quasi_distribution['__class__'] = 'QuasiDistribution'
            return quasi_distribution
        elif isinstance(obj, ProbDistribution):
            prob_distribution = serializer.probdistribution_to_json(obj)
            prob_distribution['__class__'] = 'ProbDistribution'
            return prob_distribution
        elif isinstance(obj, VQEResult):
            vqe_result = serializer.vqeresult_to_json(obj)
            vqe_result['__class__'] = 'VQEResult'
            return vqe_result
        elif isinstance(obj, NoiseModel):
            noise_model = obj.to_dict()
            noise_model['__class__'] = 'NoiseModel'
            return noise_model
        elif isinstance(obj, Statevector):
            return {'__class__': 'Statevector', 'data': obj.data}
        elif isinstance(obj, Operator):
            return {'__class__': 'Operator', 'data': obj.data}
        elif isinstance(obj, SparsePauliOp):
            return {'__class__': 'SparsePauliOp', 'op': obj.to_list()}
        elif isinstance(obj, NoiseModel):
            return {'__class__': 'NoiseModel', 'model': obj.to_dict()}
        # elif isinstance(obj, QuadraticProgram):
        #     return {'__class__': 'QuadraticProgram', 'qp': obj.export_as_lp_string()}
        elif isinstance(obj, IBMQJob):
            job_data = serializer.serialize_job(obj)
            if job_data is not None:
                job_data['__class__'] = 'IBMQJob'
            return job_data
        elif isinstance(obj, AerJob):
            aer_job_result = serializer.serialize_aerjob_result(obj)
            if aer_job_result is not None:
                aer_job_result['__class__'] = 'AerJob'
            return aer_job_result
        elif isinstance(obj, PauliOp):
            pauli_op = serializer.pauliop_to_json(obj)
            pauli_op['__class__'] = 'PauliOp'
            return pauli_op
        elif isinstance(obj, SparsePauliOp):
            return {'__class__': 'SparsePauliOp', 'op': obj.to_list()}
        elif isinstance(obj, PulseQobj):
            return {'__class__': 'PulseQobj', 'op': obj.to_dict()}
        elif isinstance(obj, QasmQobj):
            return {'__class__': 'QasmQobj', 'op': obj.to_dict()}
        elif isinstance(obj, Graph):
            g = serializer.graph_to_json(obj)
            g['__class__'] = 'Graph'
            return g


        return json.JSONEncoder.default(self, obj)
