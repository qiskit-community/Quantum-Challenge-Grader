import numpy as np
import pickle

from pathlib import Path
from typeguard import typechecked
from typing import Any, Callable, Dict

from qiskit import Aer
from qiskit.algorithms import QAOA
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob
from qiskit.utils import QuantumInstance
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Knapsack
from qiskit_optimization.problems import QuadraticProgram

from qc_grader.grader.grade import grade, prepare_solver, run_using_problem_set


challenge_id = Path(__file__).parent.name


seed = 42
time_limit_4b = 20
time_limit_4c = 12
precision_limit = 0.75
shots = 1024
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
    {'L1': [2, 2, 3, 2, 3, 2, 2],
     'L2': [3, 3, 4, 3, 4, 3, 4],
     'C1': [2, 2, 2, 2, 2, 2, 2],
     'C2': [4, 4, 4, 3, 3, 3, 3],
     'C_max': 19},
    {'L1': [2, 2, 2, 3, 3, 3, 2],
     'L2': [3, 3, 4, 4, 4, 4, 4],
     'C1': [2, 2, 2, 2, 3, 2, 2],
     'C2': [4, 3, 4, 4, 4, 3, 3],
     'C_max': 20}
]


@typechecked
def grade_ex4a(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade(answer, '4a', challenge_id)


def run_qaoa(values: list, weights: list, max_weight: int) -> np.ndarray:
    prob = Knapsack(values=values,
                    weights=weights,
                    max_weight=max_weight)
    qp = prob.to_quadratic_program()
    qins = QuantumInstance(backend=Aer.get_backend('qasm_simulator'),
                           shots=shots,
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
        challenge_id,
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
        answer = pickle.dumps(answer_dicts).hex(' ', -4)

    grade(answer, '4b', challenge_id)


def prepare_ex4c(solver_func: Callable) -> IBMQJob:
    return prepare_solver(
        solver_func,
        '4c',
        challenge_id,
        **criteria,
        basis_gates=basis_gates,
        shots=512,
        seed_simulator=42,
        optimization_level=0,
        params_order=['L1', 'L2', 'C1', 'C2', 'C_max']
    )


@typechecked
def grade_ex4c(job: IBMQJob) -> None:
    grade(job, '4c', challenge_id)
