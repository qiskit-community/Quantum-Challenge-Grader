from qiskit.algorithms import IterativeAmplitudeEstimation
from qiskit.circuit.library import  LinearAmplitudeFunction
from qiskit_finance.circuit.library import LogNormalDistribution

from qc_grader.grade import grade_and_submit
from .helpers.serialize import answer_2b


def grade_ex2a(values: list) -> None:
    grade_and_submit(values, 'ex2', 'partA')


def grade_ex2b(
    uncertainty_model: LogNormalDistribution,
    european_put_objective: LinearAmplitudeFunction,
    ae: IterativeAmplitudeEstimation
) -> None:
    answer = answer_2b(
        uncertainty_model,
        european_put_objective,
        ae
    )
    grade_and_submit(answer, 'ex2', 'partB')
