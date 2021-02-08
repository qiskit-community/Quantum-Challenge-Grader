from qiskit import QuantumCircuit
from qiskit.providers.ibmq.job import IBMQJob

from typing import Callable, Union

from qiskit.circuit.library import CXGate

from qc_grader.grade import prepare_solver, prepare_circuit, grade_job, submit_job


criteria: dict = {
    'max_qubits': 28,
    'min_cost': 100,
    'check_gates': True
}

problem_set_ex2a = [0, 1, 1, 1, 0, 0, 1, 1, 1]
problem_set_ex2b = [
    [1, 1, 1, 0, 0, 0, 1, 0, 0],
    [1, 0, 1, 0, 0, 0, 1, 1, 0],
    [1, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0]
]


def prepare_ex2a(solver_func: Callable) -> IBMQJob:
    return prepare_solver(
        solver_func,
        'week2', 'exA',
        problem_set=problem_set_ex2a,
        **criteria,
        shots=8000,
        seed_simulator=12345,
        backend_options={'fusion_enable': True}
    )


def grade_ex2a(job: Union[IBMQJob, str]) -> None:
    if grade_job(job, 'week2', 'exA'):
        print('Feel free to submit your answer.')


def submit_ex2a(job: Union[IBMQJob, str]) -> None:
    submit_job(job, 'week2', 'exA')


def prepare_ex2b(solver_func: Callable) -> IBMQJob:
    return prepare_solver(
        solver_func,
        'week2', 'exB',
        problem_set=problem_set_ex2b,
        **criteria,
        shots=8000,
        seed_simulator=12345,
        backend_options={'fusion_enable': True}
    )


def grade_ex2b(job: Union[IBMQJob, str]) -> None:
    if grade_job(job, 'week2', 'exB'):
        print('Feel free to submit your answer.')


def submit_ex2b(job: Union[IBMQJob, str]) -> None:
    if submit_job(job, 'week2', 'exB'):
        print('There seems to be huge "noise clusters" interfering with '
              'Dr. Ryoko’s device. Can you please help?')
