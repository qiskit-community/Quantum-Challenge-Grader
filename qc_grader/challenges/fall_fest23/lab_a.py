from typeguard import typechecked

from qiskit.circuit import QuantumCircuit
from qiskit.result.counts import Counts

from qc_grader.grader.grade import grade


_challenge_id = 'fall_fest23'


@typechecked
def grade_ex1a(answer1: Counts) -> None:
    grade(answer1, 'ex1a', _challenge_id)


@typechecked
def grade_ex1b(answer2: QuantumCircuit) -> None:
    grade(answer2, 'ex1b', _challenge_id)
