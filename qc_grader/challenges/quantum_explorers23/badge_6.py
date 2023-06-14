from typing import List
from typeguard import typechecked

from qc_grader.grader.grade import grade



_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge6_ex1(answer1: List[int]) -> None:
    status, _, message = grade(
        answer1,
        'badge6_ex1',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
    
@typechecked
def grade_badge6_ex2(answer2: List[int]) -> None:
    status, _, message = grade(
        answer2,
        'badge6_ex2',
        _challenge_id, 
        return_response=True
    )
    print(message)
    

@typechecked
def grade_badge6_ex3(answer3: List[int]) -> None:
    status, _, message = grade(
        answer3,
        'badge6_ex3',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex4(answer4: List[int]) -> None:
    status, _, message = grade(
        answer4,
        'badge6_ex4',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex5(answer5: List[int]) -> None:
    status, _, message = grade(
        answer5,
        'badge6_ex5',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge6_ex6(answer6: List[int]) -> None:
    status, _, message = grade(
        answer6,
        'badge6_ex6',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge6_ex7(answer7: List[int]) -> None:
    status, _, message = grade(
        answer7,
        'badge6_ex7',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex8(answer8: List[int]) -> None:
    status, _, message = grade(
        answer8,
        'badge6_ex8',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge6_ex9(answer9: List[int]) -> None:
    status, _, message = grade(
        answer9,
        'badge6_ex9',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex10(answer10: List[int]) -> None:
    status, _, message = grade(
        answer10,
        'badge6_ex10',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex11(answer11: List[int]) -> None:
    status, _, message = grade(
        answer11,
        'badge6_ex11',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex12(answer12: List[int]) -> None:
    status, _, message = grade(
        answer12,
        'badge6_ex12',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge6_ex13(answer13: List[int]) -> None:
    status, _, message = grade(
        answer13,
        'badge6_ex13',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
@typechecked
def grade_badge6_ex14(answer14: List[int]) -> None:
    status, _, message = grade(
        answer14,
        'badge6_ex14',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
@typechecked
def grade_badge6_ex15(answer15: List[int]) -> None:
    status, _, message = grade(
        answer15,
        'badge6_ex15',
        _challenge_id, 
        return_response=True
    )
    print(message)


##### coding question

@typechecked
def grade_badge6_code(ans: List) -> None:
    status, _, message = grade(
        ans,
        'badge6_code',
        _challenge_id, 
        return_response=True
    )
    print(message)

#####


@typechecked
def grade_badge6_score(lang: str) -> None:
    status, _, message = grade(
        lang,
        'badge6_score',
        _challenge_id,
        return_response=True
    )
    print(message)
