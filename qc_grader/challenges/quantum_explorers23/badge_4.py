from typeguard import typechecked
from typing import List


from qc_grader.grader.grade import grade
from qc_grader.custom_encoder.serializer import (
    samplerresult_to_json,
    quasidistribution_to_json
)

#################

_challenge_id = 'quantum_explorers23'


@typechecked
def grade_badge4_ex1(answer1: List[int]) -> None:
    status, _, message = grade(
        answer1,
        'badge4_ex1',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
    
@typechecked
def grade_badge4_ex2(answer2: List[int]) -> None:
    status, _, message = grade(
        answer2,
        'badge4_ex2',
        _challenge_id, 
        return_response=True
    )
    print(message)
    

@typechecked
def grade_badge4_ex3(answer3: List[int]) -> None:
    status, _, message = grade(
        answer3,
        'badge4_ex3',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex4(answer4: List[int]) -> None:
    status, _, message = grade(
        answer4,
        'badge4_ex4',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex5(answer5: List[int]) -> None:
    status, _, message = grade(
        answer5,
        'badge4_ex5',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge4_ex6(answer6: List[int]) -> None:
    status, _, message = grade(
        answer6,
        'badge4_ex6',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge4_ex7(answer7: List[int]) -> None:
    status, _, message = grade(
        answer7,
        'badge4_ex7',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex8(answer8: List[int]) -> None:
    status, _, message = grade(
        answer8,
        'badge4_ex8',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge4_ex9(answer9: List[int]) -> None:
    status, _, message = grade(
        answer9,
        'badge4_ex9',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex10(answer10: List[int]) -> None:
    status, _, message = grade(
        answer10,
        'badge4_ex10',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex11(answer11: List[int]) -> None:
    status, _, message = grade(
        answer11,
        'badge4_ex11',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex12(answer12: List[int]) -> None:
    status, _, message = grade(
        answer12,
        'badge4_ex12',
        _challenge_id, 
        return_response=True
    )
    print(message)

@typechecked
def grade_badge4_ex13(answer13: List[int]) -> None:
    status, _, message = grade(
        answer13,
        'badge4_ex13',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
@typechecked
def grade_badge4_ex14(answer14: List[int]) -> None:
    status, _, message = grade(
        answer14,
        'badge4_ex14',
        _challenge_id, 
        return_response=True
    )
    print(message)
    
@typechecked
def grade_badge4_ex15(answer15: List[int]) -> None:
    status, _, message = grade(
        answer15,
        'badge4_ex15',
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge4_code(sampler_results: List, quasi_dists: List) -> None: 
    answer = {
        'sampler_results': [samplerresult_to_json(r) for r in sampler_results],
        'quasi_dists': [quasidistribution_to_json(d) for d in quasi_dists], 
    }
    status, _, message = grade(
        answer, 
        'badge4_code', 
        _challenge_id, 
        return_response=True
    )
    print(message)


@typechecked
def grade_badge4_score(lang: str) -> None:
    status, _, message = grade(
        lang,
        'badge4_score',
        _challenge_id,
        return_response=True
    )
    print(message)
