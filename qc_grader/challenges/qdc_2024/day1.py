from typing import Callable, List
from typeguard import typechecked

import numpy as np
from scipy.optimize._optimize import OptimizeResult

from qiskit.quantum_info import SparsePauliOp
from qiskit.synthesis import LieTrotter

from qiskit_ibm_runtime.fake_provider import FakeTorino
from qiskit_serverless.core import QiskitFunction, Job
from qiskit_addon_utils.slicing import slice_by_gate_types, combine_slices
from qiskit_addon_utils.problem_generators import generate_xyz_hamiltonian, generate_time_evolution_circuit
from qiskit_addon_utils.coloring import auto_color_edges
from qiskit_addon_obp import backpropagate
from qiskit_addon_obp.utils.truncating import TruncationErrorBudget, setup_budget
from qiskit_addon_obp.utils.simplify import OperatorBudget

from qc_grader.grader.grade import grade


_challenge_id = 'qdc_2024'


@typechecked
def grade_day1a_ex1(qiskit_cf: QiskitFunction, job: Job) -> None:
    grade(
        [
            qiskit_cf.title,
            job.status()
        ],
        "day1a-ex1",
        _challenge_id,
    )


def run_evaluator(num_bp_slices: int, max_error_per_slice: List[float]) -> List[int]:

    backend = FakeTorino()
    coupling_map = backend.coupling_map
    edges = set(coupling_map.get_edges())
    unique_edges = set()
    for edge in edges:
        if edge[::-1] not in unique_edges:
            unique_edges.add(edge)
    coloring = auto_color_edges(sorted(unique_edges))

    hamiltonian = generate_xyz_hamiltonian(
        coupling_map,
        coupling_constants=(1.0, 1.0, 0.0),
        coloring=coloring,
    )

    dt = 0.05
    reps = 10
    time = dt * reps
    circuit = generate_time_evolution_circuit(
        hamiltonian,
        time=time,
        synthesis=LieTrotter(reps=reps),
    )

    L = circuit.num_qubits
    observable = SparsePauliOp("I" * (L // 2) + "ZZ" + "I" * (L // 2 - 1))

    slices = slice_by_gate_types(circuit)
    
    max_error_total = 0.05
    max_qwc_groups = 20

    error_budget = setup_budget(
        max_error_per_slice=max_error_per_slice, p_norm=2, max_error_total=max_error_total
    )
    op_budget = OperatorBudget(max_qwc_groups=max_qwc_groups)

    bp_obs, remaining_slices, metadata = backpropagate(
        observable,
        slices[-num_bp_slices:],
        operator_budget=op_budget,
        truncation_error_budget=error_budget,
    )
    final_circ = combine_slices(slices[:-num_bp_slices] + remaining_slices)

    return [circuit.depth(), final_circ.depth()]

@typechecked
def grade_day1a_ex2(num_bp_slices: int, max_error_per_slice: List[float]) -> None:
    answer_list = run_evaluator(num_bp_slices, max_error_per_slice)
    grade(
        answer_list,
        "day1a-ex2",
        _challenge_id,
    )