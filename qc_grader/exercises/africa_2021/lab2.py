from qiskit.algorithms import IterativeAmplitudeEstimation
from qiskit.circuit.library import  LinearAmplitudeFunction
from qiskit_finance.circuit.library import LogNormalDistribution

from qc_grader.grade import grade_json, submit_json
from .helpers.serialize import answer_2b

criteria: dict = {}


def grade_ex2a(values: list) -> None:
    ok, _ = grade_json(values, 'ex2', 'partA', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


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
    ok, _ = grade_json(answer, 'ex2', 'partB', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex2a(values: list) -> None:
    submit_json(values, 'ex2', 'partA', **criteria)


def submit_ex2b(
    uncertainty_model: LogNormalDistribution,
    european_put_objective: LinearAmplitudeFunction,
    ae: IterativeAmplitudeEstimation
) -> None:
    answer = answer_2b(
        uncertainty_model,
        european_put_objective,
        ae
    )
    submit_json(answer, 'ex2', 'partB', **criteria)
