from typing import Dict, Union

from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult

import jsonpickle

from qc_grader.grade import grade_and_submit

def grade_ex3a(answer: Dict) -> None:
    grade_and_submit(answer, 'ex3', 'partA')

def grade_ex3b(answer: Dict) -> None:
    grade_and_submit(answer, 'ex3', 'partB')

def grade_ex3c(numpy_results: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(numpy_results)
    grade_and_submit(answer, 'ex3', 'partC')
