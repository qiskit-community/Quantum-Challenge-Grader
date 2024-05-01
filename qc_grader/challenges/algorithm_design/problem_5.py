from typeguard import typechecked
from qc_grader.grader.grade import grade
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import Estimator

_challenge_id = 'algorithm_design'


@typechecked
def grade_problem_5a(
    cost_function: callable,
    k: int,
    ansatz_list: TwoLocal,
    weight_vector: list[float],
    hamiltonian: SparsePauliOp,
    estimator: Estimator
) -> None:
    evaluation_points = (2*np.pi*np.random.rand(50, 8)).tolist()
    user_values = []
    for theta in evaluation_points:
        user_value = cost_function(theta, k, ansatz_list, weight_vector, hamiltonian, estimator)
        user_values.append(user_value)
    grade(
        {'evaluation_points': evaluation_points, 'user_values': user_values},
        'problem_5a',
        _challenge_id
    )


@typechecked
def grade_problem_5b(eigenvalues: list) -> None:
    evaluation_points = (2*np.pi*np.random.rand(50, 8)).tolist()
    grade(
        {'evaluation_points': evaluation_points, 'eigenvalues': eigenvalues},
        'problem_5b',
        _challenge_id
    )
