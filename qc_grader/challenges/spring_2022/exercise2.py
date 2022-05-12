from typing import List, Union
from typeguard import typechecked

import numpy as np

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'spring_2022'


@typechecked
def grade_ex2a(qc: QuantumCircuit) -> None:
    grade(qc, '2a', _challenge_id, do_submit=True, byte_string=True)

@typechecked
def grade_ex2b(prob_densities: Union[np.ndarray, List[List[float]]]) -> None:
    answer = prob_densities.tolist() if type(prob_densities) == np.ndarray else prob_densities
    grade(answer, '2b', _challenge_id, do_submit=True)


@typechecked
def grade_ex2c(prob_densitiy_localization: List[List[float]]) -> None:
    grade(prob_densitiy_localization, '2c', _challenge_id, do_submit=True)
