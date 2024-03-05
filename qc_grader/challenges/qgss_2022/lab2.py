import numpy
import pickle

from typing import List
from qiskit import QuantumCircuit
from typeguard import typechecked

from qiskit.circuit import Parameter
from qiskit.opflow.primitive_ops.circuit_op import CircuitOp
from qiskit.opflow.evolutions.evolved_op import EvolvedOp
from qiskit.opflow.primitive_ops import PauliOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp

from qc_grader.grader.grade import grade
from qc_grader.custom_encoder.serializer import (
    circuit_to_json,
    pauliop_to_json,
    paulisumop_to_json
)


_challenge_id = 'qgss_2022'


@typechecked
def grade_lab2_ex1(op_list: List[PauliOp]) -> None:
    answer = [
        pauliop_to_json(p) for p in op_list
    ]
    grade(answer, 'ex2-1', _challenge_id)


@typechecked
def grade_lab2_ex2(op_list: List[PauliSumOp]) -> None:
    answer = [
        paulisumop_to_json(p) for p in op_list
    ]
    grade(answer, 'ex2-2', _challenge_id)


@typechecked
def grade_lab2_ex3(numpy_list: List[numpy.ndarray]) -> None:
    grade(numpy_list, 'ex2-3', _challenge_id)


@typechecked
def grade_lab2_ex4(qc_list: List[QuantumCircuit]) -> None:
    answer = [
        circuit_to_json(qc) for qc in qc_list
    ]
    grade(answer, 'ex2-4', _challenge_id)


@typechecked
def grade_lab2_ex5(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-5', _challenge_id, byte_string=True)


@typechecked
def grade_lab2_ex6(qc: QuantumCircuit) -> None:
    grade(qc, 'ex2-6', _challenge_id, byte_string=True)


@typechecked
def grade_lab2_ex7(answer: numpy.ndarray) -> None:
    grade(answer, 'ex2-7', _challenge_id)


@typechecked
def grade_lab2_ex8(op: EvolvedOp) -> None:
    answer = {
        'primitive': paulisumop_to_json(op.primitive),
        'coeff': op.coeff,
        'primitive_coeff': str(op.primitive.coeff)
    }
    grade(answer, 'ex2-8', _challenge_id)


@typechecked
def grade_lab2_ex9(op: CircuitOp) -> None:
    answer = pickle.dumps(op).hex(' ', -4)
    grade(answer, 'ex2-9', _challenge_id)


@typechecked
def grade_lab2_ex10(op: CircuitOp) -> None:
    answer = pickle.dumps(op).hex(' ', -4)
    grade(answer, 'ex2-10', _challenge_id)


@typechecked
def grade_lab2_ex11(op: CircuitOp) -> None:
    answer = pickle.dumps(op).hex(' ', -4)
    grade(answer, 'ex2-11', _challenge_id)


@typechecked
def grade_lab2_ex12(qc: QuantumCircuit) -> None:
    answer = pickle.dumps(qc).hex(' ', -4)
    grade(answer, 'ex2-12', _challenge_id)
