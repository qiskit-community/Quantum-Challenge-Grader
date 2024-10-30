from typeguard import typechecked

from qc_grader.grader.grade import grade

_challenge_id = 'qdc_2024'

@typechecked
def grade_day1_ex1(answer: str) -> None:
    grade(
        answer=answer, 
        question='day1-ex1',
        challenge=_challenge_id
    )

def grade_day1_ex2(answer) -> None: ...

def grade_day1_ex3(answer) -> None: ...

def grade_day1_ex4(answer) -> None: ...

def grade_day1_ex5(answer) -> None: ...

def grade_day1_ex6(answer) -> None: ...

def day1_score_func(answer) -> None: ...
