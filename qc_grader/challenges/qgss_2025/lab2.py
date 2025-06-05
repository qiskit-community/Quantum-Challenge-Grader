from typeguard import typechecked
from typing import List

from qiskit.quantum_info import SparsePauliOp
import numpy as np
from qiskit import transpile
from qiskit import QuantumCircuit
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import rustworkx

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2025'

# TODO!!!! 

@typechecked
def grade_lab2_ex1(
    solutions: List, backend
) -> None:
    grade({
        'solutions': solutions,
        'backend': backend,
    }, 'lab2-ex1', _challenge_id)


@typechecked
def grade_lab2_ex2(
    cost_hamiltonian: SparsePauliOp, graph: rustworkx.PyGraph
) -> None:
    grade({
        'cmcost_hamiltonianap': cost_hamiltonian,
        'graph': graph,
    }, 'lab2-ex2', _challenge_id)


@typechecked
def grade_lab2_ex3(
    results_list: list, backend_list: list, circuit_list: list
) -> None:
    grade({
        'results_list': results_list,
        'backend_list': backend_list,
        'circuit_list': circuit_list,
    }, 'lab2-ex3', _challenge_id)



@typechecked
def grade_lab2_ex4(
    valid_paths: list, valid_weights: list, graph: rustworkx.PyGraph, two_qubit_ops_list: list, logical_pair_list: list
) -> None:
    grade({
        'valid_paths': valid_paths,
        'valid_weights': valid_weights,
        'graph': graph,
        'two_qubit_ops_list': two_qubit_ops_list,
        'logical_pair_list': logical_pair_list,
    }, 'lab2-ex4', _challenge_id)



@typechecked
def grade_lab2_ex5(
    best_seed_transpiler: int, min_err_acc_seed: float, circuit_trivial: QuantumCircuit, noisy_backend, two_qubit_gate_errors_per_circuit_layout: callable
) -> None:
    grade({
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
    }, 'lab2-ex5', _challenge_id)


@typechecked
def grade_lab2_ex6a(
    fold_circuit: callable, circuit: QuantumCircuit, scale_factors: list, noisy_backends: list
) -> None:
    grade({
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
    }, 'lab2-ex6', _challenge_id)

@typechecked
def grade_lab2_ex6b(
    fold_circuit: callable, circuit: QuantumCircuit, scale_factors: list, noisy_backends: list
) -> None:
    grade({
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
    }, 'lab2-ex6', _challenge_id)


@typechecked
def grade_lab2_ex7(
    pub: tuple, circuit: QuantumCircuit, noisy_backend, scales: list
) -> None:
    grade({
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
        'TODO': 'TODO',
    }, 'lab2-ex7', _challenge_id)




