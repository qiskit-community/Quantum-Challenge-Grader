import numpy as np
import pickle

from typing import Union

from qiskit import QuantumCircuit
from qiskit.circuit.library.n_local import (
    NLocal,
    TwoLocal,
    RealAmplitudes,
    PauliTwoDesign,
    EfficientSU2,
    ExcitationPreserving,
    QAOAAnsatz,
)
from qiskit_nature.drivers import Molecule
from qiskit_nature.results.bopes_sampler_result import BOPESSamplerResult

from qiskit.algorithms import IterativeAmplitudeEstimation
from qiskit.circuit.library import  LinearAmplitudeFunction
from qiskit_finance.circuit.library import LogNormalDistribution

from .molecule import molecule_to_dict
from .bopess import bopessresult_to_dict


def answer_2b(
    uncertainty_model: LogNormalDistribution,
    european_put_objective: LinearAmplitudeFunction,
    ae: IterativeAmplitudeEstimation
) -> dict:
    return {
        'uncertainty_model': pickle.dumps(uncertainty_model).decode('ISO-8859-1'),
        'european_put_objective': pickle.dumps(european_put_objective).decode('ISO-8859-1'),
        'ae': pickle.dumps(ae).decode('ISO-8859-1')
    }


def answer_3a(molecule: Molecule) -> dict:
    return molecule_to_dict(molecule)


def answer_ex3b(q1_answer: str, q2_answer: str) -> dict:
    return {
        'q1_answer': q1_answer,
        'q2_answer': q2_answer
    }


def answer_ex3c(
    energy_surface: list,
    molecule: Molecule,
    num_electrons: int,
    num_molecular_orbitals: int,
    chemistry_inspired: bool,
    hardware_inspired_trial,
    vqe: bool,
    perturbation_steps: list,
    q2_multiple_choice: str
) -> dict:
    steps = perturbation_steps.tolist() if isinstance(perturbation_steps, np.ndarray) else perturbation_steps
    return {
        'energy_surface': energy_surface,
        'molecule': molecule_to_dict(molecule),
        'num_electrons': num_electrons,
        'num_molecular_orbitals': num_molecular_orbitals,
        'chemistry_inspired': chemistry_inspired,
        'hardware_inspired_trial': hardware_inspired_trial,
        'vqe': vqe,
        'perturbation_steps': steps,
        'q2_multiple_choice': q2_multiple_choice
    }


def answer_ex3d(q1_answer: str, q2_answer: int) -> dict:
    return {
        'q1_answer': q1_answer,
        'q2_answer': q2_answer
    }


def answer_ex3e(
    energy_surface_result: BOPESSamplerResult,
    molecule: Molecule,
    num_electrons: int,
    num_molecular_orbitals: int,
    chemistry_inspired: bool,
    hardware_inspired_trial: Union[
        QuantumCircuit,
        NLocal,
        TwoLocal,
        RealAmplitudes,
        PauliTwoDesign,
        EfficientSU2,
        ExcitationPreserving,
        QAOAAnsatz,
    ],
    vqe: bool,
    perturbation_steps: list,
) -> dict:
    return {
        'energy_surface_result': bopessresult_to_dict(energy_surface_result),
        'molecule': molecule_to_dict(molecule),
        'num_electrons': num_electrons,
        'num_molecular_orbitals': num_molecular_orbitals,
        'chemistry_inspired': chemistry_inspired,
        'hardware_inspired_trial': pickle.dumps(hardware_inspired_trial).decode('ISO-8859-1'), #circuit_to_json(hardware_inspired_trial),
        'vqe': vqe,
        'perturbation_steps': perturbation_steps
    }

