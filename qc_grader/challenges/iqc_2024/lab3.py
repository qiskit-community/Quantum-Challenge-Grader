from typeguard import typechecked

from typing import Callable, List
import numpy as np

from qiskit import QuantumCircuit
from qiskit_serverless.core.job import Job
from qiskit.quantum_info import SparsePauliOp
from qiskit_serverless.core.function import QiskitFunction


from qc_grader.grader.grade import grade, get_problem_set
from qiskit_transpiler_service.transpiler_service import TranspilerService

_challenge_id = "iqc_2024"


@typechecked
def grade_lab3_ait_ex1(transpiler_ai_false: TranspilerService) -> None:
    grade(
        [
            transpiler_ai_false.ai,
            transpiler_ai_false.backend_name,
            transpiler_ai_false.optimization_level,
        ],
        "lab3-ait-ex1",
        _challenge_id,
    )


@typechecked
def grade_lab3_ait_ex2(transpiler_ai_true: TranspilerService) -> None:
    grade(
        [
            transpiler_ai_true.ai,
            transpiler_ai_true.backend_name,
            transpiler_ai_true.optimization_level,
        ],
        "lab3-ait-ex2",
        _challenge_id,
    )


@typechecked
def grade_lab3_ckt_ex1(
    gates_connecting_to_cut: set,
    isa_toffoli_depth: int,
    depth_list: np.ndarray | List,
) -> None:

    if isinstance(depth_list, List):
        depth_list = np.array(depth_list)

    answer = {
        "gates_cut": list(gates_connecting_to_cut),
        "swap_depth": isa_toffoli_depth,
        "cut_depth": depth_list.mean(),
    }
    grade(answer, "lab3-ckt-ex1", _challenge_id)


@typechecked
def grade_lab3_ckt_ex2(
    gates_connecting_to_cut_1: set,
    gates_connecting_to_cut_2: set,
    sub_experiments: List[QuantumCircuit],
) -> None:
    answer = {
        "gates_cut_1": list(gates_connecting_to_cut_1),
        "gates_cut_2": list(gates_connecting_to_cut_2),
        "n_sub_exp": len(sub_experiments),
    }
    grade(answer, "lab3-ckt-ex2", _challenge_id)


@typechecked
def grade_lab3_qs_ex1(
    function: QiskitFunction, input_arguments: dict, job: Job
) -> None:
    answer = {
        "check_entry": function.entrypoint,
        "optimizer": input_arguments["method"],
        "op_valid": isinstance(input_arguments["operator"], SparsePauliOp),
        "circuit_valid": isinstance(input_arguments["ansatz"], QuantumCircuit),
        "job_valid": isinstance(job, Job)
    }
    grade(answer, "lab3-qs-ex1", _challenge_id)


@typechecked
def grade_lab3_qs_ex2(
    optimization_levels: list,
    transpiler_services: list,
    transpile_parallel_function: QiskitFunction,
    transpile_parallel_serverless: QiskitFunction,
    job: Job,
) -> None:

    transpiler_service_settings = [
        {
            "ai": service["service"].ai,
            "backend_name": service["service"].backend_name,
            "optimization_level": service["service"].optimization_level,
        }
        for service in transpiler_services
    ]
    config = {
        "title": transpile_parallel_serverless.raw_data["title"],
        "entrypoint": transpile_parallel_serverless.raw_data["entrypoint"],
    }

    answer = {
        'optimization_levels': optimization_levels,
        'transpiler_service_settings': transpiler_service_settings,
        'entrypoint': transpile_parallel_function.entrypoint,
        'config': config,
        'job_valid': isinstance(job, Job),
    }
    grade(answer, "lab3-qs-ex2", _challenge_id)
