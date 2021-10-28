import pickle
from typing import Any, Callable, Dict

import numpy as np
from qiskit import Aer
from qiskit.algorithms import QAOA
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.utils import QuantumInstance
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Knapsack
from qiskit_optimization.problems import QuadraticProgram
from typeguard import typechecked

from qc_grader.grade import grade_and_submit, run_using_problem_set, prepare_solver
from qc_grader.util import get_challenge_provider

seed = 42
time_limit_4b = 20
time_limit_4c = 12
precision_limit = 0.75
shots_4b = 1024
shots_4c = 512
backend = Aer.get_backend("qasm_simulator")

criteria: Dict[str, Any] = {
    'max_qubits': 28,
    'min_cost': None,
    'check_gates': False
}

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

test_problem_set = [
    {
        'L1': [3, 7, 3, 4, 2, 6, 2, 2, 4, 6, 6],
        'L2': [7, 8, 7, 6, 6, 9, 6, 7, 6, 7, 7],
        'C1': [2, 2, 2, 3, 2, 4, 2, 2, 2, 2, 2],
        'C2': [4, 3, 3, 4, 4, 5, 3, 4, 4, 3, 4],
        'C_max': 33,
        'optimal_value': 67
    },
    {
        'L1': [2, 2, 3, 7, 2, 4, 5, 5, 2, 3, 4],
        'L2': [6, 6, 9, 8, 9, 5, 7, 7, 5, 6, 8],
        'C1': [4, 2, 2, 3, 2, 3, 2, 2, 3, 4, 3],
        'C2': [5, 5, 4, 4, 3, 5, 3, 3, 4, 5, 5],
        'C_max': 38,
        'optimal_value': 66
    }
]


@typechecked
def grade_ex4a(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, '4a')


def run_qaoa(values: list, weights: list, max_weight: int) -> np.ndarray:
    prob = Knapsack(values=values,
                    weights=weights,
                    max_weight=max_weight)
    qp = prob.to_quadratic_program()
    qins = QuantumInstance(backend=Aer.get_backend('qasm_simulator'),
                           shots=shots_4b,
                           seed_simulator=seed,
                           seed_transpiler=seed)
    qaoa_mes = QAOA(quantum_instance=qins, reps=2)
    qaoa = MinimumEigenOptimizer(qaoa_mes)
    result = qaoa.solve(qp)
    return result.x


@typechecked
def grade_ex4b(function: Callable) -> None:
    result_dicts = run_using_problem_set(
        function,
        '4b',
        params_order=['L1', 'L2', 'C1', 'C2', 'C_max']
    )

    answer_dicts = []
    for result_dict in result_dicts:
        problem_set_index = result_dict['index']
        values, weights, max_weight = result_dict['result']

        result = run_qaoa(values, weights, max_weight)

        answer_dict = {
            'index': problem_set_index,
            'result': result
        }
        answer_dicts.append(answer_dict)
        answer = pickle.dumps(answer_dicts).decode('ISO-8859-1')

    grade_and_submit(answer, '4b')


def prepare_ex4c(solver_func: Callable) -> IBMQJob:
    return prepare_solver(
        solver_func,
        '4c',
        **criteria,
        basis_gates=basis_gates,
        shots=shots_4c,
        seed_simulator=12345,
        optimization_level=0,
        test_problem_set=test_problem_set,
        params_order=['L1', 'L2', 'C1', 'C2', 'C_max']
    )


@typechecked
def grade_ex4c(job: IBMQJob) -> None:
    grade_and_submit(job, '4c')
