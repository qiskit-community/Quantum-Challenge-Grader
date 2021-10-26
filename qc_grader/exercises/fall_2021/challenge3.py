import pickle

import jsonpickle
import numpy as np
from qiskit.circuit.library import NLocal
from qiskit.quantum_info import Statevector
from qiskit_machine_learning.kernels.quantum_kernel import QuantumKernel
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.svm import SVC
from typeguard import typechecked

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
    pred_public: np.ndarray,
    sample_train: np.ndarray,
    standard_scaler: StandardScaler,
    pca: PCA,
    min_max_scaler: MinMaxScaler,
    kernel_0: QuantumKernel,
    kernel_2: QuantumKernel,
    kernel_3: QuantumKernel,
    svc_0: SVC,
    svc_2: SVC,
    svc_3: SVC
) -> None:
    answer_dict = {
        'pred_public': pred_public,
        'sample_train': sample_train,
        'standard_scaler': standard_scaler,
        'pca': pca,
        'min_max_scaler': min_max_scaler,
        'kernel_0': kernel_0,
        'kernel_2': kernel_2,
        'kernel_3': kernel_3,
        'svc_0': svc_0,
        'svc_2': svc_2,
        'svc_3': svc_3
    }
    answer = pickle.dumps(answer_dict).decode('ISO-8859-1')

    grade_and_submit(answer, '3c')
