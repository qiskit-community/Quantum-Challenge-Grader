from typing import Any, Callable, Dict, List
from typeguard import typechecked

import numpy as np

from qiskit.quantum_info import Statevector

from qc_grader.grader.grade import grade, get_problem_set


_challenge_id = 'spring_2022'


@typechecked
def grade_ex3a(get_imbalance: Callable) -> None:
    _, states = get_problem_set('3a', _challenge_id)

    answer = {}
    for s in states:
        state = Statevector(np.loads(s.encode('ISO-8859-1')))
        answer[get_imbalance(state)] = s

    grade(answer, '3a', _challenge_id, do_submit=True, max_content_length=2*1024*1024)


@typechecked
def grade_ex3b(vn_entropies: Dict[int, List[float]]) -> None:
    grade(vn_entropies, '3b', _challenge_id, do_submit=True)


@typechecked
def grade_ex3c(vector_state_imbalances: Dict[int, List[float]]) -> None:
    grade(vector_state_imbalances, '3c', _challenge_id, do_submit=True)
