from typeguard import typechecked

from qiskit import transpile
from qiskit.circuit.random import random_circuit
from qiskit.transpiler import PassManager, StagedPassManager
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeTorino

from scipy.optimize._optimize import OptimizeResult

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
    grade([
        (len(answer[0].to_flow_controller().tasks), len(answer[0].init.to_flow_controller().tasks), len(answer[0].layout.to_flow_controller().tasks), len(answer[0].routing.to_flow_controller().tasks)),
        (len(answer[1].to_flow_controller().tasks), len(answer[1].init.to_flow_controller().tasks), len(answer[1].layout.to_flow_controller().tasks), len(answer[1].routing.to_flow_controller().tasks)),
        (len(answer[2].to_flow_controller().tasks), len(answer[2].init.to_flow_controller().tasks), len(answer[2].layout.to_flow_controller().tasks), len(answer[2].routing.to_flow_controller().tasks)),
        (len(answer[3].to_flow_controller().tasks), len(answer[3].init.to_flow_controller().tasks), len(answer[3].layout.to_flow_controller().tasks), len(answer[3].routing.to_flow_controller().tasks))   
    ], 'lab2-ex3', _challenge_id)


@typechecked
def grade_lab2_ex4(pm: StagedPassManager) -> None:

    layout_tasks = []
    for controller_group in pm.layout.to_flow_controller().tasks:
        tasks = getattr(controller_group, "tasks", [])
        for task in tasks:  
            layout_tasks.append(str(type(task).__name__))
    
    routing_tasks = []
    for controller_group in pm.routing.to_flow_controller().tasks:
        tasks = getattr(controller_group, "tasks", [])
        for task in tasks:  
            routing_tasks.append(str(type(task).__name__))
    
    translation_tasks = []
    for task in pm.translation.to_flow_controller().tasks:
        translation_tasks.append(type(task).__name__)

    grade({
        'layout_tasks': layout_tasks,
        'routing_tasks': routing_tasks,
        'translation_tasks': translation_tasks
    }, 'lab2-ex4', _challenge_id)


@typechecked
def grade_lab2_ex5(answer: PassManager) -> None:
    grade(answer, 'lab2-ex5', _challenge_id, to_bytes=True)
