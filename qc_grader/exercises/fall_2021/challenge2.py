from typing import Any, Dict
from typeguard import typechecked

from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult

import jsonpickle

from qc_grader.grade import grade_and_submit


@typechecked
def grade_ex2a(answer: Dict[str, int]) -> None:
    grade_and_submit(answer, '2a')


@typechecked
def grade_ex2b(answer: Dict[str, int]) -> None:
    grade_and_submit(answer, '2b')


@typechecked
def grade_ex2c(result: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(result)
    grade_and_submit(answer, '2c')


@typechecked
def grade_ex2d(result: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(result)
    grade_and_submit(answer, '2d')


@typechecked
def grade_ex2e(result: ElectronicStructureResult) -> None:
    answer = jsonpickle.encode(result)
    grade_and_submit(answer, '2e')


@typechecked
def grade_ex2f(answer: Any) -> None:
    print('Grading not yet available')
    # grade_and_submit(answer, '2f')
