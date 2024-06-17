import json

from typing import Callable, Type

from typeguard import typechecked


from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Gate
from qiskit.circuit.library import QFT
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import StagedPassManager, CouplingMap, AnalysisPass, TransformationPass

from qc_grader.grader.grade import grade
from .utils import get_qc_in


_challenge_id = 'qgss_2024'


# Lab 1, Exercise 1A
@typechecked
def grade_lab1_ex1(qc_char_func: Callable) -> None:
    if not callable(qc_char_func):
        print("Please supply the function that determines circuit characteristics as specified")
        return
    
    qc = QFT(5)
    qc = transpile(qc, GenericBackendV2(5), seed_transpiler=307)
    qc_info = qc_char_func(qc)

    if not isinstance(qc_info, dict):
        print("The circuit characteristics should be returned in the form of a dictionary as specified.")
        return

    grade({
        'qc': qc,
        'qc_info': qc_info
    }, 'lab1-ex1', _challenge_id)


# Lab 1, Exercise 1B
@typechecked
def grade_lab1_ex2(qc_routed: QuantumCircuit) -> None:
    if not isinstance(qc_routed, QuantumCircuit):
        print("Input should be one single quantum circuit! Given:", type(qc_routed))
        return

    grade(qc_routed, 'lab1-ex2', _challenge_id)


# Lab 1, Exercise 2A
@typechecked
def grade_lab1_ex3(pm_staged: StagedPassManager) -> None:
    if not isinstance(pm_staged, StagedPassManager):
        print("Input should a staged pass manager! Given:", type(pm_staged))
        return

    num_qubits = 10
    qc = QFT(num_qubits, do_swaps=False)
    qc_out = pm_staged.run(qc)

    grade({
        'qc_out': qc_out
    }, 'lab1-ex3', _challenge_id)


# Lab 1, Exercise 2B
@typechecked
def grade_lab1_ex4(pm_staged: StagedPassManager) -> None:
    if not isinstance(pm_staged, StagedPassManager):
        print("Input should a staged pass manager! Given:", type(pm_staged))
        return

    num_qubits = 10
    qc = QFT(num_qubits, do_swaps=False)
    qc_out = pm_staged.run(qc)

    grade({
        'qc_out': qc_out
    }, 'lab1-ex4', _challenge_id)


# Lab 1, Exercise 2C
@typechecked
def grade_lab1_ex5(pm_staged: StagedPassManager) -> None:
    if not isinstance(pm_staged, StagedPassManager):
        print("Input should a staged pass manager! Given:", type(pm_staged))
        return

    num_qubits = 10
    qc = QFT(num_qubits, do_swaps=False)
    qc_out = pm_staged.run(qc)
    qc_qk = transpile(qc, backend=GenericBackendV2(num_qubits, coupling_map=CouplingMap.from_line(num_qubits)), seed_transpiler=307)
    opt_cx_count = qc_out.num_nonlocal_gates()
    qk_cx_count = qc_qk.num_nonlocal_gates()

    grade({
        'qc_out': qc_out,
        'opt_cx_count': opt_cx_count,
        'qk_cx_count': qk_cx_count
    }, 'lab1-ex5', _challenge_id)


def qs_to_ind(q_dict):
    return {q._index: v for q, v in q_dict.items()}
    
# Lab 1, Exercise 3A
@typechecked
def grade_lab1_ex6(user_pass_class: Type[AnalysisPass]) -> None:
    num_qubits = 5
    qc = transpile(QFT(num_qubits, do_swaps=False), backend=GenericBackendV2(num_qubits, coupling_map=CouplingMap.from_line(num_qubits)), seed_transpiler=307)
    user_pass = user_pass_class()
    user_pass(qc)

    grade({
        'userpass': [qs_to_ind(user_pass.property_set["one_q_op"]), qs_to_ind(user_pass.property_set["two_q_op"])],
        'qc': qc
    }, 'lab1-ex6', _challenge_id)


# Lab 1, Exercise 3B
@typechecked
def grade_lab1_ex7(user_pass_class: Type[TransformationPass], pg: Gate) -> None:
    nq = 5
    qc = get_qc_in(nq, pg)
    user_pass = user_pass_class()
    qc_user = user_pass(qc)

    grade({
        'qc': qc,
        'qc_user': qc_user
    }, 'lab1-ex7', _challenge_id)


# Lab 1, Exercise 3C
@typechecked
def grade_lab1_ex8(user_pass: Type[TransformationPass], pg: Gate) -> None:
    nq = 5
    qc = get_qc_in(nq)
    qc_user = user_pass(qc)

    correct, _, characteristics = grade({
        'qc': qc,
        'qc_user': qc_user
    }, 'lab1-ex8', _challenge_id, return_response=True)

    if not correct:
        print(f'\nOops 😕! {"Your answer is incorrect" if characteristics is None else characteristics}')
    else:
        print('\nCongratulations 🎉! Your answer is correct.')
        print(f'characteristics:', json.loads(characteristics))
    return characteristics
