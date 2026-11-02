"""QDC 2026 - Proteasome inhibitors: grading functions for ``lab_proteasome``.

Each function takes the ``bundle`` dict that the notebook builds in its "Exercise <n>" cell,
checks it, casts every number to a plain float or int, and submits one answer. A bundle that
cannot be graded (a PENDING value, a missing key, a NaN) raises ``ValueError`` whose first
sentence says what to fix; nothing is submitted in that case.
"""

import math
from collections.abc import Iterable
from typing import Any

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qdc_2026"
_LAB = "lab_proteasome"

GRID_LABELS = (
    "sqd_500",
    "sqd_800",
    "trim_500_r05",
    "trim_500_r15",
    "trim_500_r30",
    "trim_800_r05",
    "trim_800_r15",
    "trim_800_r30",
)
QUANTUM_FRAGMENT_IDS = (1, 2, 3, 4, 6, 8, 9, 13, 17, 19, 22)
EX2_FIELDS = ("n_orb", "n_occ", "n_vir")
EX3_KEYS = (
    "single_fragment_sqd_energy",
    "single_fragment_trimsqd_energy",
    "single_fragment_ccsd_energy",
)
EX5_KEYS = tuple(f"fragment_{fid}_energy" for fid in QUANTUM_FRAGMENT_IDS)


def _grade(answer: dict[str, Any], exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


def _check_keys(bundle: dict[str, Any], expected: Iterable[str], cell: str) -> None:
    wanted = list(expected)
    missing = [key for key in wanted if key not in bundle]
    unexpected = [key for key in bundle if key not in wanted]
    if missing or unexpected:
        raise ValueError(
            f"bundle must have exactly the keys {wanted}; missing {missing}, unexpected "
            f"{unexpected}. Build it as in the '{cell}' cell of the notebook."
        )


def _energy(bundle: dict[str, Any], key: str, cell: str) -> float:
    """The value under ``key`` as a finite float, with a hint for the common slips."""
    value = bundle[key]
    if value is None:
        raise ValueError(
            f"{key} is None (PENDING): run {cell} to completion, then grade again."
        )
    if isinstance(value, bool):
        raise ValueError(f"{key} is a boolean; pass the energy in Ha from {cell}.")
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"{key} must be a number in Ha, got {type(value).__name__}."
        ) from err
    if not math.isfinite(number):
        raise ValueError(
            f"{key} is NaN or infinite: {cell} did not produce a valid energy."
        )
    return number


def _count(value: Any, what: str) -> int:
    """An orbital count or fragment id as a plain int (numpy ints and 21.0 are fine)."""
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{what} must be an integer, got {value!r}.")
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"{what} must be an integer, got {type(value).__name__}."
        ) from err
    if not math.isfinite(number) or number != int(number):
        raise ValueError(f"{what} must be an integer, got {value!r}.")
    return int(number)


@typechecked
def grade_lab_proteasome_ex1(bundle: dict[str, Any]) -> None:
    """Submit the ``bundle`` of the "Exercise 1 - Hartree-Fock Energy" cell.

    It is ``{"hartree_fock_energy": float(mf_ref.meta["hf_energy"])}`` from Section 1.
    """
    _check_keys(bundle, ("hartree_fock_energy",), "Exercise 1")
    _grade(
        {
            "hartree_fock_energy": _energy(
                bundle, "hartree_fock_energy", "Section 1 (Hartree-Fock)"
            )
        },
        "ex1",
    )


