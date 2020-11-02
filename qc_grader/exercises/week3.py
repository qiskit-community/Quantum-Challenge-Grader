from typing import Callable

from qiskit.providers.ibmq.job import IBMQJob

from qc_grader.grade import prepare_grading_job, grade, submit


problem_set_ex3 = [
    [['0', '2'], ['1', '0'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '3']],
    [['0', '0'], ['0', '1'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '3']],
    [['0', '0'], ['1', '1'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
    [['0', '0'], ['0', '1'], ['1', '1'], ['1', '3'], ['3', '2'], ['3', '3']],
    [['0', '2'], ['1', '0'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
    [['1', '1'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '1'], ['3', '3']],
    [['0', '2'], ['0', '3'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']],
    [['0', '0'], ['0', '3'], ['1', '2'], ['2', '2'], ['2', '3'], ['3', '0']],
    [['0', '3'], ['1', '1'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']],
    [['0', '0'], ['0', '1'], ['1', '3'], ['2', '1'], ['2', '3'], ['3', '0']],
    [['0', '1'], ['0', '3'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '2']],
    [['0', '0'], ['1', '3'], ['2', '0'], ['2', '1'], ['2', '3'], ['3', '1']],
    [['0', '1'], ['0', '2'], ['1', '0'], ['1', '2'], ['2', '2'], ['2', '3']],
    [['0', '3'], ['1', '0'], ['1', '3'], ['2', '1'], ['2', '2'], ['3', '0']],
    [['0', '2'], ['0', '3'], ['1', '2'], ['2', '3'], ['3', '0'], ['3', '1']],
    [['0', '1'], ['1', '0'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '1']]
]


def prepare_ex3(solver_func: Callable) -> IBMQJob:
    if callable(solver_func):
        return prepare_grading_job(
            solver_func,
            'week3', 'exA',
            problem_set=problem_set_ex3
        )
    else:
        print(f'Expected a function, but was given {type(solver_func)}')
        print(f'Please provide a function that returns a QuantumCircuit.')


def grade_ex3(job: IBMQJob) -> None:
    if isinstance(job, IBMQJob) or isinstance(job, str):
        grade(job, 'week3', 'exA')
    else:
        print(f'Expected an IBMQJob or a job ID, but was given {type(job)}')
        print(f'Please submit a job as your answer.')


def submit_ex3(job: IBMQJob) -> None:
    if isinstance(job, IBMQJob) or isinstance(job, str):
        submit(job, 'week3', 'exA')
    else:
        print(f'Expected an IBMQJob or a job ID, but was given {type(job)}')
        print(f'Please submit a job as your answer.')
