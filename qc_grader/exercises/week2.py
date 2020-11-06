from qiskit import QuantumCircuit
from qiskit.providers.ibmq.job import IBMQJob

from typing import Union

from qc_grader.grade import prepare_circuit, grade_job, submit_job


def prepare_ex2a(circuit: QuantumCircuit) -> IBMQJob:
    return prepare_circuit(
        circuit,
        shots=8000,
        seed_simulator=12345,
        backend_options={"fusion_enable": True},
    )


def grade_ex2a(job: Union[IBMQJob, str]) -> None:
    grade_job(job, 'week2', 'exA')


def submit_ex2a(job: Union[IBMQJob, str]) -> None:
    submit_job(job, 'week2', 'exA')


def prepare_ex2b(circuit: QuantumCircuit) -> IBMQJob:
    return prepare_circuit(
        circuit,
        shots=8000,
        seed_simulator=12345,
        backend_options={"fusion_enable": True},
    )


def grade_ex2b(job: Union[IBMQJob, str]) -> None:
    grade_job(job, 'week2', 'exB')


def submit_ex2b(job: Union[IBMQJob, str]) -> None:
    submit_job(job, 'week2', 'exB')
