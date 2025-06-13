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


import numpy

from fractions import Fraction
from io import BytesIO
from typing import Any, Union
from collections.abc import KeysView

from qiskit import QuantumCircuit, qpy
from qiskit.circuit import Parameter
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import SamplerResult, EstimatorResult, PrimitiveResult
from qiskit.quantum_info import Operator, Pauli, SparsePauliOp, Statevector
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit_aer.noise import NoiseModel
# from qiskit_algorithms.minimum_eigensolvers.vqe import VQEResult

from networkx.classes import Graph


def circuit_to_bytes(qc: Union[TwoLocal, QuantumCircuit]) -> dict:
    with BytesIO() as container:
        qpy.dump(qc, container)
        circuit = container.getvalue()

    return circuit


def dump_numpy_integer(obj: numpy.integer):
    return {'__class__': 'numpy.integer', 'int': int(obj)}


def dump_numpy_floating(obj: numpy.floating):
    return {'__class__': 'numpy.floating', 'float': float(obj)}


def dump_numpy_bool(obj: numpy.bool_):
    return {'__class__': 'numpy.bool)', 'float': bool(obj)}


def dump_numpy_ndarray(obj: numpy.ndarray):
    with BytesIO() as container:
        numpy.save(container, obj, allow_pickle=False)
        array = container.getvalue()
    return {'__class__': 'numpy.ndarray', 'ndarray': array.decode('ISO-8859-1')}

def dump_numpy_complex(obj: numpy.complex128):
    return {'__class__': 'numpy.complex128', 're': obj.real, 'im': obj.imag}

def dump_complex(obj: complex):
    return {'__class__': 'complex', 're': obj.real, 'im': obj.imag}


def dump_fraction(obj: Fraction):
    return {'__class__': 'Fraction', 'numerator': obj.numerator, 'denominator': obj.denominator}


def dump_parameter(obj: Parameter):
    return {'__class__': 'Parameter', 'name': obj.name, 'uuid': str(obj._uuid)}


def dump_two_local(obj: TwoLocal):
    circuit = circuit_to_bytes(obj)
    return {'__class__': 'TwoLocal', 'qc': circuit.decode('ISO-8859-1')}


def dump_quantum_circuit(obj: QuantumCircuit):
    circuit = circuit_to_bytes(obj)
    return {'__class__': 'QuantumCircuit', 'qc': circuit.decode('ISO-8859-1')}


def dump_quasi_distribution(obj: QuasiDistribution):
    return {
        '__class__': 'QuasiDistribution',
        'data': str(obj),
        'shots': obj.shots if hasattr(obj, 'shots') else None,
        'stddev_upper_bound': obj.stddev_upper_bound if hasattr(obj, 'stddev_upper_bound') else None
    }


def dump_sampler_result(obj: SamplerResult):
    return {
        '__class__': 'SamplerResult',
        'metadata': obj.metadata,
        'quasi_dists': [dump_quasi_distribution(d) for d in obj.quasi_dists]
    }


def dump_estimator_result(obj: EstimatorResult):
    return {
        '__class__': 'EstimatorResult',
        'metadata': obj.metadata,
        'values': obj.values
    }

def dump_primitive_result(obj: PrimitiveResult):
    return {
        '__class__': 'PrimitiveResult',
        'metadata': obj.metadata,
        'values': obj[0].data.evs
    }

def dump_prob_distribution(obj: ProbDistribution):
    return {
        '__class__': 'ProbDistribution',
        'data': str(obj),
        'shots': obj.shots,
    }


# def dump_vqe_result(obj: VQEResult):
#     return {
#         '__class__': 'VQEResult',
#         'eigenvalue': obj.eigenvalue
#         # TODO: figure out what other parmeters need to be included
#     }


def dump_state_vector(obj: Statevector):
    return {'__class__': 'Statevector', 'data': obj.data}


def dump_operator(obj: Operator):
    return {'__class__': 'Operator', 'data': obj.data}


def dump_pauli(obj: Pauli):
    return {
        '__class__': 'Pauli',
        'label': obj.to_label()
    }


def dump_sparse_pauli_op(obj: SparsePauliOp):
    return {'__class__': 'SparsePauliOp', 'op': obj.to_list()}


def dump_noise_model(obj: NoiseModel):
    return {'__class__': 'NoiseModel', 'model': obj.to_dict()}


def dump_graph(obj: Graph):
    return {
        '__class__': 'Graph',
        'nodes': list(obj.nodes(data=True)),
        'edges': list(obj.edges(data=True))
    }


def serialize_object(obj: Any):
    import pickle
    return {
        'obj': pickle.dumps(obj).decode('ISO-8859-1')
    }

def dump_dict_keys(obj: KeysView):
    return {'__class__': 'dict_keys', 'items': list(obj)}
