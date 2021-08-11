import numpy as np

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

from qc_grader.util import circuit_to_json
from .molecule import molecule_to_json
from .bopess import bopessresult_to_json


def answer_3a(molecule: Molecule) -> None:
    return molecule_to_json(molecule)


def answer_ex3b(q1_answer: str, q2_answer: str) -> None:
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
) -> None:
    steps = perturbation_steps.tolist() if isinstance(perturbation_steps, np.ndarray) else perturbation_steps
    return {
        'energy_surface': energy_surface,
        'molecule': molecule_to_json(molecule),
        'num_electrons': num_electrons,
        'num_molecular_orbitals': num_molecular_orbitals,
        'chemistry_inspired': chemistry_inspired,
        'hardware_inspired_trial': hardware_inspired_trial,
        'vqe': vqe,
        'perturbation_steps': steps,
        'q2_multiple_choice': q2_multiple_choice
    }


def answer_ex3d(q1_answer: str, q2_answer: int) -> None:
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
) -> None:
    answer = {
        'energy_surface_result': bopessresult_to_json(energy_surface_result),
        'molecule': molecule_to_json(molecule),
        'num_electrons': num_electrons,
        'num_molecular_orbitals': num_molecular_orbitals,
        'chemistry_inspired': chemistry_inspired,
        'hardware_inspired_trial': circuit_to_json(hardware_inspired_trial),
        'vqe': vqe,
        'perturbation_steps': perturbation_steps
    }

