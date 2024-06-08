from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

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
    isa_qpd_toffoli_depth_mean: float,
) -> None:
    answer = {
        "gates_cut": list(gates_connecting_to_cut),
        "swap_depth": isa_toffoli_depth,
        "cut_depth": isa_qpd_toffoli_depth_mean,
    }
    grade(answer, "lab3-ckt-ex1", _challenge_id)


@typechecked
def grade_lab3_ckt_ex2(
    gates_connecting_to_cut_1: set,
    gates_connecting_to_cut_2: set,
    n_sub_experiment: int,
    isa_qpd_toffoli_depth_2_mean: float,
) -> None:
    answer = {
        "gates_cut": list(gates_connecting_to_cut_1),
        "gates_cut": list(gates_connecting_to_cut_2),
        "n_sub_exp": n_sub_experiment,
        "cut_depth": isa_qpd_toffoli_depth_2_mean,
    }
    grade(answer, "lab3-ckt-ex2", _challenge_id)
