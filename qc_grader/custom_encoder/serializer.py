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


from typing import Any, Dict, List, Optional, Union

from networkx.classes import Graph

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.quantum_info.operators import Pauli as PauliOp
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit_aer.jobs import AerJob
from qiskit_algorithms.minimum_eigensolvers.vqe import VQEResult
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob

from qc_grader.grader.common import get_job_urls


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
) -> dict:
    if not byte_string and not isinstance(qc, TwoLocal) and (qc.num_parameters == 0 or parameter_binds is not None):
        circuit = circuit_to_dict(qc, parameter_binds)
        byte_string = False
    else:
        import pickle
        circuit = pickle.dumps(qc).decode('ISO-8859-1')
        byte_string = True

    return {
        'qc': circuit,
        'byte_string': byte_string
    }


def pauliop_to_json(op: PauliOp) -> str:
    return {
        'primitive': op.primitive.to_label(),
        'coeff': op.coeff
    }


def quasidistribution_to_json(
    op: QuasiDistribution
) -> str:
    return {
        'data': str(op),
        'shots': op.shots if hasattr(op, 'shots') else None,
        'stddev_upper_bound': op.stddev_upper_bound if hasattr(op, 'stddev_upper_bound') else None
    }


def samplerresult_to_json(
    op: SamplerResult
) -> str:
    return {
        'metadata': op.metadata,
        'quasi_dists': [quasidistribution_to_json(d) for d in op.quasi_dists]
    }


def graph_to_json(
    g: Graph
) -> str:
    return {
        'nodes': list(g.nodes(data=True)),
        'edges': list(g.edges(data=True))
    }


def estimatorresult_to_json(
    op: EstimatorResult
) -> str:
    return {
        'metadata': op.metadata,
        'values': op.values
    }


def probdistribution_to_json(
    op: ProbDistribution
) -> str:
    return {
        'data': str(op),
        'shots': op.shots,
    }


def vqeresult_to_json(
    result: VQEResult
) -> str:
    return {
        'eigenvalue': result.eigenvalue
        # TODO: figure out what other parmeters need to be included
    }


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

    return {
        'download_url': download_url,
        'result_url': result_url
    }


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

    return job.result().to_dict()
