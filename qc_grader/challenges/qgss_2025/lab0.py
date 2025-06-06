from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2025'


@typechecked
def grade_lab0_ex1(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab0-ex1', _challenge_id)


@typechecked
def grade_lab0_ex2(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab0-ex2', _challenge_id)
