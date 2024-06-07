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
