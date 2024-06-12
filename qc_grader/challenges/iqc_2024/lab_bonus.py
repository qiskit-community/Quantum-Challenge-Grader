from typing import List
from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab_bonus_ex1(new_mapping_qc: QuantumCircuit, transpiled_qc: QuantumCircuit, result_values_list: List[float]) -> None:

    answer = {
        'mapping_qc_depth': new_mapping_qc.depth(),
        'transpiled_qc_cx_depth': transpiled_qc.depth(lambda x: len(x.qubits)==2),
        'result_values_list': result_values_list
    }
    grade(answer, 'lab-bonus-ex1', _challenge_id)
