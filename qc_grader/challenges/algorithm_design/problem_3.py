from typeguard import typechecked
from qiskit.circuit.library import TwoLocal
from qc_grader.grader.grade import grade

_challenge_id = 'algorithm_design'


@typechecked
def grade_problem_3(answer: list) -> None:
    grade(answer, 'problem_3', _challenge_id)
