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

import inspect
import json

from fractions import Fraction
from typing import Any, Dict, List, Optional, Union

from networkx.classes import Graph

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.qobj import PulseQobj, QasmQobj
from qiskit.quantum_info import SparsePauliOp
from qiskit.quantum_info.operators import Pauli as PauliOp
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit_aer.jobs import AerJob
from qiskit_aer.noise import NoiseModel
from qiskit_algorithms.minimum_eigensolvers.vqe import VQEResult
from qiskit_algorithms.optimizers import OptimizerResult
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob

from qc_grader.common import get_job_urls


class QObjEncoder(json.encoder.JSONEncoder):
    def default(self, obj: Any) -> Any:
        import numpy as np

        if isinstance(obj, np.integer):
            return {'__class__': 'np.integer', 'int': int(obj)}
        if isinstance(obj, np.floating):
            return {'__class__': 'np.floating', 'float': float(obj)}
        if isinstance(obj, np.ndarray):
            return {'__class__': 'np.ndarray', 'list': obj.tolist()}
        if isinstance(obj, complex):
            return {'__class__': 'complex', 're': obj.real, 'im': obj.imag}
        if isinstance(obj, Fraction):
            return {'__class__': 'Fraction', 'numerator': obj.numerator, 'denominator': obj.denominator}
        if isinstance(obj, Parameter):
            return {'__class__': 'Parameter', 'name': obj.name, 'uuid': str(obj._uuid)}

        return json.JSONEncoder.default(self, obj)


def to_json(result: Any, skip: List[str] = []) -> str:
    if result is None:
        return ''
    as_dict = {}
    import inspect
    for name, value in inspect.getmembers(result):
        if not name.startswith('_') and name not in skip and \
                not inspect.ismethod(value) and not inspect.isfunction(value):
            as_dict[name] = value

    return json.dumps(as_dict, cls=QObjEncoder)


def circuit_to_dict(
    qc: QuantumCircuit,
    parameter_binds: Optional[List[Dict[Parameter, float]]] = None
) -> Dict[str, Any]:
    from qiskit import assemble
    if not parameter_binds:
        qobj = assemble(qc)
    else:
        qobj = assemble(qc, parameter_binds=parameter_binds)
    return qobj.to_dict()


def circuit_to_json(
    qc: Union[TwoLocal, QuantumCircuit],
    parameter_binds: Optional[List] = None,
    byte_string: bool = False
) -> str:
    if not byte_string and not isinstance(qc, TwoLocal) and (qc.num_parameters == 0 or parameter_binds is not None):
        circuit = circuit_to_dict(qc, parameter_binds)
        byte_string = False
    else:
        import pickle
        circuit = pickle.dumps(qc).decode('ISO-8859-1')
        byte_string = True

    return json.dumps({
        'qc': circuit,
        'byte_string': byte_string
    }, cls=QObjEncoder)


def qobj_to_json(qobj: Union[PulseQobj, QasmQobj]) -> str:
    return json.dumps(qobj.to_dict(), cls=QObjEncoder)


def sparsepauliop_to_json(op: SparsePauliOp) -> str:
    return json.dumps(op.to_list(), cls=QObjEncoder)


def pauliop_to_json(op: PauliOp) -> str:
    return json.dumps({
        'primitive': op.primitive.to_label(),
        'coeff': op.coeff
    }, cls=QObjEncoder)


def noisemodel_to_json(noise_model: NoiseModel) -> str:
    return json.dumps(noise_model.to_dict(), cls=QObjEncoder)


def optimizerresult_to_json(
    op: OptimizerResult
) -> str:
    result = {}
    for name, value in inspect.getmembers(op):
        if (
            not name.startswith('_')
            and not inspect.ismethod(value)
            and not inspect.isfunction(value)
            and hasattr(op, name)
        ):
            result[name] = value
    return json.dumps(result, cls=QObjEncoder)


def quasidistribution_to_json(
    op: QuasiDistribution
) -> str:
    return json.dumps({
        'data': str(op),
        'shots': op.shots if hasattr(op, 'shots') else None,
        'stddev_upper_bound': op.stddev_upper_bound if hasattr(op, 'stddev_upper_bound') else None
    }, cls=QObjEncoder)


