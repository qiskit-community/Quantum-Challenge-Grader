from typing import Any, Callable, Dict, Union
from typeguard import typechecked

from qiskit_optimization.problems.quadratic_program import QuadraticProgram
from qiskit_optimization.algorithms.minimum_eigen_optimizer import MinimumEigenOptimizationResult
from qiskit.providers.ibmq.job import IBMQJob

from qc_grader.grade import grade_and_submit, run_using_problem_set, submit_job


@typechecked
def grade_ex4a(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, '4a')


@typechecked
def grade_ex4b(function: Callable) -> None:
    answer = run_using_problem_set(
        function,
        '4b',
        params_order=['L1', 'L2', 'C1', 'C2', 'C_max']
    )
    if answer:
        grade_and_submit(answer, '4b')


@typechecked
def prepare_ex4c(function: Callable) -> IBMQJob:
    return run_using_problem_set(
        function,
        '4c',
        params_order=['L1', 'L2', 'C1', 'C2', 'C_max'],
        execute_result=True
    )

@typechecked
def grade_ex4c(job: Union[IBMQJob, str]):
    grade_and_submit(job, '4c')
