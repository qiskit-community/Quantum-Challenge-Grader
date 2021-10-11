import jsonpickle
import numpy.typing as npt

from typing import Dict
from typeguard import typechecked

from qiskit_finance.applications.optimization.portfolio_optimization import PortfolioOptimization

from qc_grader.grade import grade_and_submit


@typechecked
def grade_ex1a(portfolio: PortfolioOptimization) -> None:
    answer = jsonpickle.encode(portfolio)
    grade_and_submit(answer, '1a')


@typechecked
def grade_ex1b(numpy_results: npt.ArrayLike) -> None:
    answer = jsonpickle.encode(numpy_results)
    grade_and_submit(answer, '1b')


@typechecked
def grade_ex1c(numpy_results: npt.ArrayLike) -> None:
    answer = jsonpickle.encode(numpy_results)
    grade_and_submit(answer, '1c')
