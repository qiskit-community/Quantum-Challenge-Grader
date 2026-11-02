from unittest.mock import patch

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

from qc_grader.challenges.qdc_2026 import lab_thermal_states as lab
from qc_grader.custom_encoder import to_json

_GRADE = "qc_grader.challenges.qdc_2026.lab_thermal_states.grade_answer"


def _submitted(function, *args):  # noqa: ANN001, ANN202
    with patch(_GRADE) as grade:
        function(*args)
    answer = grade.call_args.args[0]
    assert len(to_json(answer)) < 1_000_000  # serialisable, and small
    return answer, grade.call_args.kwargs["exercise"]


def test_ex1_2_canonical_keys_and_missing() -> None:
    energies = {
        (np.float64(100.0), 1): np.zeros((51, 100)),
        (0.25, 3): np.ones((51, 100)),
    }
    answer, exercise = _submitted(lab.grade_lab_thermal_states_ex1_2, energies)
    assert exercise == "ex1_2"
    assert set(answer) == {"b100_ne1", "b100_ne3", "b0p25_ne1", "b0p25_ne3"}
    assert answer["b100_ne3"] is None and answer["b0p25_ne3"][0][0] == 1.0


def test_ex2_6_packs_circuits_and_restores_rng() -> None:
    def init_environment(circ, NS, omega_n, beta):  # noqa: ANN001, ANN202, N803
        p_flip = 1 / (1 + np.exp(min(beta, 700) * omega_n))
        for i, flip in enumerate(np.random.rand(len(omega_n)) < p_flip):
            if flip:
                circ.x(NS + i)

    def init_system(circ, NS):  # noqa: ANN001, ANN202, N803
        init = ParameterVector("init", NS)
        for n in range(NS):
            circ.rx(init[n], n)
        return circ

    np.random.seed(5)
    before = np.random.rand()
    np.random.seed(5)
    answer, _ = _submitted(
        lab.grade_lab_thermal_states_ex2_6, init_environment, init_system
    )
    assert np.random.rand() == before  # the notebook's global RNG stream is untouched
    assert len(answer["x_counts"]) == 1000 and answer["cold_circuit"].num_qubits == 8
    assert answer["init_system_circuit"].num_parameters == 4 and answer["errors"] == {}


def test_ex2_7_reports_errors_per_function() -> None:
    def broken(*args):  # noqa: ANN002, ANN202
        raise RuntimeError("TODO")

    answer, _ = _submitted(
        lab.grade_lab_thermal_states_ex2_7,
        lambda lx, ly: np.arange(12),
        broken,
        lambda c, NS, dt, gx: c.rx(gx * dt, range(NS)),
        broken,
        broken,
    )
    assert answer["se_coupling"] == list(range(12)) and isinstance(
        answer["evolve_HX"], QuantumCircuit
    )
    assert (
        answer["evolve_HSE"] is None
        and "RuntimeError" in answer["errors"]["evolve_HSE"]
    )


def test_ex2_8c_flattens_sweep() -> None:
    def sweep(samplex, NS, ninit, ntwirls, seed, post_rot_values=(0, np.pi / 2)):  # noqa: ANN001, ANN202, N803
        return np.zeros((ninit, ntwirls, 2, len(samplex.parameters)))

    answer, _ = _submitted(lab.grade_lab_thermal_states_ex2_8c, sweep)
    assert (
        answer["shape"] == [200, 3, 2, 7]
        and len(answer["values"]) == 8400
        and answer["same_for_seed"] is True
    )


def test_ex2_8d_g_requires_objects() -> None:
    with pytest.raises(ValueError, match="CONNECT_TO_QPU"):
        lab.grade_lab_thermal_states_ex2_8d_g(None, None, None, None)


@pytest.mark.parametrize("bad", [None, 385.0, True, "385"])
def test_depths_must_be_integers(bad: object) -> None:
    with pytest.raises(ValueError, match="integer"):
        lab.grade_lab_thermal_states_ex2_8f(bad)


def test_ex4_2_casts_numpy_ints() -> None:
    answer, exercise = _submitted(
        lab.grade_lab_thermal_states_ex4_2, np.int64(385), 385
    )
    assert exercise == "ex4_2"
    assert answer == {"part4_two_qubit_depth": 385, "part2_two_qubit_depth": 385}
    assert all(type(v) is int for v in answer.values())


def test_hardware_results_are_reduced_to_floats() -> None:
    per_random = np.zeros((8, 1))
    energies = {
        (b, n): (per_random, np.array([-0.5]), np.array([0.01]))
        for b in (0.25, 100.0)
        for n in (0, 1, 3, 7)
    }
    answer, _ = _submitted(lab.grade_lab_thermal_states_ex2_14, energies)
    assert answer["b100_r7"] == -0.5 and all(type(v) is float for v in answer.values())
    answer, _ = _submitted(
        lab.grade_lab_thermal_states_ex4_7, {"zne": np.float64(-0.8), "zne_err": 0.02}
    )
    assert answer == {"zne": -0.8, "zne_err": 0.02}
    with pytest.raises(ValueError, match="perform_zne"):
        lab.grade_lab_thermal_states_ex3_5(None)
    with pytest.raises(ValueError, match="no entry"):
        lab.grade_lab_thermal_states_ex2_14(
            {(0.25, 0): (per_random, np.array([0.0]), np.array([0.0]))}
        )


def test_concepts_packs_strings() -> None:
    answer, _ = _submitted(
        lab.grade_lab_thermal_states_ex2_8_concepts, {"q1": "b", "q2": None}
    )
    assert answer == {"q1": "b", "q2": "", "q3": "", "q4": ""}


def test_probe_backend_pins_the_reset_duration() -> None:
    # 2.8E schedules the templates with the probe backend's durations; qiskit < 2.5 has none for reset.
    backend = lab._test_backend()
    for qubit in (0, 29, 155):
        assert backend.target["reset"][(qubit,)].duration == pytest.approx(
            lab._RESET_DURATION
        )
    assert backend.instruction_durations.get("reset", [29]) > 0
