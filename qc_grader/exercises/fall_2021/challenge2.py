from typing import Any, Dict
from typeguard import typechecked

from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult
from qiskit_nature.runtime import VQEProgram
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem
from qiskit.providers.ibmq.job import IBMQJob
from qiskit_nature.algorithms.ground_state_solvers import GroundStateEigensolver

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
def grade_ex2f(
        runtime_vqe: VQEProgram,
        qubit_converter: QubitConverter,
        problem: ElectronicStructureProblem
) -> None:
    # check provider
    # check backend
    # create ground state solver
    runtime_gse = GroundStateEigensolver(qubit_converter, runtime_vqe)
    print('Running VQE Runtime job, this can take a few minutes.')
    runtime_vqe_results = runtime_gse.solve(problem)

    answer = jsonpickle.encode(runtime_vqe_results)
    grade_and_submit(answer, '2f')
