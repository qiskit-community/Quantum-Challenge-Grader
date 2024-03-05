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


import logging
import warnings

from functools import wraps
from typing import Any, Callable, Optional, Tuple, Union

from qiskit import QuantumCircuit
from qiskit.circuit import Barrier, Gate, Instruction, Measure
from qiskit.circuit.library import UGate, U3Gate, CXGate
from qiskit_ibm_provider import IBMProvider, IBMProviderError
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob


ValidationResult = Tuple[bool, Optional[Union[str, int, float]]]


def normalize_slash(url: str) -> str:
    return f'{url}/' if url[-1] != '/' else url


def get_provider(
    hub: Optional[str] = None,
    group: Optional[str] = None,
    project: Optional[str] = None,
    load_account_fallback: Optional[bool] = True
) -> IBMProvider:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        ibmq_logger = logging.getLogger('qiskit_ibm_provider')
        current_level = ibmq_logger.level
        ibmq_logger.setLevel(logging.ERROR)

        provider = None

        # get providers
        if hub or group or project:
            try:
                provider = IBMProvider(instance=f'{hub}/{group}/{project}')
            except IBMProviderError:
                pass

        # handle no correct provider found
        if provider is None and load_account_fallback:
            provider = IBMProvider()

        ibmq_logger.setLevel(current_level)
        return provider


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
