from typeguard import typechecked

from qiskit import QuantumCircuit
from .lattice import HeavyHexLattice
from qc_grader.grader.grade import grade
from qiskit_ibm_runtime.ibm_backend import IBMBackend
import numpy


_challenge_id = 'qdc_2025'


@typechecked
def grade_lab1_ex1(qc: QuantumCircuit) -> None:
    grade(qc, 'lab1-ex1', _challenge_id)


@typechecked
def grade_lab1_ex2(qc: QuantumCircuit, lattice: HeavyHexLattice) -> None:
    plaq_width = lattice.plaquettes_width
    plaq_height = lattice.plaquettes_height
    answer_dict = {
        "plaq_width": plaq_width,
        "plaq_height": plaq_height,
        "qc": qc
    }
    grade(answer_dict, 'lab1-ex2', _challenge_id)

@typechecked
def grade_lab1_ex3(qc: QuantumCircuit, lattice: HeavyHexLattice) -> None:
    plaq_width = lattice.plaquettes_width
    plaq_height = lattice.plaquettes_height
    answer_dict = {
        "plaq_width": plaq_width,
        "plaq_height": plaq_height,
        "qc": qc
    }
    grade(answer_dict, 'lab1-ex3', _challenge_id)


@typechecked
def grade_lab1_ex4(isa_circuits: list, lattice: HeavyHexLattice, dt: float, backend: IBMBackend) -> None:
    plaq_width = lattice.plaquettes_width
    plaq_height = lattice.plaquettes_height

    answer_dict = {
        "isa_circuits": isa_circuits,
        "plaq_width": plaq_width,
        "plaq_height": plaq_height,
        "dt": dt
    }
    grade(answer_dict, 'lab1-ex4', _challenge_id)

@typechecked
def grade_lab1_ex5(best_expectation_vals: numpy.ndarray, qubit: int, dt: float, classical_exp_vals: numpy.ndarray ) -> None:
    answer_dict = {
        "best_expectation_vals": best_expectation_vals,
        "qubit": qubit,
        "dt": dt,
        "classical_exp_vals": classical_exp_vals
    }
    grade(answer_dict, 'lab1-ex5', _challenge_id)