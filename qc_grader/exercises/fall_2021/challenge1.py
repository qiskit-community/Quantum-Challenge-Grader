import jsonpickle
import pickle
import numpy.typing as npt

from typing import Dict
from typeguard import typechecked

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms.minimum_eigen_optimizer import MinimumEigenOptimizationResult

from qc_grader.grade import grade_and_submit


@typechecked
def grade_ex1a(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, '1a')


@typechecked
def grade_ex1b(result: MinimumEigenOptimizationResult) -> None:
    answer = pickle.dumps(result).decode('ISO-8859-1')
    grade_and_submit(answer, '1b')


@typechecked
def grade_ex1c(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, '1c')


@typechecked
def grade_ex1d(result: MinimumEigenOptimizationResult) -> None:
    answer = pickle.dumps(result).decode('ISO-8859-1')
    grade_and_submit(answer, '1d')
