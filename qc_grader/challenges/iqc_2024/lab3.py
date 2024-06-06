from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit
from qiskit_serverless.core.function import QiskitFunction
from qiskit import QuantumCircuit
from qiskit_serverless.core.job import Job
from qiskit.quantum_info import SparsePauliOp

from qc_grader.grader.grade import grade, get_problem_set
from qiskit_transpiler_service.transpiler_service import TranspilerService

_challenge_id = "iqc_2024"


@typechecked
def grade_lab3_ckt_ex1(circuit: QuantumCircuit) -> None:
    from qiskit_ibm_runtime import SamplerV2 as Sampler
    from qiskit_aer import AerSimulator

    backend = AerSimulator()
    sampler = Sampler(backend)
    job = sampler.run([circuit])
    counts = job.result()[0].data.c.get_counts()

    answer = {"counts": counts, "circuit": circuit}

    grade(answer, "lab3-ckt-ex1", _challenge_id)


@typechecked
def grade_lab3_ckt_ex2(gates_cut: set, swap_depth: int, cut_depth: float) -> None:
    answer = {
        "gates_cut": list(gates_cut),
        "swap_depth": swap_depth,
        "cut_depth": cut_depth,
    }
    grade(answer, "lab3-ckt-ex2", _challenge_id)


@typechecked
def grade_lab3_qs_ex1(
    function: QiskitFunction, input_arguments: dict, job: Job
) -> None:

    check_entry = function.entrypoint
    job_valid = isinstance(job, Job)
    circuit_valid = isinstance(input_arguments["ansatz"], QuantumCircuit)
    op_valid = isinstance(input_arguments["operator"], SparsePauliOp)
    answer = [
        check_entry,
        input_arguments["method"],
        op_valid,
        circuit_valid,
        job_valid,
    ]
    grade(answer, "lab3-qs-ex1", _challenge_id)


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
def grade_lab3_ait_ex2(circuit: QuantumCircuit) -> None:
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
def grade_lab3_qca_ex1(circuit: QuantumCircuit) -> None:
    grade(circuit, "lab3-qca-ex1", _challenge_id)


@typechecked
def grade_lab3_qca_ex2(circuit: QuantumCircuit) -> None:
    grade(circuit, "lab3-qca-ex2", _challenge_id)
