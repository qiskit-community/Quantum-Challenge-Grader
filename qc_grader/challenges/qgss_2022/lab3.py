from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2022'


@typechecked
def grade_lab3_ex1(qc: QuantumCircuit) -> None:
    grade(qc, 'ex3-1', _challenge_id)


@typechecked
def grade_lab3_ex2(zero_state_count: int, one_state_count: int) -> None:
    answer = {
        'zero_state': zero_state_count,
        'one_state': one_state_count
    }
    grade(answer, 'ex3-2', _challenge_id)
