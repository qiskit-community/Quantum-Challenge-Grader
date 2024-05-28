from typeguard import typechecked

from qiskit import transpile
from qiskit.circuit.random import random_circuit
from qiskit.transpiler import PassManager
from qiskit_ibm_runtime.fake_provider import FakeTorino

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab2_ex1(answer: dict) -> None:
    grade(answer, 'lab2-ex1', _challenge_id)


@typechecked
def grade_lab2_ex2(func: callable) -> None:
    num_qubits = 5
    depth = 5
    qc = random_circuit(num_qubits, depth,measure=True, seed=10000)
    qc_tr = transpile(qc, backend=FakeTorino(), optimization_level=3, seed_transpiler=1000)

    out1 = func(qc_tr, FakeTorino())

    grade({
        'input': qc_tr,
        'output': out1
    }, 'lab2-ex2', _challenge_id)


@typechecked
def grade_lab2_ex3(answer: list) -> None:
    grade(answer, 'lab2-ex3', _challenge_id)


@typechecked
def grade_lab2_ex4(answer: list) -> None:
    grade(answer, 'lab2-ex4', _challenge_id)


@typechecked
def grade_lab2_ex5(answer: PassManager) -> None:
    grade(answer, 'lab2-ex5', _challenge_id, to_bytes=True)
