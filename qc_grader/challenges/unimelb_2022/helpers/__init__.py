from typing import Callable, Optional

from qiskit.providers.ibmq.runtime import RuntimeJob
from qiskit.opflow import PauliSumOp
from qiskit.quantum_info import SparsePauliOp

from qiskit_nature.runtime import VQEProgram
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem

from qc_grader.grader.common import get_provider


# for prepare_vqe_runtime_program
# adapted from VQEProgram in Qiskit Nature
# https://github.com/Qiskit/qiskit-nature/blob/0.2.2/qiskit_nature/runtime/vqe_program.py
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
        return runtime_vqe.callback(iteration_count, params, mean, sigma)

    # if callback is set, return wrapped callback, else return None
    if runtime_vqe.callback:
        return wrapped_callback
    else:
        return None


def prepare_vqe_runtime_program(
    runtime_vqe: VQEProgram,
    qubit_converter: QubitConverter,
    problem: ElectronicStructureProblem,
    real_device: bool,
    **kwargs
) -> Optional[RuntimeJob]:
    # overwriting provider and backend if they are not challenge provider and simulator
    challenge_provider = get_provider(hub='ibm-q-education', group='ibm-4')

    if challenge_provider:
        ibmq_qasm_simulator = challenge_provider.get_backend('ibmq_qasm_simulator')
        ibm_perth = challenge_provider.get_backend('ibm_perth')
        ibmq_jakarta = challenge_provider.get_backend('ibmq_jakarta')
        ibm_lagos = challenge_provider.get_backend('ibm_lagos')
        
    else:
        return None

    # check provider is challenge provider, overwrite if otherwise
    if runtime_vqe.provider != challenge_provider:
        print('You are not using the challenge provider. Overwriting provider...')
        runtime_vqe.provider = challenge_provider

    if real_device:
        if runtime_vqe.backend != ibm_perth and runtime_vqe.backend != ibmq_jakarta and runtime_vqe.backend != ibm_lagos):
            print('You are not using the assigned backends, even though you set "real_device=True".\n'+\
                  'Please change your backend setting.')
            return None
    elif runtime_vqe.backend != ibmq_qasm_simulator:
        print('You are not using the ibmq_qasm_simulator backend. Overwriting backend...')
        runtime_vqe.backend = ibmq_qasm_simulator

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
