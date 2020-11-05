import json

from typing import Any, Callable, Optional, Tuple

from qiskit import execute
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.result import Result

from qc_grader.api import get_server_endpoint, send_request
from qc_grader.exercises import get_question_id
from qc_grader.grade import grade, submit
from qc_grader.util import compute_cost, get_provider



basis_gates = [
    'u1', 'u2', 'u3', 'cx', 'cz', 'id',
    'x', 'y', 'z', 'h', 's', 'sdg', 't',
    'tdg', 'swap', 'ccx',
    'unitary', 'diagonal', 'initialize',
    'cu1', 'cu2', 'cu3', 'cswap',
    'mcx', 'mcy', 'mcz',
    'mcu1', 'mcu2', 'mcu3',
    'mcswap', 'multiplexer', 'kraus', 'roerror'
]

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


def get_problem_set(
    lab_id: str, ex_id: str, endpoint: str
) -> Tuple[Optional[int], Optional[Any]]:
    problem_set_response = None

    try:
        payload = {'question_id': get_question_id(lab_id, ex_id)}
        problem_set_response = send_request(endpoint, query=payload, method='GET')
    except Exception as err:
        print('Unable to obtain the problem set')

    try:
        status = problem_set_response.get('status')

        if status == 'valid':
            index = problem_set_response.get('index')
            value = json.loads(problem_set_response.get('value'))
            return index, value
        else:
            cause = problem_set_response.get('cause')
            print(f'Problem set failed: {cause}')
    except Exception as err:
        print(f'Problem set could not be processed: {err}')

    return None, None


def prepare_job(
    solver_func: Callable,
    lab_id: str,
    ex_id: str,
    problem_set: Optional[list] = None,
    server_url: Optional[str] = None
) -> IBMQJob:
    server = server_url if server_url else get_server_endpoint(lab_id, ex_id)
    if not server:
        print('Failed to find and connect to a valid grading server.')
        return

    endpoint = server + 'problem-set'
    index, value = get_problem_set(lab_id, ex_id, endpoint)

    print(f'Running {solver_func.__name__}...')

    qc_1 = solver_func(problem_set)

    if value and index >= 0:
        qc_2 = solver_func(value)
        cost = compute_cost(qc_1)
        
        backend = get_provider().get_backend('ibmq_qasm_simulator')

        # execute experiments
        print('Starting experiments. Please wait...')
        job = execute(
            [qc_1, qc_2],
            basis_gates=basis_gates,
            backend=backend,
            shots=1000,
            seed_simulator=12345,
            optimization_level=0,
            qobj_header={
                'qc_index': [None, index],
                'qc_cost': cost
            }
        )

        print(f'You may monitor the job (id: {job.job_id()}) status '
              'and proceed to grading when it successfully completes.')
        return job
    

def prepare_ex3(solver_func: Callable) -> IBMQJob:
    if callable(solver_func):
        return prepare_job(
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
