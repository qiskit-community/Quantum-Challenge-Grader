from typeguard import typechecked
from typing import List

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import IBMBackend
from qiskit.primitives.containers.bindings_array import BindingsArray

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2024'


@typechecked
def grade_lab2_ex1(
    answer: List, backend
) -> None:
    grade({
        'cmap': list(backend.coupling_map) if backend.coupling_map is not None else [],
        'answer': answer,
    }, 'lab2-ex1', _challenge_id)


@typechecked
def grade_lab2_ex2(
    layer1: List, layer2: List, path: List, backend
) -> None:
    grade({
        'layer1': layer1,
        'layer2': layer2,
        'path': path,
        'cmap': list(backend.coupling_map) if backend.coupling_map is not None else []
    }, 'lab2-ex2', _challenge_id)


@typechecked
def grade_lab2_ex3(
    circuit: QuantumCircuit, layer: List, gate_name: str, backend
) -> None:
    grade({
        'qc': circuit,
        'layer': layer,
        'gate_name': gate_name,
        'cmap': list(backend.coupling_map) if backend.coupling_map is not None else [],
    }, 'lab2-ex3', _challenge_id)


@typechecked
def grade_lab2_ex4(
    array_answer: BindingsArray,
    circ: QuantumCircuit,
    num_samples: int,
) -> None:
    if not isinstance(array_answer, BindingsArray):
        print(f"the answer need to be put into the `BindingsArray` type")
    else:
        grade({
            'BindingsArray.shape': array_answer.shape,
            'BindingsArray.num_parameters': array_answer.num_parameters,
            'BindingsArrayangles.as_array': array_answer.as_array(),
            'QuantumCircuit.num_parameters': circ.num_parameters,
            'num_samples': num_samples
        }, 'lab2-ex4', _challenge_id)
