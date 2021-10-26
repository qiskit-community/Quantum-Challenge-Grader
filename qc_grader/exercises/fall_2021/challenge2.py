from typing import Dict, Optional

import jsonpickle
from qiskit.providers import JobStatus
from qiskit.providers.ibmq.runtime import RuntimeJob
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem
from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult
from qiskit_nature.runtime import VQEProgram
from typeguard import typechecked

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
        problem: ElectronicStructureProblem,
        real_device: bool = False
) -> Optional[RuntimeJob]:
    return prepare_vqe_runtime_program(runtime_vqe, qubit_converter, problem, real_device)


@typechecked
def grade_ex2f(job: RuntimeJob) -> None:
    job_status = job.status()
    if job_status in [JobStatus.CANCELLED, JobStatus.ERROR]:
        print(f'Job did not successfully complete: {job_status.value}.')
    elif job_status is not JobStatus.DONE:
        print(f'Job has not yet completed: {job_status.value}.')
        print(f'Please wait for the job (id: {job.job_id()}) to complete then try again.')
    else:
        answer = jsonpickle.encode(job.result())
        grade_and_submit(answer, '2f')
