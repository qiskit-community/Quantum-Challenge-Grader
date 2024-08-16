from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'fall_fest24'
_grade_only = True


@typechecked
def grade_lab_bonus_ex1(new_mapping_qc: QuantumCircuit) -> None:
    grade(new_mapping_qc.depth(lambda x: len(x.qubits)==2), 'lab-bonus-ex1', _challenge_id, grade_only=_grade_only)


@typechecked
def grade_lab_bonus_ex2(transpiled_qc: QuantumCircuit) -> None:
    grade(transpiled_qc.depth(lambda x: len(x.qubits)==2), 'lab-bonus-ex2', _challenge_id, grade_only=_grade_only)


@typechecked
def grade_lab_bonus_ex3(result_values_list: List[float]) -> None:
    grade(result_values_list, 'lab-bonus-ex3', _challenge_id, grade_only=_grade_only)
