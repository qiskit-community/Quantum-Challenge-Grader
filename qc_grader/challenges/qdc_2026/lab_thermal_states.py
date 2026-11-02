# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
QDC 2026 - Thermal states lab - Grading Functions

Each grade_* function runs the participant's code on fixed probe inputs, reduces the results to
plain data and submits them. Reference answers live only on the grading server.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Optional

import numpy as np
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import Parameter, ParameterVector
from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"
_LAB = "lab_thermal_states"
_DATA = Path(__file__).parent / "data"

# Physics constants of the challenge (identical to the notebook and the server).
_ALPHA, _T_TOT, _NTROT, _GX, _GZ = 1.75, 0.75, 3, 0.5, 2.0
_DT = _T_TOT / _NTROT
_SEED = 2026


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@contextmanager
def _seeded_global_rng(seed: int) -> Iterator[None]:
    """Seed np.random for participant code that uses it, then restore the notebook's RNG state."""
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def _error_text(err: BaseException) -> str:
    return f"{type(err).__name__}: {str(err)[:200]}"


def _returned_circuit(circuit: QuantumCircuit, returned: Any) -> QuantumCircuit:
    """The notebook's functions modify `circuit` in place; some also return it."""
    return returned if isinstance(returned, QuantumCircuit) else circuit


def _int_list(values: Any) -> list[int]:
    return [int(v) for v in np.asarray(values).ravel()]


def _float(value: Any, name: str) -> float:
    try:
        return float(np.asarray(value, dtype=float).item())
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"{name} must be a single number, got {type(value).__name__}."
        ) from err


