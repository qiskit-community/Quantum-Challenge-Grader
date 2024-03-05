from typing import Callable
from typeguard import typechecked

import numpy as np
import pickle

from qiskit.circuit import Instruction
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.grader.grade import grade
from qc_grader.custom_encoder.serializer import paulisumop_to_json


_challenge_id = 'qgss_2022'


@typechecked
def grade_lab4_ex1(answer: PauliSumOp) -> None:
    grade(answer, 'ex4-1', _challenge_id)


@typechecked
def grade_lab4_ex2(compute_U_heis3: Callable) -> None:
    ts = np.linspace(0, np.pi, 100)

    answer = []
    for t in ts:
        op = compute_U_heis3(float(t))

        result = {
            'primitive': paulisumop_to_json(op.primitive),
            'coeff': op.coeff
        }

        answer.append((t, result))

    grade(answer, 'ex4-2', _challenge_id)


@typechecked
def grade_lab4_ex3(inst: Instruction) -> None:
    answer = pickle.dumps(inst).hex(' ', -4)
    grade(answer, 'ex4-3', _challenge_id)


@typechecked
def grade_lab4_ex4(inst: Instruction) -> None:
    answer = pickle.dumps(inst).hex(' ', -4)
    grade(answer, 'ex4-4', _challenge_id)
