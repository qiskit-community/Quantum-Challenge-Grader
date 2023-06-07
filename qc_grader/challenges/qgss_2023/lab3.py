from typeguard import typechecked

from typing import List, Dict, Callable
from fractions import Fraction
from qiskit.quantum_info import Operator

from qiskit.quantum_info import Operator
from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2023'


@typechecked
def grade_lab3_ex1(count_data: Dict) -> None:
    grade(count_data, 'ex3-1', _challenge_id)

@typechecked
def grade_lab3_ex2(answer_list : List) -> None:
    grade(answer_list, 'ex3-2', _challenge_id)

@typechecked
def grade_lab3_ex3(qpe_circuits : List[QuantumCircuit]) -> None:
    min_depth_qpe = qpe_circuits[0]
    max_depth_qpe = qpe_circuits[1]

    min_depth_ops = sum([val for key, val in min_depth_qpe.count_ops().items()])
    max_depth_ops = sum([val for key, val in max_depth_qpe.count_ops().items()])

    grade([min_depth_ops, max_depth_ops], 'ex3-3', _challenge_id)


@typechecked
def grade_lab3_ex4(required_register_size : int) -> None:
    grade(required_register_size, 'ex3-4', _challenge_id)

@typechecked
def grade_lab3_ex5(count_data_list : List[Dict]) -> None:
    grade(count_data_list, 'ex3-5', _challenge_id)

@typechecked
def grade_lab3_ex6(unitary_result: Operator) -> None:
    unitary_result_data = unitary_result.data
    grade(unitary_result_data, 'ex3-6', _challenge_id)

@typechecked
def grade_lab3_ex7(shor_qpe_counts : Dict) -> None:
    grade(shor_qpe_counts, 'ex3-7', _challenge_id)

@typechecked
def grade_lab3_ex8(fraction_integers: List[Fraction]) -> None:
    grade(fraction_integers, 'ex3-8', _challenge_id)

@typechecked
def grade_lab3_ex9(shor_qpe: Callable) -> None:
    _, inputs = get_problem_set('ex3-9', _challenge_id)

    shor_qpe_results = shor_qpe(inputs[0], inputs[1])
    grade(shor_qpe_results, 'ex3-9', _challenge_id)
