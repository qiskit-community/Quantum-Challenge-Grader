from pathlib import Path
from typing import Any, Dict, List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex3a(imbalance_val: float) -> None:
    grade(imbalance_val, 7, challenge_id)  # 3a


@typechecked
def grade_ex3b(vn_entropies: Dict[int, List[float]]) -> None:
    grade(vn_entropies, 8, challenge_id)  # 3b


@typechecked
def grade_ex3c(vector_state_imbalances: Dict[int, List[float]]) -> None:
    grade(vector_state_imbalances, 9, challenge_id)  # 3c
