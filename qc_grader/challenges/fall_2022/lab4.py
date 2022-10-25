from typeguard import typechecked
from typing import Callable

import numpy as np

from qiskit.algorithms import MinimumEigensolverResult
from qiskit_nature.drivers import Molecule
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from qiskit_nature import settings

from qc_grader.grader.grade import grade


settings.dict_aux_operators = True
settings.dict_aux_operators = True

_challenge_id = 'fall_2022'


@typechecked
def grade_lab4_ex1(h3p: Molecule) -> None:
    answer = {
        'geometry': h3p.geometry,
        'multiplicity': h3p.multiplicity,
        'charge': h3p.charge
    }

    grade(answer, 'ex4-1', _challenge_id)


@typechecked
def grade_lab4_ex2(
    sol: MinimumEigensolverResult,
    vqe_interpret: list,
    sol_rem: MinimumEigensolverResult,
    vqe_interpret_rem: list
) -> None:
    answer = {
        'vqe_interpret': vqe_interpret[-1],
        'vqe_interpret_rem': vqe_interpret_rem[-1]
    }

    grade(answer, 'ex4-2', _challenge_id)


@typechecked
def grade_lab4_ex3(construct_problem: Callable, custom_vqe: Callable) -> None:

    molecule = [["H", [0.3714,    0.0,    0.0]],
              ["H", [ -0.3714,    0.0,   0.0]]]
    ansatz_m, ops_m, real_solution_m, problem_reduced_m = construct_problem(geometry=molecule, charge=0, multiplicity=1, basis="ccpvdz", num_electrons=2, num_molecular_orbitals=2)
    Energy_H_m, jobs = custom_vqe(ansatz_m, ops_m, problem_reduced_m, noise_model=None)

    answer = {
        'real_solution_m': real_solution_m,
        'Energy_m': Energy_H_m,
        'job': jobs[0]
    }

    grade(answer, 'ex4-3', _challenge_id) 


@typechecked
def grade_lab4_ex4(react_vqe_ev: complex) -> None:
    grade(react_vqe_ev, 'ex4-4', _challenge_id) 


@typechecked
def grade_lab4_ex5(temp_dipoles_dict: dict, temp_nu_dipoles : np.ndarray, dip_tot: float) -> None:
    answer = {
        'temp_dipoles_dict': temp_dipoles_dict,
        'temp_nu_dipoles': temp_nu_dipoles,
        'dip_tot': dip_tot
    }
    grade(answer, 'ex4-5', _challenge_id)
