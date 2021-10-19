from typing import Dict
from typeguard import typechecked

from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult
from qiskit_nature.runtime import VQEProgram
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem
from qiskit.providers.ibmq.runtime import RuntimeJob

import jsonpickle

from qc_grader.grade import grade_and_submit, prepare_vqe_runtime_program


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
def prepare_ex2f(
    runtime_vqe: VQEProgram,
    qubit_converter: QubitConverter,
    problem: ElectronicStructureProblem
) -> RuntimeJob:
    return prepare_vqe_runtime_program(runtime_vqe, qubit_converter, problem)


@typechecked
def grade_ex2f(job: RuntimeJob) -> None:
    answer = jsonpickle.encode(job.result())
    grade_and_submit(answer, '2f')
