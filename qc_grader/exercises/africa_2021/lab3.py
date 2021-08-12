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

from qc_grader.grade import grade_json, submit_json

from .helpers.serialize import (
    answer_3a, answer_ex3b, answer_ex3c, answer_ex3d, answer_ex3e
)


criteria: dict = {}


def grade_ex3a(molecule: Molecule) -> None:
    answer = answer_3a(molecule)
    ok, _ = grade_json(answer, 'ex3', 'partA', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex3b(q1_answer: str, q2_answer: str) -> None:
    answer = answer_ex3b(q1_answer, q2_answer)
    ok, _ = grade_json(answer, 'ex3', 'partB', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex3c(
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
    answer = answer_ex3c(
        energy_surface,
        molecule,
        num_electrons,
        num_molecular_orbitals,
        chemistry_inspired,
        hardware_inspired_trial,
        vqe,
        perturbation_steps,
        q2_multiple_choice
    )
    ok, _ = grade_json(answer, 'ex3', 'partC', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex3d(q1_answer: str, q2_answer: int) -> None:
    answer = answer_ex3d(q1_answer, q2_answer)
    ok, _ = grade_json(answer, 'ex3', 'partD', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex3e(
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
    perturbation_steps: list
) -> None:
    answer = answer_ex3e(
        energy_surface_result,
        molecule,
        num_electrons,
        num_molecular_orbitals,
        chemistry_inspired,
        hardware_inspired_trial,
        vqe,
        perturbation_steps
    )
    ok, _ = grade_json(answer, 'ex3', 'partE', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex3a(molecule: Molecule) -> None:
    answer = answer_3a(molecule)
    submit_json(answer, 'ex3', 'partA', **criteria)


def submit_ex3b(q1_answer: str, q2_answer: str) -> None:
    answer = answer_ex3b(q1_answer, q2_answer)
    submit_json(answer, 'ex3', 'partB', **criteria)


def submit_ex3c(
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
    answer = answer_ex3c(
        energy_surface,
        molecule,
        num_electrons,
        num_molecular_orbitals,
        chemistry_inspired,
        hardware_inspired_trial,
        vqe,
        perturbation_steps,
        q2_multiple_choice
    )
    submit_json(answer, 'ex3', 'partC', **criteria)


def submit_ex3d(q1_answer: str, q2_answer: int) -> None:
    answer = answer_ex3d(q1_answer, q2_answer)
    submit_json(answer, 'ex3', 'partD', **criteria)


def submit_ex3e(
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
    answer = answer_ex3e(
        energy_surface_result,
        molecule,
        num_electrons,
        num_molecular_orbitals,
        chemistry_inspired,
        hardware_inspired_trial,
        vqe,
        perturbation_steps,
    )
    submit_json(answer, 'ex3', 'partE', **criteria)
