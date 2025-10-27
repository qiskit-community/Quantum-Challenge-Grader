from typeguard import typechecked

from qiskit import QuantumCircuit
from .lattice import HeavyHexLattice
from qc_grader.grader.grade import grade
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime import EstimatorV2
import numpy
from typing import List
import json

from math import pi

from collections import OrderedDict
from typing import List

import numpy as np

from qiskit import QuantumCircuit
import qiskit_ibm_runtime
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime.runtime_job_v2 import RuntimeJobV2
from qiskit_aer.primitives.estimator_v2 import EstimatorV2
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from qiskit.quantum_info import Statevector, SparsePauliOp
from qiskit.quantum_info import Operator
from qiskit.circuit.library import TwoLocal
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.primitives import StatevectorEstimator

from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKyoto
from qiskit import qpy


_challenge_id = "qdc_2025"

@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status == False:
        print(message)
    else:
        print("Team name submitted.")

@typechecked
def grade_lab3_ex1(mps_energies_t0: numpy.ndarray, mps_wp_circ_t0: QuantumCircuit) -> None:

    answer_dict = {
        "mps_energies_t0": mps_energies_t0,
        "mps_wp_circ_t0": mps_wp_circ_t0,
    }

    grade(answer_dict, "lab3-ex1", _challenge_id)

@typechecked
def grade_lab3_ex2(mps_energies_t4: numpy.ndarray, mps_wp_circ_t4: QuantumCircuit, mps_vac_circ_t4:QuantumCircuit) -> None:

    answer_dict = {
        "mps_energies_t4": mps_energies_t4,
        "mps_wp_circ_t4": mps_wp_circ_t4,
        "mps_vac_circ_t4": mps_vac_circ_t4
    }

    grade(answer_dict, "lab3-ex2", _challenge_id)

@typechecked
def grade_lab3_ex3(t: float, hardware_wp_circ: QuantumCircuit, hardware_vac_circ: QuantumCircuit) -> None:

    answer_dict = {
            "t": t,
            "hardware_wp_circ": hardware_wp_circ,
            "hardware_vac_circ": hardware_vac_circ
        }

    grade(answer_dict, "lab3-ex3", _challenge_id)

@typechecked
def grade_lab3_ex4(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, raw_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "raw_energies": raw_energies
        }
    
    grade(answer_dict, "lab3-ex4", _challenge_id)

@typechecked
def grade_lab3_ex5(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, mit_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "mit_energies": mit_energies
        }
    
    grade(answer_dict, "lab3-ex5", _challenge_id)

@typechecked
def grade_lab3_ex6(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, mit_sym_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "mit_sym_energies": mit_sym_energies
        }
    
    grade(answer_dict, "lab3-ex6", _challenge_id)


@typechecked
def grade_lab3_ex7(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, rescaled_mit_sym_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "rescaled_mit_sym_energies": rescaled_mit_sym_energies
        }
    
    grade(answer_dict, "lab3-ex7", _challenge_id)

@typechecked
def grade_lab3_ex8(t: float, best_wp_circ: QuantumCircuit, best_vac_circ: QuantumCircuit, best_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "best_wp_circ": best_wp_circ,
            "best_vac_circ": best_vac_circ,
            "best_energies": best_energies
        }
    
    grade(answer_dict, "lab3-ex8", _challenge_id)

def grade_lab3_ex9(t: float, hardware_wp_circ: QuantumCircuit, hardware_vac_circ: QuantumCircuit) -> None:

    answer_dict = {
            "t": t,
            "hardware_wp_circ": hardware_wp_circ,
            "hardware_vac_circ": hardware_vac_circ
        }

    grade(answer_dict, "lab3-ex9", _challenge_id)

@typechecked
def grade_lab3_ex10(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, raw_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "raw_energies": raw_energies
        }
    
    grade(answer_dict, "lab3-ex10", _challenge_id)

@typechecked
def grade_lab3_ex11(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, mit_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "mit_energies": mit_energies
        }
    
    grade(answer_dict, "lab3-ex11", _challenge_id)


@typechecked
def grade_lab3_ex12(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, mit_sym_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "mit_sym_energies": mit_sym_energies
        }
    
    grade(answer_dict, "lab3-ex12", _challenge_id)

@typechecked
def grade_lab3_ex13(t: float, wp_meas_evs: numpy.ndarray, vac_meas_evs: numpy.ndarray, rescaled_mit_sym_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "wp_meas_evs": wp_meas_evs,
            "vac_meas_evs": vac_meas_evs,
            "rescaled_mit_sym_energies": rescaled_mit_sym_energies
        }
    
    grade(answer_dict, "lab3-ex13", _challenge_id)

@typechecked
def grade_lab3_ex14(t: float, best_wp_circ: QuantumCircuit, best_vac_circ: QuantumCircuit, best_energies: numpy.ndarray) -> None:

    answer_dict = {
            "t": t,
            "best_wp_circ": best_wp_circ,
            "best_vac_circ": best_vac_circ,
            "best_energies": best_energies
        }
    
    grade(answer_dict, "lab3-ex14", _challenge_id)