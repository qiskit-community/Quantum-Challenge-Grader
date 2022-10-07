#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2022
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from functools import wraps
import json
import logging

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import warnings

from qiskit import IBMQ, QuantumCircuit
from qiskit.circuit import Barrier, Gate, Instruction, Measure, Parameter
from qiskit.circuit.library import UGate, U3Gate, CXGate
from qiskit.opflow.primitive_ops.pauli_op import PauliOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.ibmq import AccountProvider, IBMQProviderError
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.qobj import PulseQobj, QasmQobj
from qiskit.primitives import SamplerResult, EstimatorResult

ValidationResult = Tuple[bool, Optional[Union[str, int, float]]]


class MaxContentError(BaseException):
    def __init__(self, content_length: int, max_content_length: int) -> None:
        self.message = f'Max content length ({max_content_length}) exceeded: {content_length}'

    def __str__(self) -> str:
        return self.message


class QObjEncoder(json.encoder.JSONEncoder):
    def default(self, obj: Any) -> Any:
        import numpy as np

        if isinstance(obj, np.ndarray):
            return {'__class__': 'ndarray', 'list': obj.tolist()}
        if isinstance(obj, complex):
            return {'__class__': 'complex', 're': obj.real, 'im': obj.imag}

        return json.JSONEncoder.default(self, obj)


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
    qc: QuantumCircuit,
    parameter_binds: Optional[List] = None,
    byte_string: bool = False
) -> str:
    if byte_string:
        import pickle
        return json.dumps({
            'qc': pickle.dumps(qc).decode('ISO-8859-1')
        }, cls=QObjEncoder)
    else:
        return json.dumps(circuit_to_dict(qc, parameter_binds), cls=QObjEncoder)


def qobj_to_json(qobj: Union[PulseQobj, QasmQobj]) -> str:
    return json.dumps(qobj.to_dict(), cls=QObjEncoder)


def paulisumop_to_json(op: PauliSumOp) -> str:
    return json.dumps(op.primitive.to_list(), cls=QObjEncoder)


def pauliop_to_json(op: PauliOp) -> str:
    return json.dumps({
        'primitive': op.primitive.to_label(),
        'coeff': op.coeff
    }, cls=QObjEncoder)


def noisemodel_to_json(noise_model: NoiseModel) -> str:
    return json.dumps(noise_model.to_dict(), cls=QObjEncoder)


def EstimatorResult_to_json(op: EstimatorResult) ->str:
    return json.dumps({
        'values':op.values,
        'metadata':op.metadata
    },cls=QObjEncoder)

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


def cached(key_function: Callable) -> Callable:
    def _decorator(f: Any) -> Callable:
        f.__cache = {}
        @wraps(f)
        def _decorated(*args: Any, **kwargs: Any) -> int:
            key = key_function(*args, **kwargs)
            if key not in f.__cache:
                f.__cache[key] = f(*args, **kwargs)
            return f.__cache[key]
        return _decorated
    return _decorator


def gate_key(gate: Gate) -> Tuple[str, int]:
    return gate.name, gate.num_qubits


@cached(gate_key)
def gate_cost(gate: Gate) -> int:
    if isinstance(gate, (UGate, U3Gate)):
        return 1
    elif isinstance(gate, CXGate):
        return 10
    elif isinstance(gate, (Measure, Barrier)):
        return 0
    return sum(map(gate_cost, (g for g, _, _ in gate.definition.data)))


def compute_cost(circuit: Union[Instruction, QuantumCircuit]) -> int:
    print('Computing cost...')
    circuit_data = None
    if isinstance(circuit, QuantumCircuit):
        circuit_data = circuit.data
    elif isinstance(circuit, Instruction):
        circuit_data = circuit.definition.data
    else:
        raise Exception(f'Unable to obtain circuit data from {type(circuit)}')

    return sum(map(gate_cost, (g for g, _, _ in circuit_data)))


