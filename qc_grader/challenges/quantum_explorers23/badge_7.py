from typeguard import typechecked
from typing import Callable, Dict, List

from qiskit import QuantumCircuit
from qiskit.primitives import SamplerResult
from qiskit.quantum_info import Operator
from qiskit.result import QuasiDistribution

from qc_grader.grader.grade import grade


_challenge_id = 'quantum_explorers23'


# @typechecked
def grade_badge7_ex1(answer: List[QuantumCircuit]) -> None:
    status, _, message = grade(
        answer,
        'badge7_ex1',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex2(answer: List[float]) -> None:
    status, _, message = grade(
        answer,
        'badge7_ex2',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex3(answer: QuasiDistribution) -> None:
    status, _, message = grade(
        answer,
        'badge7_ex3',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex4(answer: QuantumCircuit) -> None:
    status, _, message = grade(
        answer,
        'badge7_ex4',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex5(answer: QuantumCircuit) -> None:
    answer_op = Operator(answer.remove_final_measurements(inplace=False))
    answer_data = answer_op.data

    status, _, message = grade(
        answer_data,
        'badge7_ex5',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex6(answer: Callable) -> None:
    test_data = SamplerResult([{0: 0.1, 1: 0.2, 2: 0, 3: 0,
                                   4: 0.3, 5: 0.4, 6: 0, 7: 0}],
                                   [{}])
    post_select_dist = answer(test_data)[0]
    
    status, _, message = grade(
        post_select_dist,
        'badge7_ex6',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex7(answer: List) -> None:
    status, _, message = grade(
        answer,
        'badge7_ex7',
        _challenge_id, 
        return_response=True
    )
    print(message)

# @typechecked
def grade_badge7_ex8(answer: List) -> None:
    status, _, message = grade(
        answer,
        'badge7_ex8',
        _challenge_id, 
        return_response=True
    )
    print(message)


    #####


@typechecked
def grade_badge7_score(lang: str) -> None:
    status, _, message = grade(
        lang,
        'badge7_score',
        _challenge_id,
        return_response=True
    )
    print(message)
