
from typeguard import typechecked

from typing import Dict

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade
from qc_grader.common.serializer import circuit_to_json


_challenge_id = 'algo_queen_2023'


@typechecked
def grade_prob1_ex3(qc: QuantumCircuit, counts: Dict[str, int]) -> None:
    answer = {
        'qc': circuit_to_json(qc),
        'counts': counts
    }

    grade(answer, 'prob1-ex3', _challenge_id)
