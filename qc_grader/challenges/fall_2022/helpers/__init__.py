from typing import List
import numpy as np

# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Instruction, Parameter
from qiskit.tools.jupyter import *
from qiskit.visualization import *
# Import necessary libraries and packages
import math
import matplotlib.pyplot as plt
import numpy as np

from qiskit import Aer, IBMQ, QuantumCircuit
from qiskit.primitives import Estimator
from qiskit.providers.aer import StatevectorSimulator
from qiskit.utils import QuantumInstance

from qiskit.tools.jupyter import *
from qiskit.visualization import *

# Import Qiskit libraries for VQE
from qiskit.algorithms import MinimumEigensolverResult, VQE
from qiskit.algorithms.optimizers import SLSQP, SPSA

# Import Qiskit Nature libraries
from qiskit_nature.algorithms import GroundStateEigensolver, VQEUCCFactory
from qiskit_nature.algorithms.ground_state_solvers.minimum_eigensolver_factories import NumPyMinimumEigensolverFactory
from qiskit_nature.circuit.library import UCC, UCCSD
from qiskit_nature.drivers import Molecule
from qiskit_nature.drivers.second_quantization import ElectronicStructureDriverType, ElectronicStructureMoleculeDriver
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.mappers.second_quantization import BravyiKitaevMapper, JordanWignerMapper, ParityMapper
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem
from qiskit_nature.transformers.second_quantization.electronic import ActiveSpaceTransformer

from qiskit_nature.settings import settings

settings.dict_aux_operators = True

from qiskit.primitives import BackendEstimator
from qiskit.providers.fake_provider import FakeLagos
from qiskit.providers.aer import AerSimulator
from zne import zne, ZNEStrategy
from zne.extrapolation import PolynomialExtrapolator, LinearExtrapolator, Extrapolator
from zne.noise_amplification import LocalFoldingAmplifier, GlobalFoldingAmplifier, CircuitNoiseAmplifier

def prepare_vqe_run(
    ansatz_list: list, 
    ops_list: list, 
    problem_reduced_list: list,
    initial_point_list: list,
    optimizer_list: list,
    zne_strategy: None or ZNEStrategy
):
    # Keep track of jobs (Do-not-modify)
    sol_list = []
    result_list = []
    job_list = []
    
    if zne_strategy == None:
        estimator = BackendEstimator(backend=FakeLagos())
    else:
        # Define Estimator with the fake backend
        ZNEEstimator = zne(BackendEstimator)
        estimator = ZNEEstimator(backend=FakeLagos(), zne_strategy=zne_strategy)
    
    for i in range(3):
        
        print("Running VQE.......", i+1)
        # Define evaluate_expectation function
        def evaluate_expectation(x):
            x = list(x)
            # Define estimator run parameters
            job = estimator.run(circuits=[ansatz_list[i]], observables=[ops_list[i]], parameter_values=[x]).result()
            results = job.values[0]
            job_list.append(job)

            # Pass results back to optimizer function
            return np.real(results)

        np.random.seed(10)

        # Define initial point. We shall define a random point here based on the number of parameters in our ansatz
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
        