def uses_multiqubit_gate(circuit: QuantumCircuit) -> bool:
    circuit_data = None
    if isinstance(circuit, QuantumCircuit):
        circuit_data = circuit.data
    elif isinstance(circuit, Instruction) and circuit.definition is not None:
        circuit_data = circuit.definition.data
    else:
        raise Exception(f'Unable to obtain circuit data from {type(circuit)}')

    for g, _, _ in circuit_data:
        if isinstance(g, (Barrier, Measure)):
            continue
        elif isinstance(g, Gate):
            if g.num_qubits > 1:
                return True
        elif isinstance(g, (QuantumCircuit, Instruction)) and uses_multiqubit_gate(g):
            return True

    return False


def calc_depth(qc: QuantumCircuit) -> Tuple[int, int]:
    from qiskit.compiler import transpile

    tqc = transpile(
        qc, basis_gates=['u1', 'u2', 'u3', 'cx'], optimization_level=0
    )
    num_ops = tqc.count_ops()
    depth = tqc.depth()
    return depth, num_ops


def get_provider(
    hub: Optional[str] = None,
    group: Optional[str] = None,
    project: Optional[str] = None,
    load_account_fallback: Optional[bool] = True
) -> AccountProvider:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        ibmq_logger = logging.getLogger('qiskit.providers.ibmq')
        current_level = ibmq_logger.level
        ibmq_logger.setLevel(logging.ERROR)

        provider = None

        # get providers
        if hub or group or project:
            try:
                providers = IBMQ.providers()
            except IBMQProviderError:
                IBMQ.load_account()
                providers = IBMQ.providers()

            # get correct provider
            for p in providers:
                if (
                    (hub in p.credentials.hub if hub else True)
                    and (group in p.credentials.group if group else True)
                    and (project in p.credentials.project if project else True)
                ):
                    # correct provider found
                    provider = p
                    break

        # handle no correct provider found
        if provider is None and load_account_fallback:
            provider = IBMQ.load_account()

        ibmq_logger.setLevel(current_level)
        return provider


def get_job(
    job_id: str,
    hub: Optional[str] = None,
    group: Optional[str] = None,
    project: Optional[str] = None,
    load_account_fallback: Optional[bool] = True
) -> Optional[IBMQJob]:
    try:
        provider = get_provider(hub, group, project, load_account_fallback)
        job = provider.backends.retrieve_job(job_id)
        return job
    except Exception:
        pass

    return None


def get_job_urls(
    job: Union[str, IBMQJob],
    hub: Optional[str] = None,
    group: Optional[str] = None,
    project: Optional[str] = None,
    load_account_fallback: Optional[bool] = True
) -> Tuple[Optional[str], Optional[str]]:
    try:
        job_id = job.job_id() if isinstance(job, IBMQJob) else job
        provider = get_provider(hub, group, project, load_account_fallback)
        download_url = provider._api_client.account_api.job(job_id).download_url()['url']
        result_url = provider._api_client.account_api.job(job_id).result_url()['url']
        return download_url, result_url
    except Exception:
        return None, None


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


def serialize_answer(answer: Any, **kwargs: bool) -> Optional[str]:
    if isinstance(answer, IBMQJob):
        payload = serialize_job(answer)
    elif isinstance(answer, QuantumCircuit):
        payload = circuit_to_json(answer, **kwargs)
    elif isinstance(answer, PauliSumOp):
        payload = paulisumop_to_json(answer)
    elif isinstance(answer, PauliOp):
        payload = pauliop_to_json(answer)
    elif isinstance(answer, (PulseQobj, QasmQobj)):
        payload = qobj_to_json(answer)
    elif isinstance(answer, (complex, float, int)):
        payload = str(answer)
    elif isinstance(answer, EstimatorResult):
        payload=EstimatorResult_to_json(answer)
    elif isinstance(answer, str):
        payload = answer
    else:
        payload = json.dumps(answer, skipkeys=True, cls=QObjEncoder)

    return payload


def normalize_slash(url: str) -> str:
    if url[-1] != '/':
        url += '/'

    return url
