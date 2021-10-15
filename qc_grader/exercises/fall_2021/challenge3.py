from typeguard import typechecked

import pickle
import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import NLocal

from qc_grader.grade import grade_and_submit


@typechecked
def grade_ex3a(qc: QuantumCircuit) -> None:
    grade_and_submit(qc, '3a')


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
