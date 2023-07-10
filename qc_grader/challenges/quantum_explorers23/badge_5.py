from typing import List
from typeguard import typechecked
import numpy as np

from qc_grader.grader.grade import grade
from qiskit_machine_learning.algorithms.classifiers.qsvc import QSVC


_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge5_ex1(answer1: List[int]) -> None:
    status, _, message = grade(
        answer1,
        'badge5_ex1',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
    
@typechecked
def grade_badge5_ex2(answer2: List[int]) -> None:
    status, _, message = grade(
        answer2,
        'badge5_ex2',
        _challenge_id, 
        return_response=True
    )
    print(message)
    

@typechecked
def grade_badge5_ex3(answer3: List[int]) -> None:
    status, _, message = grade(
        answer3,
        'badge5_ex3',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex4(answer4: List[int]) -> None:
    status, _, message = grade(
        answer4,
        'badge5_ex4',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex5(answer5: List[int]) -> None:
    status, _, message = grade(
        answer5,
        'badge5_ex5',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge5_ex6(answer6: List[int]) -> None:
    status, _, message = grade(
        answer6,
        'badge5_ex6',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge5_ex7(answer7: List[int]) -> None:
    status, _, message = grade(
        answer7,
        'badge5_ex7',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex8(answer8: List[int]) -> None:
    status, _, message = grade(
        answer8,
        'badge5_ex8',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge5_ex9(answer9: List[int]) -> None:
    status, _, message = grade(
        answer9,
        'badge5_ex9',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex10(answer10: List[int]) -> None:
    status, _, message = grade(
        answer10,
        'badge5_ex10',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex11(answer11: List[int]) -> None:
    status, _, message = grade(
        answer11,
        'badge5_ex11',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex12(answer12: List[int]) -> None:
    status, _, message = grade(
        answer12,
        'badge5_ex12',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge5_ex13(answer13: List[int]) -> None:
    status, _, message = grade(
        answer13,
        'badge5_ex13',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
@typechecked
def grade_badge5_ex14(answer14: List[int]) -> None:
    status, _, message = grade(
        answer14,
        'badge5_ex14',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
@typechecked
def grade_badge5_ex15(answer15: List[int]) -> None:
    status, _, message = grade(
        answer15,
        'badge5_ex15',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge5_code(qsvc: QSVC) -> None:

    x_test = np.array([[5.34070751, 3.45575192, 4.39822972],
       [4.08407045, 2.51327412, 4.08407045],
       [0.62831853, 5.65486678, 4.08407045],
       [5.96902604, 4.39822972, 0.62831853],
       [5.96902604, 4.39822972, 5.96902604],
       [0.        , 5.96902604, 4.08407045]])
    
    y_test = np.array([0, 0, 0, 1, 1, 0])

    test_score = qsvc.score(x_test, y_test)

    status, _, message = grade(
        test_score,
        'badge5_code',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge5_score(lang: str) -> None:
    status, _, message = grade(
        lang,
        'badge5_score',
        _challenge_id,
        return_response=True
    )
    print(message)
