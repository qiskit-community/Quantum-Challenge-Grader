from typing import Dict, Union
import jsonpickle

from qc_grader.grade import grade_and_submit

def grade_ex3a(answer: str) -> None:
    grade_and_submit(answer, 'ex3', 'partA')
