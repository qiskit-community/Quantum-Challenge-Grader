import inspect
import json
import logging
import numpy as np
import pickle
import warnings

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Union

from qiskit import IBMQ, QuantumCircuit, assemble
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.circuit import Barrier, Gate, Instruction, Measure
from qiskit.circuit.library import UGate, U3Gate, CXGate
from qiskit.compiler import transpile
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.ibmq import AccountProvider, IBMQProviderError
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.qobj import PulseQobj, QasmQobj


class QObjEncoder(json.encoder.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return { '__class__': 'ndarray', 'list': obj.tolist() }
        if isinstance(obj, complex):
            return { '__class__': 'complex', 're': obj.real, 'im': obj.imag }
        return json.JSONEncoder.default(self, obj)


def get_challenge_provider() -> AccountProvider:
    provider = get_provider()
    if (
        "iqc-fall-21" in provider.credentials.hub
        and "challenge" in provider.credentials.group
    ):
        # correct provider found
        return provider
    else:
        print('You have been not assigned to a challenge provider yet.',
              'Note that you need to pass at least one exercise,',
              'and it may take up to 12 hours to get assigned.',
              'Meanwhile, please proceed to other exercises and try again later.')
        return None


def get_provider() -> AccountProvider:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        ibmq_logger = logging.getLogger('qiskit.providers.ibmq')
        current_level = ibmq_logger.level
        ibmq_logger.setLevel(logging.ERROR)

        # get providers
        try:
            providers = IBMQ.providers()
        except IBMQProviderError:
            IBMQ.load_account()
            providers = IBMQ.providers()

        # get correct provider
        provider = None
        for p in providers:
            if (
                "iqc-fall-21" in p.credentials.hub
                and "challenge" in p.credentials.group
                #and "ex1" in p.credentials.project
            ):
                # correct provider found
                provider = p

        # handle no correct provider found
        if provider == None:
            provider = IBMQ.load_account()

        ibmq_logger.setLevel(current_level)
        return provider


def get_job(job_id: str) -> Optional[IBMQJob]:
    try:
        job = get_provider().backends.retrieve_job(job_id)
        return job
    except Exception:
        pass

    return None


def circuit_to_json(
    qc: QuantumCircuit,
    parameter_binds: Optional[List] = None,
    byte_string: bool = False
) -> str:
    if byte_string:
        return pickle.dumps(qc).decode('ISO-8859-1')
    else:
        return json.dumps(circuit_to_dict(qc, parameter_binds), cls=QObjEncoder)


def circuit_to_dict(qc: QuantumCircuit, parameter_binds: Optional[List] = None) -> dict:
    if not parameter_binds:
        qobj = assemble(qc)
    else:
        qobj = assemble(qc, parameter_binds=parameter_binds)
    return qobj.to_dict()


def qobj_to_json(qobj: Union[PulseQobj, QasmQobj]) -> str:
    return json.dumps(qobj.to_dict(), cls=QObjEncoder)


def paulisumop_to_json(op: PauliSumOp) -> str:
    return json.dumps(op.primitive.to_list(), cls=QObjEncoder)


def noisemodel_to_json(noise_model: NoiseModel) -> str:
    return json.dumps(noise_model.to_dict(), cls=QObjEncoder)


def to_json(result: Any, skip: List = []) -> str:
    if result is None:
        return ''
    as_dict = {}
    for name, value in inspect.getmembers(result):
        if not name.startswith('_') and name not in skip and \
            not inspect.ismethod(value) and not inspect.isfunction(value):
            as_dict[name] = value

    return json.dumps(as_dict, cls=QObjEncoder)


def get_job_urls(job: Union[str, IBMQJob]) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        job_id = job.job_id() if isinstance(job, IBMQJob) else job
        download_url = get_provider()._api_client.account_api.job(job_id).download_url()['url']
        result_url = get_provider()._api_client.account_api.job(job_id).result_url()['url']
        return download_url, result_url
    except Exception:
        return None, None


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


def calc_depth(qc: QuantumCircuit):
    tqc = transpile(
        qc, basis_gates=['u1', 'u2', 'u3', 'cx'], optimization_level=0
    )
    num_ops = tqc.count_ops()
    depth = tqc.depth()
    return depth, num_ops
