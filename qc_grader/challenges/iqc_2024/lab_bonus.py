from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab_bonus_ex1(new_mapping_qc: QuantumCircuit) -> None:
    grade(new_mapping_qc.depth(lambda x: len(x.qubits)==2), 'lab-bonus-ex1', _challenge_id)


@typechecked
def grade_lab_bonus_ex2(transpiled_qc: QuantumCircuit) -> None:
    grade(transpiled_qc.depth(lambda x: len(x.qubits)==2), 'lab-bonus-ex2', _challenge_id)


@typechecked
def grade_lab_bonus_ex3(result_values_list: List[float]) -> None:
    grade(result_values_list, 'lab-bonus-ex3', _challenge_id)