@typechecked
def grade_lab_proteasome_ex2(bundle: dict[str, Any]) -> None:
    """Submit the ``bundle`` of the "Exercise 2 - EWF Fragment Selection" cell.

    It is ``{"fragment_count": len(_sel_df), "fragments": {fragment_id: {"n_orb", "n_occ",
    "n_vir"}}}`` built from the selected rows of Stage D. Fragment ids are sent as strings.
    """
    _check_keys(bundle, ("fragment_count", "fragments"), "Exercise 2")
    fragments = bundle["fragments"]
    if not isinstance(fragments, dict):
        raise ValueError(
            "bundle['fragments'] must be a dict {fragment_id: {'n_orb', 'n_occ', 'n_vir'}} "
            "built from _sel_df as in the Exercise 2 cell."
        )
    packed: dict[str, dict[str, int]] = {}
    for fid, record in fragments.items():
        key = str(_count(fid, "fragment id"))
        if not isinstance(record, dict):
            raise ValueError(
                f"fragments[{fid!r}] must be a dict with n_orb, n_occ and n_vir."
            )
        extra = [field for field in record if field not in EX2_FIELDS]
        if extra:
            raise ValueError(
                f"fragments[{fid!r}] has unexpected fields {extra}; send only n_orb, n_occ and n_vir."
            )
        if any(field not in record for field in EX2_FIELDS):
            raise ValueError(
                f"fragments[{fid!r}] needs n_orb, n_occ and n_vir (Stage D catalog columns)."
            )
        packed[key] = {
            field: _count(record[field], f"fragments[{fid!r}][{field!r}]")
            for field in EX2_FIELDS
        }
    _grade(
        {
            "fragment_count": _count(bundle["fragment_count"], "fragment_count"),
            "fragments": packed,
        },
        "ex2",
    )


@typechecked
def grade_lab_proteasome_ex3(bundle: dict[str, Any]) -> None:
    """Submit the ``bundle`` of the "Exercise 3 - Single-Fragment Solver Energies" cell.

    It holds ``single_fragment_sqd_energy`` (``answer_08``), ``single_fragment_trimsqd_energy``
    (``e_trim``) from 3b.1 and ``single_fragment_ccsd_energy`` (``answer_07``) from 3a.
    """
    _check_keys(bundle, EX3_KEYS, "Exercise 3")
    cells = {
        "single_fragment_sqd_energy": "3b.1 (SQD/TrimSQD)",
        "single_fragment_trimsqd_energy": "3b.1 (SQD/TrimSQD)",
        "single_fragment_ccsd_energy": "3a (CCSD reference)",
    }
    _grade({key: _energy(bundle, key, cells[key]) for key in EX3_KEYS}, "ex3")


@typechecked
def grade_lab_proteasome_ex4(bundle: dict[str, Any]) -> None:
    """Submit the ``bundle`` of the "Exercise 4 - Tuning Grid" cell.

    It maps each of the eight grid labels to ``float(row["energy_ha"])`` of ``grid_df`` and
    adds ``best_config``, the label you identified as the lowest-energy configuration.
    """
    _check_keys(bundle, (*GRID_LABELS, "best_config"), "Exercise 4")
    best = bundle["best_config"]
    if not isinstance(best, str):
        raise ValueError(
            f"best_config must be a grid label (a string), got {type(best).__name__}."
        )
    best = best.strip()
    if best not in GRID_LABELS:
        raise ValueError(
            f"best_config {best!r} is not a grid label; use one of {', '.join(GRID_LABELS)}."
        )
    answer: dict[str, Any] = {
        label: _energy(bundle, label, "the tuning grid (E.3c)") for label in GRID_LABELS
    }
    answer["best_config"] = best
    _grade(answer, "ex4")


@typechecked
def grade_lab_proteasome_ex5(bundle: dict[str, Any]) -> None:
    """Submit the ``bundle`` of the "Exercise 5 - Submit TrimSQD fragment energies" cell.

    It maps ``fragment_<id>_energy`` to the TrimSQD energy (Ha) of each of the 11 quantum
    fragments of the full campaign (Section 6), ids 1, 2, 3, 4, 6, 8, 9, 13, 17, 19 and 22.
    """
    _check_keys(bundle, EX5_KEYS, "Exercise 5")
    _grade(
        {
            key: _energy(bundle, key, "the full campaign (Sections 6.2 and 6.3)")
            for key in EX5_KEYS
        },
        "ex5",
    )


@typechecked
def grade_lab_proteasome_ex6(bundle: dict[str, Any]) -> None:
    """Submit the ``bundle`` of the "Exercise 6 - Ixazomib Total Energy" cell.

    It is ``{"ixazomib_total_energy": float(stage4_summary["e_total"])}`` from F.2/F.3.
    """
    _check_keys(bundle, ("ixazomib_total_energy",), "Exercise 6")
    _grade(
        {
            "ixazomib_total_energy": _energy(
                bundle, "ixazomib_total_energy", "the Stage 4 reconstruction (F.2)"
            )
        },
        "ex6",
    )
