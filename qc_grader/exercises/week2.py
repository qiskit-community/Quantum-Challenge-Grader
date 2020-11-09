from qiskit import QuantumCircuit
from qiskit.providers.ibmq.job import IBMQJob

from typing import Union

from qc_grader.grade import prepare_circuit, grade_job, submit_job


def prepare_ex2a(circuit: QuantumCircuit) -> IBMQJob:
    return prepare_circuit(
        circuit,
        max_qubits=28,
        shots=8000,
        seed_simulator=12345,
        backend_options={"fusion_enable": True},
    )


def grade_ex2a(job: Union[IBMQJob, str]) -> None:
    if grade_job(job, 'week2', 'exA'):
        print('Feel free to submit your answer.')


def submit_ex2a(job: Union[IBMQJob, str]) -> None:
    submit_job(job, 'week2', 'exA')


def prepare_ex2b(circuit: QuantumCircuit) -> IBMQJob:
    return prepare_circuit(
        circuit,
        max_qubits=28,
        shots=8000,
        seed_simulator=12345,
        backend_options={"fusion_enable": True},
    )


def grade_ex2b(job: Union[IBMQJob, str]) -> None:
    if grade_job(job, 'week2', 'exB'):
        print('Feel free to submit your answer.')


def submit_ex2b(job: Union[IBMQJob, str]) -> None:
    if submit_job(job, 'week2', 'exB'):
        print('There seems to be huge "noise clusters" interfering with '
              'Dr. Ryoko’s device. Can you please help?')
