from typing import Callable, List
from typeguard import typechecked

import numpy as np
import pickle
from scipy.optimize._optimize import OptimizeResult
from pathlib import Path

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
from qiskit_addon_sqd.counts import counts_to_arrays, generate_counts_uniform
from qiskit_addon_sqd.subsampling import postselect_and_subsample
from qiskit_addon_sqd.fermion import solve_fermion, flip_orbital_occupancies
from qiskit_addon_sqd.configuration_recovery import recover_configurations

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


def obp(num_bp_slices: int, max_error_per_slice: List[float]) -> List[int]:

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
    observable = SparsePauliOp.from_sparse_list([("Z", [(circuit.num_qubits)//2], 1.0) ],num_qubits=circuit.num_qubits)

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
    answer_list = obp(num_bp_slices, max_error_per_slice)
    grade(
        answer_list,
        "day1a-ex2",
        _challenge_id,
    )

@typechecked
def sqd_configuration_recovery(n_batches: int, samples_per_batch: int) -> np.ndarray:
    """Perform SQD on N2 molecule, given some subspace parameters."""
    iterations = 5
    num_orbitals = 16
    num_elec_a = num_elec_b = 5
    rand_seed = int(np.random.default_rng(2**24).random())

    current_directory = Path(__file__).parent
    N2_device_counts = current_directory / 'N2_device_counts.npy'
    
    counts = np.load(N2_device_counts, allow_pickle=True).item()
    # Convert counts into bitstring and probability arrays
    bitstring_matrix, probabilities = counts_to_arrays(counts)

    # Read in molecule from disk
    n2_fci = current_directory / "n2_fci.txt"
    hcore = np.load(current_directory / "hcore.npy")
    eri = np.load(current_directory / "eri.npy")
    with open(current_directory / "nuclear_repulsion_energy.pkl", "rb") as f:
        nre = pickle.load(f)

    # Self-consistent configuration recovery loop
    energy_hist = np.zeros((iterations, n_batches))  # energy history
    occupancy_hist = np.zeros((iterations, 2 * num_orbitals))
    occupancies_bitwise = None  # orbital i corresponds to column i in bitstring matrix
    for i in range(iterations):
        print(f"Starting configuration recovery iteration {i}")
        # On the first iteration, we have no orbital occupancy information from the
        # solver, so we just post-select from the full bitstring set based on hamming weight.
        if occupancies_bitwise is None:
            bs_mat_tmp = bitstring_matrix
            probs_arr_tmp = probabilities

        # If we have average orbital occupancy information, we use it to refine the full set of noisy configurations
        else:
            bs_mat_tmp, probs_arr_tmp = recover_configurations(
                bitstring_matrix,
                probabilities,
                occupancies_bitwise,
                num_elec_a,
                num_elec_b,
                rand_seed=rand_seed,
            )

        # Throw out configurations with incorrect particle number in either the spin-up or spin-down systems
        batches = postselect_and_subsample(
            bs_mat_tmp,
            probs_arr_tmp,
            hamming_right=num_elec_a,
            hamming_left=num_elec_b,
            samples_per_batch=samples_per_batch,
            num_batches=n_batches,
            rand_seed=rand_seed,
        )

        # Run eigenstate solvers in a loop. This loop should be parallelized for larger problems.
        energy_tmp = np.zeros(n_batches)
        occs_tmp = np.zeros((n_batches, 2 * num_orbitals))
        for j in range(n_batches):
            energy_sci, _, avg_occs, _ = solve_fermion(
                batches[j],
                hcore,
                eri,
            )
            energy_sci += nre
            energy_tmp[j] = energy_sci
            occs_tmp[j, :num_orbitals] = avg_occs[0]
            occs_tmp[j, num_orbitals:] = avg_occs[1]

        # Combine batch results
        avg_occupancies = np.mean(occs_tmp, axis=0)
        # The occupancies from the solver should be flipped to match the bits in the bitstring matrix.
        occupancies_bitwise = flip_orbital_occupancies(avg_occupancies)

        # Track optimization history
        energy_hist[i, :] = energy_tmp
        occupancy_hist[i, :] = avg_occupancies

    return energy_hist

@typechecked
def grade_day1b_ex1(num_batches: int, samples_per_batch: int) -> None:
    energy_hist = sqd_configuration_recovery(num_batches, samples_per_batch)
    min_e = np.min(energy_hist)
    grade(
        min_e,
        "day1b-ex1",
        _challenge_id,
    )


@typechecked
def submit_feedback_1a_1(feedback: str) -> None:
    grade(feedback, 'feedback-1a-1', _challenge_id)


@typechecked
def submit_feedback_1a_2(feedback: str) -> None:
    grade(feedback, 'feedback-1a-2', _challenge_id)

@typechecked
def submit_feedback_1a_3(feedback: str) -> None:
    grade(feedback, 'feedback-1a-3', _challenge_id)


@typechecked
def submit_feedback_1b_1(feedback: str) -> None:
    grade(feedback, 'feedback-1b-1', _challenge_id)


@typechecked
def submit_feedback_1b_2(feedback: str) -> None:
    grade(feedback, 'feedback-1b-2', _challenge_id)
