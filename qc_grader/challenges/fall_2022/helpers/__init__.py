# Importing standard Qiskit libraries
from qiskit.tools.jupyter import *
from qiskit.visualization import *

# Import necessary libraries and packages
import numpy as np
from typing import Union

# Import Qiskit libraries for VQE
from qiskit.algorithms import MinimumEigensolverResult
from qiskit.algorithms.optimizers import SPSA

from qiskit.primitives import BackendEstimator
from qiskit.providers.fake_provider import FakeLagos
from zne import zne, ZNEStrategy

# Import Qiskit Nature libraries
from qiskit_nature.settings import settings

settings.dict_aux_operators = True


def prepare_vqe_run(
    ansatz_list: list,
    ops_list: list,
    problem_reduced_list: list,
    initial_point_list: list,
    optimizer_list: list,
    zne_strategy: Union[ZNEStrategy, None]
):
    # Keep track of jobs (Do-not-modify)
    sol_list = []
    result_list = []
    job_list = []
    
    backend = FakeLagos()
    backend.set_options(seed_simulator=1024)

    if zne_strategy is None:
        estimator = BackendEstimator(backend=backend)
    else:
        # Define Estimator with the fake backend
        ZNEEstimator = zne(BackendEstimator)
        estimator = ZNEEstimator(backend=backend, zne_strategy=zne_strategy)

    for i in range(3):
        print("Running VQE.......", i+1)

        # Define evaluate_expectation function
        def evaluate_expectation(x):
            x = list(x)
            # Define estimator run parameters
            job = estimator.run(
                circuits=[ansatz_list[i]],
                observables=[ops_list[i]],
                parameter_values=[x]
            ).result()
            results = job.values[0]
            job_list.append(job)

            # Pass results back to optimizer function
            return np.real(results)

        np.random.seed(10)

        # Define initial point.
        # We shall define a random point here based on the number of parameters in our ansatz
        if initial_point_list[i] is None:
            initial_point_list[i] = np.random.random(ansatz_list[i].num_parameters)

        # Define optimizer and pass callback function
        if optimizer_list[i] is None:
            optimizer_list[i] = SPSA(maxiter=1)

        # Define minimize function
        result = optimizer_list[i].minimize(evaluate_expectation, x0=initial_point_list[i])
        result_list.append(result)

        sol = MinimumEigensolverResult()
        sol.eigenvalue = result.fun
        sol = problem_reduced_list[i].interpret(sol).total_energies[0]
        sol_list.append(sol.real)

        print(f"VQE run {i+1} complete")
        print(f"Converged value for run {i+1} is: {sol}")
        print(f"Result for run {i+1}: {result} \n")

    return result_list, sol_list, job_list
