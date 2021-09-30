from typing import Dict, Union

from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult

import jsonpickle

from qc_grader.grade import grade_and_submit

def grade_ex2a(answer: Dict) -> None:
    grade_and_submit(answer, 'ex2', 'partA')

def grade_ex2b(answer: Dict) -> None:
    grade_and_submit(answer, 'ex2', 'partB')

def grade_ex2c(numpy_results: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(numpy_results)
    grade_and_submit(answer, 'ex2', 'partC')

def grade_ex2d(vqe_results: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(vqe_results)
    grade_and_submit(answer, 'ex2', 'partD')

def grade_ex2e(qeom_results: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(qeom_results)
    grade_and_submit(answer, 'ex2', 'partE')
