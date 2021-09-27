from typing import Dict, Union
from qc_grader.grade import grade_and_submit

def grade_ex3a(answer: Dict) -> None:
    grade_and_submit(answer, 'ex3', 'partA')

def grade_ex3b(answer: Dict) -> None:
    grade_and_submit(answer, 'ex3', 'partB')