def samplerresult_to_json(
    op: SamplerResult
) -> str:
    return json.dumps({
        'metadata': op.metadata,
        'quasi_dists': [quasidistribution_to_json(d) for d in op.quasi_dists]
    }, cls=QObjEncoder)


def graph_to_json(
    g: Graph
) -> str:
    return json.dumps({
        'nodes': list(g.nodes(data=True)),
        'edges': list(g.edges(data=True))
    }, cls=QObjEncoder)


def estimatorresult_to_json(
    op: EstimatorResult
) -> str:
    return json.dumps({
        'metadata': op.metadata,
        'values': op.values
    }, cls=QObjEncoder)


def probdistribution_to_json(
    op: ProbDistribution
) -> str:
    return json.dumps({
        'data': str(op),
        'shots': op.shots,
    }, cls=QObjEncoder)


def vqeresult_to_json(
    result: VQEResult
) -> str:
    return json.dumps({
        'eigenvalue': result.eigenvalue
        # TODO: figure out what other parmeters need to be included
    }, cls=QObjEncoder)


def serialize_job(job: IBMQJob) -> Optional[Dict[str, str]]:
    from qiskit.providers import JobStatus

    job_status = job.status()

    if job_status in [JobStatus.CANCELLED, JobStatus.ERROR]:
        print(f'Job did not successfully complete: {job_status.value}.')
        return None
    elif job_status is not JobStatus.DONE:
        print(f'Job has not yet completed: {job_status.value}.')
        print(f'Please wait for the job (id: {job.job_id()}) to complete then try again.')
        return None

    download_url, result_url = get_job_urls(job)

    if not download_url or not result_url:
        print('Unable to obtain job URLs')
        return None

    return json.dumps({
        'download_url': download_url,
        'result_url': result_url
    })


def serialize_aerjob_result(job: AerJob) -> Optional[Dict[str, str]]:
    from qiskit.providers import JobStatus

    job_status = job.status()

    if job_status in [JobStatus.CANCELLED, JobStatus.ERROR]:
        print(f'Job did not successfully complete: {job_status.value}.')
        return None
    elif job_status is not JobStatus.DONE:
        print(f'Job has not yet completed: {job_status.value}.')
        print(f'Please wait for the job (id: {job.job_id()}) to complete then try again.')
        return None

    return json.dumps(job.result().to_dict())


def serialize_answer(answer: Any, **kwargs: bool) -> Optional[str]:
    if isinstance(answer, IBMQJob):
        payload = serialize_job(answer)
    elif isinstance(answer, AerJob):
        payload = serialize_aerjob_result(answer)
    elif isinstance(answer, QuantumCircuit):
        payload = circuit_to_json(answer, **kwargs)
    elif isinstance(answer, PauliOp):
        payload = pauliop_to_json(answer)
    elif isinstance(answer, SparsePauliOp):
        payload = sparsepauliop_to_json(answer)
    elif isinstance(answer, (PulseQobj, QasmQobj)):
        payload = qobj_to_json(answer)
    elif isinstance(answer, SamplerResult):
        payload = samplerresult_to_json(answer)
    elif isinstance(answer, EstimatorResult):
        payload = estimatorresult_to_json(answer)
    elif isinstance(answer, Graph):
        payload = graph_to_json(answer)
    elif isinstance(answer, QuasiDistribution):
        payload = quasidistribution_to_json(answer)
    elif isinstance(answer, ProbDistribution):
        payload = probdistribution_to_json(answer)
    elif isinstance(answer, VQEResult):
        payload = vqeresult_to_json(answer)
    elif isinstance(answer, NoiseModel):
        payload = noisemodel_to_json(answer)
    elif isinstance(answer, TwoLocal):
        payload = circuit_to_json(answer)
    elif isinstance(answer, (complex, float, int)):
        payload = str(answer)
    elif isinstance(answer, str):
        payload = answer
    else:
        payload = json.dumps(answer, skipkeys=True, cls=QObjEncoder)

    return payload
