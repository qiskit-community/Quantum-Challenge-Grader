from typing import Any, Callable
from typeguard import typechecked
import pickle

from qiskit import Aer
from qiskit.algorithms import QAOA
from qiskit.utils import QuantumInstance
from qiskit_optimization.problems.quadratic_program import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Knapsack

from qc_grader.grade import grade_and_submit, run_using_problem_set

seed = 42
time_limit_4b = 20
time_limit_4c = 12
precision_limit = 0.75
shots = 1024
backend = Aer.get_backend("qasm_simulator")

@typechecked
def grade_ex4a(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, '4a')


@typechecked
def grade_ex4b(function: Callable) -> None:
    answer_dict = run_using_problem_set(
        function,
        '4b',
        params_order=['L1', 'L2', 'C1', 'C2', 'C_max']
    )

    problem_set_index = answer_dict['index']
    values, weights, max_weight = answer_dict['result']
    
    prob = Knapsack(values = values,
                    weights = weights, 
                    max_weight = max_weight)
    qp = prob.to_quadratic_program()
    qins = QuantumInstance(backend = Aer.get_backend('qasm_simulator'),
                           shots = shots, 
                           seed_simulator = seed, 
                           seed_transpiler = seed)
    qaoa_mes = QAOA(quantum_instance = qins, reps = 2)
    qaoa = MinimumEigenOptimizer(qaoa_mes)
    result = qaoa.solve(qp)

    answer_dict = {
            'index': problem_set_index,
            'result': result
            }
    answer = pickle.dumps(answer_dict).decode('ISO-8859-1')

    grade_and_submit(answer, '4b')


@typechecked
def grade_ex4c(answer: Any) -> None:
    print('Grading not yet available')
    # grade_and_submit(answer, '4c')