def _two_qubit_depth(value: Any, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(
            f"{name} must be an integer: the cz/rzz depth computed with circuit.depth(...). "
            f"Got {type(value).__name__}; build the circuit first (CONNECT_TO_QPU=True)."
        )
    return int(value)


def _load_qpy(name: str) -> list[QuantumCircuit]:
    with open(_DATA / name, "rb") as file:
        return list(qpy.load(file))


########################################################################################################################
# Part 1
########################################################################################################################

_PART1_KEYS = {
    (100.0, 1): "b100_ne1",
    (100.0, 3): "b100_ne3",
    (0.25, 1): "b0p25_ne1",
    (0.25, 3): "b0p25_ne3",
}


@typechecked
def grade_lab_thermal_states_ex1_2(part1_energies: Mapping[Any, Any]) -> None:
    """Submit `part1_energies`, the dict {(beta, NE): energy-density array} from section 1.2."""
    answer: dict[str, Optional[list[list[float]]]] = {}
    for (beta, ne), key in _PART1_KEYS.items():
        match = [
            value
            for (b, n), value in part1_energies.items()
            if np.isclose(float(b), beta) and int(n) == ne
        ]
        answer[key] = np.asarray(match[0], dtype=float).tolist() if match else None
    _grade(answer, "ex1_2")


########################################################################################################################
# Part 2.6 - 2.7
########################################################################################################################

_EX2_6_NS = 4


@typechecked
def grade_lab_thermal_states_ex2_6(
    init_environment: Callable, init_system: Callable
) -> None:
    """Submit your `init_environment` and `init_system` functions from section 2.6."""
    errors: dict[str, str] = {}
    cold_circuit: Optional[QuantumCircuit] = None
    x_counts: Optional[list[int]] = None
    omega_n = np.ones(_EX2_6_NS)
    try:
        with _seeded_global_rng(_SEED):
            cold_circuit = QuantumCircuit(2 * _EX2_6_NS)
            init_environment(cold_circuit, _EX2_6_NS, omega_n, 1e10)
            x_counts = []
            for _ in range(1000):
                circuit = QuantumCircuit(2 * _EX2_6_NS)
                init_environment(circuit, _EX2_6_NS, omega_n, 0.0)
                x_counts.append(int(circuit.count_ops().get("x", 0)))
    except Exception as err:  # noqa: BLE001 - report the participant's error to the server
        cold_circuit, x_counts = None, None
        errors["init_environment"] = _error_text(err)

    init_system_circuit: Optional[QuantumCircuit] = None
    try:
        circuit = QuantumCircuit(2 * _EX2_6_NS)
        init_system_circuit = _returned_circuit(
            circuit, init_system(circuit, _EX2_6_NS)
        )
    except Exception as err:  # noqa: BLE001
        errors["init_system"] = _error_text(err)

    _grade(
        {
            "cold_circuit": cold_circuit,
            "x_counts": x_counts,
            "init_system_circuit": init_system_circuit,
            "errors": errors,
        },
        "ex2_6",
    )


# Probe constants (identical to the server).
_EX2_7_COUPLINGS = ["X", "Y", "Z"]
_EX2_7_RANDOM_COUPLING = [0, 1, 2, 0, 1, 2]
_EX2_7_RANDOM_SIGN = [1, -1, 1, -1, 1, -1]
_EX2_7_OMEGA_HZ = [0.37, 1.21, 2.05, 0.83]
_EX2_7_OMEGA_TROT = [0.52, 1.74, 0.29, 2.61, 1.08, 3.33]


@typechecked
def grade_lab_thermal_states_ex2_7(
    SE_Coupling: Callable,
    evolve_HSE: Callable,
    evolve_HX: Callable,
    evolve_HZ: Callable,
    one_Trot_step: Callable,
) -> None:
    """Submit your `SE_Coupling`, `evolve_HSE`, `evolve_HX`, `evolve_HZ` and `one_Trot_step` (section 2.7).

    Each evolve function is applied to an empty circuit; the server prepends its own random state.
    """
    errors: dict[str, str] = {}
    se_coupling: Optional[list[int]] = None
    try:
        se_coupling = _int_list(SE_Coupling(2, 2))
    except Exception as err:  # noqa: BLE001
        errors["SE_Coupling"] = _error_text(err)

    probes = {
        "evolve_HSE": (
            12,
            lambda c: evolve_HSE(
                c,
                6,
                6,
                _DT,
                list(_EX2_7_COUPLINGS),
                list(_EX2_7_RANDOM_COUPLING),
                list(_EX2_7_RANDOM_SIGN),
                np.arange(6),
                1.0,
                _ALPHA,
            ),
        ),
        "evolve_HX": (4, lambda c: evolve_HX(c, 4, _DT, _GX)),
        "evolve_HZ": (
            8,
            lambda c: evolve_HZ(c, 4, 4, 1, 1, _DT, _GZ, np.array(_EX2_7_OMEGA_HZ)),
        ),
        "one_Trot_step": (
            12,
            lambda c: one_Trot_step(
                c,
                6,
                6,
                1,
                1,
                _DT,
                list(_EX2_7_COUPLINGS),
                list(_EX2_7_RANDOM_COUPLING),
                list(_EX2_7_RANDOM_SIGN),
                np.arange(6),
                1.0,
                _ALPHA,
                _GX,
                _GZ,
                np.array(_EX2_7_OMEGA_TROT),
            ),
        ),
    }
    circuits: dict[str, Optional[QuantumCircuit]] = {}
    for name, (num_qubits, apply) in probes.items():
        try:
            circuit = QuantumCircuit(num_qubits)
            with _seeded_global_rng(_SEED):
                circuits[name] = _returned_circuit(circuit, apply(circuit))
        except Exception as err:  # noqa: BLE001
            circuits[name] = None
            errors[name] = _error_text(err)
    _grade({"se_coupling": se_coupling, **circuits, "errors": errors}, "ex2_7")


########################################################################################################################
# Part 2.8 - the Samplomatic pipeline, on a fixed test circuit and a fixed offline backend
########################################################################################################################

_LAYOUT_2X2 = [38, 39, 48, 50, 52, 54, 57, 58, 66, 68, 70, 72] + [
    29,
    33,
    49,
    51,
    53,
    55,
    47,
    71,
    65,
    67,
    69,
    73,
]
_NS_2X2 = 12
_BACKEND = None
_RESET_DURATION = (
    2.212008e-06  # s; the reset duration GenericBackendV2 assigns on qiskit 2.5.2
)


def _test_backend() -> Any:
    # Heron-like target with fractional rx/rzz and instruction durations; deterministic and offline.
    global _BACKEND
    if _BACKEND is None:
        from qiskit.providers.fake_provider import GenericBackendV2
        from qiskit.transpiler import InstructionProperties
        from qiskit_ibm_runtime.fake_provider import FakeBoston

        _BACKEND = GenericBackendV2(
            num_qubits=156,
            basis_gates=[
                "cz",
                "rz",
                "rx",
                "rzz",
                "x",
                "sx",
                "id",
                "measure",
                "reset",
                "delay",
            ],
            coupling_map=list(FakeBoston().coupling_map.get_edges()),
            seed=1,
        )
        # qiskit < 2.5 gives GenericBackendV2 no reset duration, and the ALAP scheduling in the
        # participant's finalize_templates (2.8E) needs one. Pin the value qiskit 2.5.2 assigns,
        # which the server's 2.8E reference was built with, so every supported qiskit agrees.
        for qubit in range(_BACKEND.num_qubits):
            _BACKEND.target.update_instruction_properties(
                "reset",
                (qubit,),
                InstructionProperties(duration=_RESET_DURATION, error=None),
            )
    return _BACKEND


def _test_logical_circuit() -> QuantumCircuit:
    # A small Gibbs-like circuit on the (2, 2) layout with partly idle entangling layers, a labelled
    # bath-reset window and a parameterized readout.
    ns = _NS_2X2
    init = ParameterVector("init", ns)
    post_rot = Parameter("post_rot")
    qc = QuantumCircuit(2 * ns)
    for n in range(ns):
        qc.rx(init[n], n)
    for n in range(ns):
        qc.rzz(0.21, n, n + ns)
    qc.rx(0.3, range(ns))
    qc.rz(0.4, range(2 * ns))
    for n in range(0, ns, 2):
        qc.rzz(0.33, n, n + ns)
    for n in range(1, ns, 3):
        qc.cz(n, n + ns)
    qc.barrier(label="pre_reset_0")
    for n in range(ns):
        qc.reset(n + ns)
    qc.barrier(label="post_reset_0")
    for n in range(ns // 2):
        qc.rzz(-0.17, n, n + ns)
    for n in range(ns):
        qc.rz(np.pi / 2, n)
        qc.rx(post_rot, n)
    qc.measure_all()
    return qc


def _first_circuit(result: Any) -> QuantumCircuit:
    first = result[0] if isinstance(result, (list, tuple)) else result
    if not isinstance(first, QuantumCircuit):
        raise ValueError(f"expected a list of circuits, got {type(first).__name__}")
    return first


@typechecked
def grade_lab_thermal_states_ex2_8a(compile_to_isa: Callable) -> None:
    """Submit your `compile_to_isa(logical_circuits, backend, layout)` function (section 2.8A)."""
    try:
        isa_circuit: Optional[QuantumCircuit] = _first_circuit(
            compile_to_isa(
                [_test_logical_circuit()], _test_backend(), list(_LAYOUT_2X2)
            )
        )
        error = ""
    except Exception as err:  # noqa: BLE001
        isa_circuit, error = None, _error_text(err)
    _grade({"isa_circuit": isa_circuit, "error": error}, "ex2_8a")


def _signature(template: QuantumCircuit, samplex: Any) -> dict[str, Any]:
    return {
        "num_parameters": int(template.num_parameters),
        "count_ops": {str(k): int(v) for k, v in template.count_ops().items()},
        "samplex_parameters": [str(p.name) for p in samplex.parameters],
    }


@typechecked
def grade_lab_thermal_states_ex2_8b(box_and_build: Callable) -> None:
    """Submit your `box_and_build(isa_circuits, *, return_boxed=False)` function (section 2.8B)."""
    isa = _load_qpy("ex2_8_isa_input.qpy")
    boxed_sig: Optional[dict[str, Any]] = None
    plain_sig: Optional[dict[str, Any]] = None
    error = ""
    try:
        templates, samplexes, boxed = box_and_build(isa, return_boxed=True)
        boxed_sig = {
            "num_boxes": int(boxed[0].count_ops().get("box", 0)),
            **_signature(templates[0], samplexes[0]),
        }
        plain = box_and_build(isa)
        if len(plain) != 2:
            raise ValueError(
                "box_and_build(isa_circuits) must return (templates, samplexes)"
            )
        plain_sig = _signature(plain[0][0], plain[1][0])
    except Exception as err:  # noqa: BLE001
        boxed_sig, plain_sig, error = None, None, _error_text(err)
    _grade({"boxed": boxed_sig, "plain": plain_sig, "error": error}, "ex2_8b")


class _ProbeParameter:
    def __init__(self, name: str) -> None:
        self.name = name


class _ProbeSamplex:
    # Stand-in exposing only `.parameters`, in a shuffled order: a sweep that ignores
    # samplex.parameters puts values in the wrong columns. The server keeps the same order.
    def __init__(self, ns: int) -> None:
        names = [f"init[{n}]" for n in range(ns)] + ["post_rot"]
        self.parameters = [_ProbeParameter(names[i]) for i in (5, 6, 2, 1, 4, 3, 0)]


@typechecked
def grade_lab_thermal_states_ex2_8c(samplex_parameter_values: Callable) -> None:
    """Submit your `samplex_parameter_values(samplex, NS, ninit, ntwirls, seed)` function (section 2.8C)."""
    samplex = _ProbeSamplex(6)
    try:
        values = np.asarray(
            samplex_parameter_values(samplex, 6, 200, 3, seed=11), dtype=float
        )
        repeat = np.asarray(
            samplex_parameter_values(samplex, 6, 200, 3, seed=11), dtype=float
        )
        answer = {
            "shape": [int(n) for n in values.shape],
            "values": values.ravel().tolist() if values.size <= 20_000 else [],
            "same_for_seed": bool(
                values.shape == repeat.shape and np.array_equal(values, repeat)
            ),
            "error": "",
        }
    except Exception as err:  # noqa: BLE001
        answer = {
            "shape": [],
            "values": [],
            "same_for_seed": False,
            "error": _error_text(err),
        }
    _grade(answer, "ex2_8c")


@typechecked
def grade_lab_thermal_states_ex2_8d_g(
    training_program: Any,
    training_template: Optional[QuantumCircuit],
    training_samplex: Any,
    sampled: Any,
) -> None:
    """Submit `training_program`, `training_template`, `training_samplex` and `sampled` (sections 2.8D and 2.8G).

    These are built from a live backend; the values you submit are self-reported.
    """
    if (
        training_program is None
        or training_template is None
        or training_samplex is None
        or sampled is None
    ):
        raise ValueError(
            "Build the training template, samplex, local samples and QuantumProgram first "
            "(this needs CONNECT_TO_QPU=True), then rerun this cell."
        )
    try:
        items = list(training_program.items)
        item = items[0]
        answer = {
            "num_items": len(items),
            "circuit_is_template": item.circuit is training_template,
            "samplex_matches": item.samplex is training_samplex,
            "item_shape": [int(n) for n in item.shape],
            "parameter_values_shape": [
                int(n)
                for n in np.asarray(item.samplex_arguments["parameter_values"]).shape
            ],
            "samplex_num_parameters": len(training_samplex.parameters),
            "template_num_parameters": int(training_template.num_parameters),
            "sampled_parameter_values_shape": [
                int(n) for n in np.asarray(sampled["parameter_values"]).shape
            ],
            "sampled_flips_shape": [
                int(n) for n in np.asarray(sampled["measurement_flips.meas"]).shape
            ],
            "error": "",
        }
    except Exception as err:  # noqa: BLE001
        answer = {
            "num_items": 0,
            "circuit_is_template": False,
            "samplex_matches": False,
            "item_shape": [],
            "parameter_values_shape": [],
            "samplex_num_parameters": 0,
            "template_num_parameters": 0,
            "sampled_parameter_values_shape": [],
            "sampled_flips_shape": [],
            "error": _error_text(err),
        }
    _grade(answer, "ex2_8d_g")


@typechecked
def grade_lab_thermal_states_ex2_8e(finalize_templates: Callable) -> None:
    """Submit your `finalize_templates(templates, backend, layout, post_selection=...)` function (section 2.8E)."""
    templates = _load_qpy("ex2_8_templates.qpy")
    try:
        result = finalize_templates(
            templates, _test_backend(), list(_LAYOUT_2X2), post_selection=False
        )
        final = _first_circuit(result[0] if isinstance(result, tuple) else result)
        answer = {
            "count_ops": {str(k): int(v) for k, v in final.count_ops().items()},
            "barrier_labels": [
                str(inst.operation.label)
                for inst in final.data
                if inst.operation.name == "barrier" and inst.operation.label
            ],
            "error": "",
        }
    except Exception as err:  # noqa: BLE001
        answer = {"count_ops": {}, "barrier_labels": [], "error": _error_text(err)}
    _grade(answer, "ex2_8e")


@typechecked
def grade_lab_thermal_states_ex2_8f(part2_two_qubit_depth: Any) -> None:
    """Submit `part2_two_qubit_depth`, the cz/rzz depth of the 24-qubit template (section 2.8F)."""
    _grade(
        {
            "part2_two_qubit_depth": _two_qubit_depth(
                part2_two_qubit_depth, "part2_two_qubit_depth"
            )
        },
        "ex2_8f",
    )


@typechecked
def grade_lab_thermal_states_ex2_8_concepts(part2p8_answers: Mapping[str, Any]) -> None:
    """Submit `part2p8_answers`, the dict {"q1": ..., "q4": ...} of letters a-d (feedback only, 0 points)."""
    _grade(
        {
            key: str(part2p8_answers.get(key, "") or "")
            for key in ("q1", "q2", "q3", "q4")
        },
        "ex2_8_concepts",
    )


########################################################################################################################
# Part 2.11 - analysis functions, on a fixed synthetic result
########################################################################################################################

_KAGOME_2X2 = [
    (0, 2),
    (0, 3),
    (1, 4),
    (1, 5),
    (2, 3),
    (3, 4),
    (4, 5),
    (2, 6),
    (3, 7),
    (4, 7),
    (6, 8),
    (6, 9),
    (7, 10),
    (7, 11),
    (8, 9),
    (9, 10),
    (10, 11),
]


def _synthetic_bits(shape: tuple, salt: int) -> np.ndarray:
    # A fixed 64-bit LCG, independent of numpy's RNGs, so the server's reference never drifts.
    n = int(np.prod(shape))
    multiplier, increment = (
        np.uint64(6364136223846793005),
        np.uint64(1442695040888963407),
    )
    x = np.arange(n, dtype=np.uint64) * multiplier + increment + np.uint64(salt)
    x = x * multiplier + increment
    return ((x >> np.uint64(33)) & np.uint64(1)).astype(bool).reshape(shape)


def _synthetic_result() -> dict[str, np.ndarray]:
    # Same keys and axes as one QuantumProgram item result: (init, twirl, basis, shots, bits).
    return {
        "meas": _synthetic_bits((2, 3, 2, 16, 24), 1),
        "measurement_flips.meas": _synthetic_bits((2, 3, 2, 1, 24), 2),
    }


def _nested(values: Any) -> list:
    return np.asarray(values, dtype=float).tolist()


@typechecked
def grade_lab_thermal_states_ex2_11(
    get_vals: Callable, compute_observables: Callable
) -> None:
    """Submit your `get_vals` and `compute_observables` functions (section 2.11)."""
    errors: dict[str, str] = {}
    answer: dict[str, Any] = {
        "z_site": None,
        "x_site": None,
        "zz_bond": None,
        "observables": None,
    }
    try:
        result = _synthetic_result()
        answer["z_site"] = _nested([get_vals(result, 0, [j], 24) for j in range(12)])
        answer["x_site"] = _nested([get_vals(result, 1, [j], 24) for j in range(12)])
        answer["zz_bond"] = _nested(
            [get_vals(result, 0, list(edge), 24) for edge in _KAGOME_2X2]
        )
    except Exception as err:  # noqa: BLE001
        answer["z_site"] = answer["x_site"] = answer["zz_bond"] = None
        errors["get_vals"] = _error_text(err)
    try:
        observables = compute_observables(
            np.linspace(-0.6, 0.4, 12),
            np.linspace(-0.9, 0.5, len(_KAGOME_2X2)),
            np.linspace(0.3, -0.2, 12),
            12,
        )
        answer["observables"] = [
            float(np.asarray(v, dtype=float).item()) for v in observables
        ]
    except Exception as err:  # noqa: BLE001
        errors["compute_observables"] = _error_text(err)
    _grade({**answer, "errors": errors}, "ex2_11")


########################################################################################################################
# Parts 2.14, 3.5, 3.6 and 4.7 - hardware energy densities (self-reported)
########################################################################################################################


def _mean_energy(
    energies: Mapping[Any, Any], beta: float, nreset: int, name: str
) -> float:
    for (b, n), value in energies.items():
        if np.isclose(float(b), beta) and int(n) == nreset:
            return _float(value[1], f"the mean energy in {name}[({beta}, {nreset})]")
    raise ValueError(
        f"{name} has no entry for (beta, N_resets) = ({beta}, {nreset}); run the analysis cells first."
    )


@typechecked
def grade_lab_thermal_states_ex2_14(part2_energies: Any) -> None:
    """Submit `part2_energies` (or `part2_best_energies`) from energy_from_results (section 2.14).

    Hardware results are self-reported.
    """
    if not isinstance(part2_energies, Mapping) or not part2_energies:
        raise ValueError(
            "part2_energies is empty: retrieve the Part 2 results and run energy_from_results first."
        )
    answer = {
        f"{prefix}_r{nreset}": _mean_energy(
            part2_energies, beta, nreset, "part2_energies"
        )
        for prefix, beta in (("b0p25", 0.25), ("b100", 100.0))
        for nreset in (0, 1, 3, 7)
    }
    _grade(answer, "ex2_14")


def _zne_answer(zne: Any, name: str) -> dict[str, float]:
    if not isinstance(zne, Mapping) or "zne" not in zne:
        raise ValueError(
            f"{name} is empty: run perform_zne on the post-selected energies first."
        )
    return {
        "zne": _float(zne["zne"], f"{name}['zne']"),
        "zne_err": _float(zne.get("zne_err", 0.0), f"{name}['zne_err']"),
    }


@typechecked
def grade_lab_thermal_states_ex3_5(part3_zne_beta100_ps: Any) -> None:
    """Submit `part3_zne_beta100_ps` (or the "best" version), the perform_zne dict at beta = 100 (section 3.5)."""
    _grade(_zne_answer(part3_zne_beta100_ps, "part3_zne_beta100_ps"), "ex3_5")


@typechecked
def grade_lab_thermal_states_ex3_6(part3_zne_beta0p25_ps: Any) -> None:
    """Submit `part3_zne_beta0p25_ps` (or the "best" version), the perform_zne dict at beta = 0.25 (section 3.6)."""
    _grade(_zne_answer(part3_zne_beta0p25_ps, "part3_zne_beta0p25_ps"), "ex3_6")


@typechecked
def grade_lab_thermal_states_ex4_7(part4_zne_ps: Any) -> None:
    """Submit `part4_zne_ps` (or `part4_best_zne_ps`), the 67-qubit perform_zne dict (section 4.7)."""
    _grade(_zne_answer(part4_zne_ps, "part4_zne_ps"), "ex4_7")


########################################################################################################################
# Part 3.4 - ZNE functions
########################################################################################################################

_EX3_4_PROBES = [([1.0, 2.0, 3.0], [2.0, 3.0, 4.0]), ([1.0, 1.5, 2.0], [1.0, 2.0, 3.5])]
_EX3_4_NOISE_AMP = [0.0, 0.25, 0.50]
# Raw (beta = 0.25, 7 resets) energies per randomization and noise factor; not secret.
_EX3_4_ENERGY_PER_RANDOMIZATION = [
    [-0.193125, -0.18489583333333334, -0.13226562500000003],
    [-0.6348958333333333, -0.5946874999999999, -0.55140625],
    [-0.4798177083333333, -0.41807291666666674, -0.4009895833333333],
    [-0.5552864583333333, -0.5178385416666667, -0.48330729166666675],
    [-0.4771614583333334, -0.44476562500000005, -0.4028645833333333],
    [-0.2742708333333333, -0.2243229166666667, -0.18247395833333332],
    [-0.605859375, -0.5750260416666667, -0.5238020833333333],
    [-0.379375, -0.36075520833333335, -0.3047135416666667],
]


@typechecked
def grade_lab_thermal_states_ex3_4(linear_zne: Callable, perform_zne: Callable) -> None:
    """Submit your `linear_zne` and `perform_zne` functions (section 3.4)."""
    errors: dict[str, str] = {}
    intercepts: Optional[list[float]] = None
    zne: Optional[float] = None
    try:
        intercepts = [
            _float(linear_zne(np.array(x), np.array(y)), "linear_zne(...)")
            for x, y in _EX3_4_PROBES
        ]
    except Exception as err:  # noqa: BLE001
        errors["linear_zne"] = _error_text(err)
    try:
        per_randomization = np.array(_EX3_4_ENERGY_PER_RANDOMIZATION)
        energies = {
            (0.25, 7): (
                per_randomization,
                per_randomization.mean(axis=0),
                per_randomization.std(axis=0, ddof=1) / np.sqrt(len(per_randomization)),
            )
        }
        zne = _float(
            perform_zne(energies, list(_EX3_4_NOISE_AMP), 0.25, 7)["zne"],
            "perform_zne(...)['zne']",
        )
    except Exception as err:  # noqa: BLE001
        errors["perform_zne"] = _error_text(err)
    _grade({"linear_zne": intercepts, "perform_zne": zne, "errors": errors}, "ex3_4")


########################################################################################################################
# Part 4
########################################################################################################################


@typechecked
def grade_lab_thermal_states_ex4_1(
    kagome_edge_set: Callable, SE_Coupling: Callable
) -> None:
    """Submit your `kagome_edge_set` and `SE_Coupling` with the (3, 3) entries filled in (section 4.1)."""
    errors: dict[str, str] = {}
    edges: Optional[list[list[int]]] = None
    se_coupling: Optional[list[int]] = None
    try:
        edges = [_int_list(edge) for edge in kagome_edge_set(3, 3)]
    except Exception as err:  # noqa: BLE001
        errors["kagome_edge_set"] = _error_text(err)
    try:
        with _seeded_global_rng(_SEED):
            se_coupling = _int_list(SE_Coupling(3, 3))
    except Exception as err:  # noqa: BLE001
        errors["SE_Coupling"] = _error_text(err)
    _grade({"edges": edges, "se_coupling": se_coupling, "errors": errors}, "ex4_1")


@typechecked
def grade_lab_thermal_states_ex4_2(
    part4_two_qubit_depth: Any, part2_two_qubit_depth: Any
) -> None:
    """Submit `part4_two_qubit_depth` (section 4.2) together with `part2_two_qubit_depth` (section 2.8F)."""
    _grade(
        {
            "part4_two_qubit_depth": _two_qubit_depth(
                part4_two_qubit_depth, "part4_two_qubit_depth"
            ),
            "part2_two_qubit_depth": _two_qubit_depth(
                part2_two_qubit_depth, "part2_two_qubit_depth"
            ),
        },
        "ex4_2",
    )
