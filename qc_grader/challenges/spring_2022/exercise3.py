from typing import Any, Dict, List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'spring-2022'


@typechecked
def grade_ex3a(imbalance_val: float) -> None:
    grade(imbalance_val, '3a', _challenge_id)


@typechecked
def grade_ex3b(vn_entropies: Dict[int, List[float]]) -> None:
    grade(vn_entropies, '3b', _challenge_id)


@typechecked
def grade_ex3c(vector_state_imbalances: Dict[int, List[float]]) -> None:
    grade(vector_state_imbalances, '3c', _challenge_id)
