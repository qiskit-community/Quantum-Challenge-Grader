from qiskit.providers.ibmq.job import IBMQJob

from typing import Union

from qc_grader.grade import grade, submit


def grade_ex2a(job: Union[IBMQJob, str]) -> None:
    if isinstance(job, IBMQJob) or isinstance(job, str):
        grade(job, 'week2', 'exA')
    else:
        print(f'Expected an IBMQJob or a job ID, but was given {type(job)}')
        print(f'Please submit a job as your answer.')


def submit_ex2a(job: Union[IBMQJob, str]) -> None:
    if isinstance(job, IBMQJob) or isinstance(job, str):
        submit(job, 'week2', 'exA')
    else:
        print(f'Expected an IBMQJob or a job ID, but was given {type(job)}')
        print(f'Please submit a job as your answer.')


def grade_ex2b(job: Union[IBMQJob, str]) -> None:
    if isinstance(job, IBMQJob) or isinstance(job, str):
        grade(job, 'week2', 'exB')
    else:
        print(f'Expected an IBMQJob or a job ID, but was given {type(job)}')
        print(f'Please submit a job as your answer.')


def submit_ex2b(job: Union[IBMQJob, str]) -> None:
    if isinstance(job, IBMQJob) or isinstance(job, str):
        submit(job, 'week2', 'exB')
    else:
        print(f'Expected an IBMQJob or a job ID, but was given {type(job)}')
        print(f'Please submit a job as your answer.')
