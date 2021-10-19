from typing import Any, Dict, Optional, Callable
from typeguard import typechecked

from qiskit_nature.results.electronic_structure_result import ElectronicStructureResult
from qiskit_nature.runtime import VQEProgram
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.providers.ibmq.runtime import RuntimeJob
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


from qiskit.opflow import PauliSumOp
from qiskit.quantum_info import SparsePauliOp
def _convert_to_paulisumop(operator):
    """Attempt to convert the operator to a PauliSumOp."""
    if isinstance(operator, PauliSumOp):
        return operator

    try:
        primitive = SparsePauliOp(operator.primitive)
        return PauliSumOp(primitive, operator.coeff)
    except Exception as exc:
        raise ValueError(
            f"Invalid type of the operator {type(operator)} "
            "must be PauliSumOp, or castable to one."
        ) from exc


def _wrap_vqe_callback(runtime_vqe) -> Optional[Callable]:
    """Wraps and returns the given callback to match the signature of the runtime callback."""

    def wrapped_callback(*args):
        _, data = args  # first element is the job id
        iteration_count = data[0]
        params = data[1]
        mean = data[2]
        sigma = data[3]
        return runtime_vqe._callback(iteration_count, params, mean, sigma)

    # if callback is set, return wrapped callback, else return None
    if runtime_vqe._callback:
        return wrapped_callback
    else:
        return None


@typechecked
def prepare_ex2f(
        runtime_vqe: VQEProgram,
        qubit_converter: QubitConverter,
        problem: ElectronicStructureProblem
) -> RuntimeJob:
    # check provider
    # check backend
    # create ground state solver
    # execute experiments
    print('Starting experiment. Please wait...')
    second_q_ops = problem.second_q_ops()

    operator = qubit_converter.convert(
        second_q_ops[0],
        num_particles=problem.num_particles,
        sector_locator=problem.symmetry_sector_locator,
    )
    aux_operators = qubit_converter.convert_match(second_q_ops[1:])

    # try to convert the operators to a PauliSumOp, if it isn't already one
    operator = _convert_to_paulisumop(operator)
    if aux_operators is not None:
        aux_operators = [_convert_to_paulisumop(aux_op) for aux_op in aux_operators]

    # combine the settings with the given operator to runtime inputs
    inputs = {
        "operator": operator,
        "aux_operators": aux_operators,
        "ansatz": runtime_vqe.ansatz,
        "optimizer": runtime_vqe.optimizer,
        "initial_point": runtime_vqe.initial_point,
        "shots": runtime_vqe.shots,
        "measurement_error_mitigation": runtime_vqe.measurement_error_mitigation,
        "store_intermediate": runtime_vqe.store_intermediate,
    }

    # define runtime options
    options = {"backend_name": runtime_vqe.backend.name()}

    # send job to runtime and return result
    job = runtime_vqe.provider.runtime.run(
        program_id='vqe',
        inputs=inputs,
        options=options,
        callback=_wrap_vqe_callback(runtime_vqe),
    )

    print(f'You may monitor the job (id: {job.job_id()}) status '
          'and proceed to grading when it successfully completes.')

    return job

    
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
