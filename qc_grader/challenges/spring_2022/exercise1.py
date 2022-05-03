from pathlib import Path
from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name


@typechecked
def grade_ex1a(qc: QuantumCircuit) -> None:
    grade(qc, 1, challenge_id, byte_string=True)  # 1a


@typechecked
def grade_ex1b(qc: QuantumCircuit) -> None:
    grade(qc, 2, challenge_id, byte_string=True)  # 1b


@typechecked
def grade_ex1c(list_fidelities: List[float]) -> None:
    grade(list_fidelities, 3, challenge_id)  # 1c
