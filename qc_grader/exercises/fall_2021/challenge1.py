from typing import Dict, Union
import jsonpickle

from qiskit_finance.applications.optimization.portfolio_optimization import PortfolioOptimization

from qc_grader.grade import grade_and_submit

def grade_ex1a(portfolio: PortfolioOptimization) -> None:
    answer = jsonpickle.encode(portfolio)
    grade_and_submit(answer, 'ex1', 'partA')

