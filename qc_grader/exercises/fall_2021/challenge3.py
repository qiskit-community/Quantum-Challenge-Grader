from typeguard import typechecked

import pickle
import jsonpickle
import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import NLocal
from qiskit.quantum_info import Statevector

from qc_grader.grade import grade_and_submit


@typechecked
def grade_ex3a(fmap: NLocal) -> None:
    x = [-0.5, -0.4, 0.3, 0, -0.9]
    qc = fmap.bind_parameters(x)
    statevector = Statevector.from_instruction(qc)

    answer = jsonpickle.encode(statevector)
    grade_and_submit(answer, '3a')


@typechecked
def grade_ex3b(amplitude: float) -> None:
    grade_and_submit(amplitude, '3b')


@typechecked
def grade_ex3c(
    pred_test: np.ndarray,
    fmap_1: NLocal,
    fmap_2: NLocal,
    fmap_3: NLocal,
    n_dim: int
) -> None:
    answer_dict = {
            'pred_test': pred_test,
            'fmap_1': fmap_1,
            'fmap_2': fmap_2,
            'fmap_3': fmap_3,
            'n_dim': n_dim
    }
    answer = pickle.dumps(answer_dict).decode('ISO-8859-1')

    grade_and_submit(answer, '3c')
