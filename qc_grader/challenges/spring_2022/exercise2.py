from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'spring-2022'


@typechecked
def grade_ex2a(qc: QuantumCircuit) -> None:
    grade(qc, '2a', _challenge_id, byte_string=True)

@typechecked
def grade_ex2b(prob_densities: List[List[float]]) -> None:
    grade(prob_densities, '2b', _challenge_id)


@typechecked
def grade_ex2c(prob_densitiy_localization: List[List[float]]) -> None:
    grade(prob_densitiy_localization, '2c', _challenge_id)
