import jsonpickle
import pickle

from pathlib import Path

from qiskit.algorithms.minimum_eigen_solvers import VQE, QAOA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms.minimum_eigen_optimizer import MinimumEigenOptimizer
from typeguard import typechecked

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex1a(qp: QuadraticProgram) -> None:
    answer = jsonpickle.encode(qp.export_as_lp_string())
    grade(answer, '1a', challenge_id)


@typechecked
def grade_ex1b(vqe: VQE, qp: QuadraticProgram) -> None:
    if isinstance(vqe, QAOA):
        print("Oops 😕! Please use VQE instead of QAOA algorithm to solve this exercise.")
        return
    meo = MinimumEigenOptimizer(vqe)
    result = meo.solve(qp)
    answer = pickle.dumps(result).decode('ISO-8859-1')
    grade(answer, '1b', challenge_id)


@typechecked
def grade_ex1c(qaoa: QAOA, qp: QuadraticProgram) -> None:
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    answer = pickle.dumps(result).decode('ISO-8859-1')
    grade(answer, '1c', challenge_id)
