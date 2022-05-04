from pathlib import Path
from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex2a(qc: QuantumCircuit) -> None:
    grade(qc, 4, challenge_id, byte_string=True)  # 2a


@typechecked
def grade_ex2b(prob_densities: List[List[float]]) -> None:
    grade(prob_densities, 5, challenge_id)  # 2b


@typechecked
def grade_ex2c(prob_densitiy_localization: List[List[float]]) -> None:
    grade(prob_densitiy_localization, 6, challenge_id)  # 2c
