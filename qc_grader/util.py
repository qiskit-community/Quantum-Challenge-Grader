import json

import numpy as np
from typing import Any, Union

from qiskit import IBMQ, QuantumCircuit, assemble
from qiskit.providers.ibmq import AccountProvider, IBMQProviderError
from qiskit.providers.ibmq.exceptions import IBMQBackendApiError, IBMQBackendApiProtocolError
from qiskit.providers.ibmq.job import IBMQJob


def get_provider() -> AccountProvider:
    # get provider
    try:
        provider = IBMQ.get_provider()
    except IBMQProviderError:
        provider = IBMQ.load_account()
    return provider


def get_job_status(job: Union[str, IBMQJob]) -> IBMQJob:
    job_id = job.job_id() if isinstance(job, IBMQJob) else job
    try:
        the_job = job if isinstance(job, IBMQJob) else get_provider().backends.retrieve_job(job_id)
        return job_id, the_job.status()
    except (IBMQBackendApiError, IBMQBackendApiProtocolError):
        return job_id, None


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
