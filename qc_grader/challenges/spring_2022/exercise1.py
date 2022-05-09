from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'spring_2022'


@typechecked
def grade_ex1a(qc: QuantumCircuit) -> None:
    grade(qc, '1a', _challenge_id, do_submit=True, byte_string=True)


@typechecked
def grade_ex1b(qc: QuantumCircuit) -> None:
    grade(qc, '1b', _challenge_id, do_submit=True, byte_string=True)


@typechecked
def grade_ex1c(list_fidelities: List[float]) -> None:
    grade(list_fidelities, '1c', _challenge_id, do_submit=True)
