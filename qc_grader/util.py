import json

import numpy as np
from typing import Any, Optional, Tuple, Union

from qiskit import IBMQ, QuantumCircuit, assemble
from qiskit.providers.ibmq import AccountProvider, IBMQProviderError
from qiskit.providers.ibmq.job import IBMQJob


def get_provider() -> AccountProvider:
    # get provider
    try:
        provider = IBMQ.get_provider()
    except IBMQProviderError:
        provider = IBMQ.load_account()
    return provider


def get_job_status(job: Union[str, IBMQJob]) -> Tuple[str, Optional[str]]:
    try:
        if isinstance(job, IBMQJob):
            job_id = job.job_id()
            job_status = job.status()
        else:
            job_id = job
            job_status = get_provider().backends.retrieve_job(job_id).status()
    except Exception:
        return job_id, None

    return job_id, job_status


def circuit_to_json(qc: QuantumCircuit) -> str:
    class _QobjEncoder(json.encoder.JSONEncoder):
        def default(self, obj: Any) -> Any:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, complex):
                return (obj.real, obj.imag)
            return json.JSONEncoder.default(self, obj)

    return json.dumps(circuit_to_dict(qc), cls=_QobjEncoder)


def circuit_to_dict(qc: QuantumCircuit) -> dict:
    qobj = assemble(qc)
    return qobj.to_dict()
