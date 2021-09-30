from typing import Dict, Union
import jsonpickle

from qiskit_finance.applications.optimization.portfolio_optimization import PortfolioOptimization
from qiskit_optimization.algorithms.minimum_eigen_optimizer import MinimumEigenOptimizationResult

from qc_grader.grade import grade_and_submit

def grade_ex1a(portfolio: PortfolioOptimization) -> None:
    answer = jsonpickle.encode(portfolio)
    grade_and_submit(answer, 'ex1', 'partA')

def grade_ex1b(result: MinimumEigenOptimizationResult) -> None:
    answer = jsonpickle.encode(result.x)
    grade_and_submit(answer, 'ex1', 'partB')

