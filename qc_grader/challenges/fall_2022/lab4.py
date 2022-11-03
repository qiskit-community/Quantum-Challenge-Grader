from typeguard import typechecked
from typing import Callable, Optional

import numpy as np

from qiskit.algorithms.optimizers.optimizer import OptimizerResult
from qiskit_nature.drivers import Molecule
from qiskit.primitives import Estimator
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from qiskit_nature import settings

from qc_grader.grader.grade import grade, get_problem_set

from .helpers import prepare_vqe_run

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
    result: OptimizerResult,
    vqe_interpret: list
) -> None:
    answer = {
        'vqe_interpret': vqe_interpret[-1].real,
        'result': result.fun
    }

    grade(answer, 'ex4-2', _challenge_id)


@typechecked
def grade_lab4_ex3(construct_problem: Callable, custom_vqe: Callable) -> None:
    from qiskit.utils import algorithm_globals
    algorithm_globals.random_seed = 12

    estimator = Estimator()
    _, molecule = get_problem_set('ex4-3', _challenge_id)
    ansatz_m, ops_m, real_solution_m, problem_reduced_m = construct_problem(
        geometry=molecule,
        charge=0,
        multiplicity=1,
        basis="ccpvdz",
        num_electrons=2,
        num_molecular_orbitals=2
    )
    Energy_H_m, jobs, result_m = custom_vqe(
        estimator, ansatz_m, ops_m, problem_reduced_m
    )

    answer = {
        'real_solution_m': real_solution_m,
        'Energy_m': Energy_H_m[-1].real,
        'job': len(jobs)
    }

    grade(answer, 'ex4-3', _challenge_id)


@typechecked
def grade_lab4_ex4(react_vqe_ev: complex) -> None:
    grade(react_vqe_ev, 'ex4-4', _challenge_id)


@typechecked
def grade_lab4_ex5(
    temp_dipoles_dict: dict,
    temp_nu_dipoles: np.ndarray,
    dip_tot: float
) -> None:
    answer = {
        'temp_dipoles_dict': temp_dipoles_dict,
        'temp_nu_dipoles': temp_nu_dipoles,
        'dip_tot': dip_tot
    }
    grade(answer, 'ex4-5', _challenge_id)


@typechecked
def grade_lab4_final(
    ansatz_list: list,
    ops_list: list,
    problem_reduced_list: list,
    initial_point_list: Optional[list] = [None, None, None],
    optimizer_list: Optional[list] = [None, None, None],
    zne_strategy=None
):
    result_list, sol_list, job_list = prepare_vqe_run(
        ansatz_list,
        ops_list,
        problem_reduced_list,
        initial_point_list,
        optimizer_list,
        zne_strategy
    )

    grade(result_list, sol_list, job_list, 'ex4-6', _challenge_id)
