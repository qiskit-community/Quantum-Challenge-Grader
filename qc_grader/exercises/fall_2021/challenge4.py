from typing import Dict, Union
import jsonpickle

from qiskit_optimization.problems.quadratic_program import QuadraticProgram
from qiskit_optimization.algorithms.minimum_eigen_optimizer import MinimumEigenOptimizationResult

from qc_grader.grade import grade_and_submit

def grade_ex4a(quadratic_program: QuadraticProgram) -> None:
    objective = quadratic_program.objective

    answer_dict = {
                'offset': objective.constant,
                'matrix': objective.quadratic.to_array(symmetric=True),
                'linear coeff': objective.linear.to_array()
            }
    answer = jsonpickle.encode(answer_dict)
    grade_and_submit(answer, 'ex4', 'partA')

def grade_ex4b(result: MinimumEigenOptimizationResult) -> None:
    answer = jsonpickle.encode(result.x)
    grade_and_submit(answer, 'ex4', 'partB')

def grade_ex4c(result: MinimumEigenOptimizationResult) -> None:
    answer = jsonpickle.encode(result.x)
    grade_and_submit(answer, 'ex4', 'partC')
