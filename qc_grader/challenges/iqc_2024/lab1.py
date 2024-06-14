from typing import Callable, List
from typeguard import typechecked

import numpy as np
from scipy.optimize._optimize import OptimizeResult

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import PrimitiveJob, PrimitiveResult
from qiskit.providers import JobStatus
from qiskit.circuit.library import EfficientSU2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import EstimatorV2 as Estimator

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab1_ex1(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex1', _challenge_id)


@typechecked
def grade_lab1_ex2(job: PrimitiveJob) -> None:
    status = job.status()
    if status != JobStatus.DONE:
        print(f'Please wait for Job to complete succesfully before grading: {status}')
    else:
        r = job.result()[0]
        grade({
            'metadata': r.metadata,
            'counts': r.data.meas.get_counts()
        }, 'lab1-ex2', _challenge_id)


@typechecked
def grade_lab1_ex3(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex3', _challenge_id)


@typechecked
def grade_lab1_ex4(
    num_qubits: int,
    rotation_blocks: List[str],
    entanglement_blocks: str,
    entanglement: str
) -> None:
    answer = {
        'num_qubits': num_qubits,
        'rotation_blocks': rotation_blocks,
        'entanglement_blocks': entanglement_blocks,
        'entanglement': entanglement
    }
    grade(answer, 'lab1-ex4', _challenge_id)


@typechecked
def grade_lab1_ex5(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab1-ex5', _challenge_id)


@typechecked
def grade_lab1_ex6(cost_func: Callable) -> None:
    ansatz = EfficientSU2(3)
    params = np.ones((1,ansatz.num_parameters))
    aer_sim = AerSimulator()
    pm = generate_preset_pass_manager(backend=aer_sim, optimization_level=2)
    isa_circuits = pm.run(ansatz)
    choc_op = SparsePauliOp(['ZII', 'IZI', 'IIZ'])
    hamiltonian_isa = choc_op.apply_layout(layout=isa_circuits.layout)
    estimator = Estimator(backend=aer_sim)
    
    callback_dict = {
        "prev_vector": None,
        "iters": 0,
        "cost_history": []
    }
    cost, result = cost_func(
        params,
        isa_circuits,
        hamiltonian_isa,
        estimator,
        callback_dict
    )
    if not isinstance(result, PrimitiveResult):
        print('You need to implement code to get a result.')
    else:
        grade({
            'cost': cost,
            'result': {
                'metadata': result[0].metadata,
                'evs': result[0].data.evs
            }
        }, 'lab1-ex6', _challenge_id)


@typechecked
def grade_lab1_ex7(optimize_result: OptimizeResult) -> None:
    grade(dict(optimize_result), 'lab1-ex7', _challenge_id)
