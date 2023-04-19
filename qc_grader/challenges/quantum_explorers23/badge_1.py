from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge1_ex1(answer1: List[int]) -> None:
    status, _, message = grade(
        answer1,
        'badge1_ex1',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
    
@typechecked
def grade_badge1_ex2(answer2: List[int]) -> None:
    status, _, message = grade(
        answer2,
        'badge1_ex2',
        _challenge_id, 
        return_response=True
    )
    print(message)
    

@typechecked
def grade_badge1_ex3(answer3: List[int]) -> None:
    status, _, message = grade(
        answer3,
        'badge1_ex3',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge1_ex16(circuit: QuantumCircuit) -> None:
    status, _, message = grade(
        circuit,
        'badge1_ex16',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
    
@typechecked
def grade_badge1_score(check_score: List[int]) -> None:
    status, _, message = grade(
        check_score,
        'badge1_score',
        _challenge_id, 
        return_response=True
    )
    print(message)
