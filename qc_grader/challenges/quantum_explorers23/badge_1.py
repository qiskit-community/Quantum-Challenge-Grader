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
def grade_badge1_ex4(answer4: List[int]) -> None:
    status, _, message = grade(
        answer4,
        'badge1_ex4',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex5(answer5: List[int]) -> None:
    status, _, message = grade(
        answer5,
        'badge1_ex5',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge1_ex6(answer6: List[int]) -> None:
    status, _, message = grade(
        answer6,
        'badge1_ex6',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge1_ex7(answer7: List[int]) -> None:
    status, _, message = grade(
        answer7,
        'badge1_ex7',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex8(answer8: List[int]) -> None:
    status, _, message = grade(
        answer8,
        'badge1_ex8',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge1_ex9(answer9: List[int]) -> None:
    status, _, message = grade(
        answer9,
        'badge1_ex9',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex10(answer10: List[int]) -> None:
    status, _, message = grade(
        answer10,
        'badge1_ex10',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex11(answer11: List[int]) -> None:
    status, _, message = grade(
        answer11,
        'badge1_ex11',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex12(answer12: List[int]) -> None:
    status, _, message = grade(
        answer12,
        'badge1_ex12',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex13(answer13: List[int]) -> None:
    status, _, message = grade(
        answer13,
        'badge1_ex13',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex14(answer14: List[int]) -> None:
    status, _, message = grade(
        answer14,
        'badge1_ex14',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge1_ex15(answer15: List[int]) -> None:
    status, _, message = grade(
        answer15,
        'badge1_ex15',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge1_code(circuit: QuantumCircuit) -> None:
    status, _, message = grade(
        circuit,
        'badge1_code',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge1_score(lang: str) -> None:
    status, _, message = grade(
        lang,
        'badge1_score',
        _challenge_id
    )
    print(message)
