from typing import Any
import jsonpickle
import numpy as np

from qiskit.circuit.library import NLocal

from qc_grader.grade import grade_and_submit
from qc_grader.util import circuit_to_json


def grade_ex3a(pred_test: np.ndarray, fmap_1: NLocal, fmap_2: NLocal, fmap_3: NLocal, n_dim: int) -> None:
    answer_dict = {
            'pred_test': pred_test,
            'fmap_1': circuit_to_json(fmap_1),
            'fmap_2': circuit_to_json(fmap_2),
            'fmap_3': circuit_to_json(fmap_3),
            'n_dim': n_dim
    }
    answer = jsonpickle.encode(answer_dict)

    grade_and_submit(answer, 'ex3', 'partA')
