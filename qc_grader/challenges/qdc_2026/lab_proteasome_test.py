"""Client tests for lab_proteasome: run with ``pytest`` in a checkout of the client repo.

Every number below is synthetic. This repository is public, so no reference value of the
challenge appears here; the tests only check packing, casting and the refusal hints.
"""

from typing import Any
from unittest.mock import patch

import numpy as np
import pytest
from typeguard import TypeCheckError

from qc_grader.challenges.qdc_2026 import lab_proteasome as lab
from qc_grader.custom_encoder import to_json

GRADE = "qc_grader.challenges.qdc_2026.lab_proteasome.grade_answer"

FRAGMENTS = {
    5: (20, 10, 10),
    7: (24, 13, 11),
    11: (21, 12, 9),
}  # synthetic ids and counts
GRID = {label: -10.0 - 0.1 * index for index, label in enumerate(lab.GRID_LABELS)}
ENERGIES = {key: -20.0 - index for index, key in enumerate(lab.EX5_KEYS)}


def submitted(function: Any, bundle: dict[str, Any]) -> tuple[Any, str]:
    with patch(GRADE) as grade:
        function(bundle)
    assert grade.call_count == 1
    kwargs = grade.call_args.kwargs
    assert kwargs["challenge"] == "qdc_2026" and kwargs["lab"] == "lab_proteasome"
    answer = grade.call_args.args[0]
    assert len(to_json(answer)) < 10_000  # serialisable, and small
    return answer, kwargs["exercise"]


def test_ex1_packs_a_plain_float() -> None:
    answer, exercise = submitted(
        lab.grade_lab_proteasome_ex1, {"hartree_fock_energy": np.float64(-1.25)}
    )
    assert exercise == "ex1"
    assert answer == {"hartree_fock_energy": -1.25}
    assert type(answer["hartree_fock_energy"]) is float


def test_ex2_sends_string_ids_and_plain_ints() -> None:
    bundle = {
        "fragment_count": np.int64(len(FRAGMENTS)),
        "fragments": {
            np.int64(fid): {
                "n_orb": np.int64(n_orb),
                "n_occ": n_occ,
                "n_vir": float(n_vir),
            }
            for fid, (n_orb, n_occ, n_vir) in FRAGMENTS.items()
        },
    }
    answer, exercise = submitted(lab.grade_lab_proteasome_ex2, bundle)
    assert exercise == "ex2"
    assert (
        answer["fragment_count"] == len(FRAGMENTS)
        and type(answer["fragment_count"]) is int
    )
    assert list(answer["fragments"]) == [str(fid) for fid in FRAGMENTS]
    for fid, (n_orb, n_occ, n_vir) in FRAGMENTS.items():
        record = answer["fragments"][str(fid)]
        assert record == {"n_orb": n_orb, "n_occ": n_occ, "n_vir": n_vir}
        assert all(type(v) is int for v in record.values())


def test_ex2_rejects_malformed_records() -> None:
    with pytest.raises(ValueError, match="needs n_orb"):
        lab.grade_lab_proteasome_ex2(
            {"fragment_count": 1, "fragments": {5: {"n_orb": 20}}}
        )
    with pytest.raises(ValueError, match="unexpected fields"):
        lab.grade_lab_proteasome_ex2(
            {
                "fragment_count": 1,
                "fragments": {
                    5: {"n_orb": 20, "n_occ": 10, "n_vir": 10, "sqd_n_qubits": 40}
                },
            }
        )
    with pytest.raises(ValueError, match="must be an integer"):
        lab.grade_lab_proteasome_ex2(
            {
                "fragment_count": 1,
                "fragments": {5: {"n_orb": 20.5, "n_occ": 10, "n_vir": 10}},
            }
        )
    with pytest.raises(ValueError, match="must be a dict"):
        lab.grade_lab_proteasome_ex2({"fragment_count": 1, "fragments": [5]})


def test_ex3_packs_three_energies() -> None:
    bundle = {
        "single_fragment_sqd_energy": -3.1,
        "single_fragment_trimsqd_energy": np.float64(-3.2),
        "single_fragment_ccsd_energy": -3.3,
    }
    answer, exercise = submitted(lab.grade_lab_proteasome_ex3, bundle)
    assert exercise == "ex3" and answer == {
        key: float(value) for key, value in bundle.items()
    }


def test_ex3_pending_value_names_the_cell() -> None:
    bundle = {
        "single_fragment_sqd_energy": None,
        "single_fragment_trimsqd_energy": -3.2,
        "single_fragment_ccsd_energy": -3.3,
    }
    with pytest.raises(ValueError, match=r"PENDING.*3b\.1"):
        lab.grade_lab_proteasome_ex3(bundle)


def test_ex4_packs_grid_and_best_config() -> None:
    bundle: dict[str, Any] = {**GRID, "best_config": " sqd_800 "}
    answer, exercise = submitted(lab.grade_lab_proteasome_ex4, bundle)
    assert exercise == "ex4"
    assert answer == {**GRID, "best_config": "sqd_800"}


def test_ex4_rejects_a_mistyped_label_and_an_incomplete_grid() -> None:
    with pytest.raises(ValueError, match="not a grid label"):
        lab.grade_lab_proteasome_ex4({**GRID, "best_config": "sqd_80"})
    with pytest.raises(ValueError, match="must be a grid label"):
        lab.grade_lab_proteasome_ex4({**GRID, "best_config": None})
    partial = dict(GRID)
    del partial["trim_800_r15"]
    with pytest.raises(ValueError, match=r"missing \['trim_800_r15'\]"):
        lab.grade_lab_proteasome_ex4({**partial, "best_config": "sqd_800"})


def test_ex5_packs_eleven_energies() -> None:
    answer, exercise = submitted(
        lab.grade_lab_proteasome_ex5, {k: np.float64(v) for k, v in ENERGIES.items()}
    )
    assert exercise == "ex5" and answer == ENERGIES
    assert len(answer) == 11 and all(type(v) is float for v in answer.values())


def test_ex5_rejects_nan_and_wrong_keys() -> None:
    bad = dict(ENERGIES)
    bad["fragment_9_energy"] = float("nan")
    with pytest.raises(ValueError, match="NaN"):
        lab.grade_lab_proteasome_ex5(bad)
    with pytest.raises(ValueError, match="unexpected \\['fragment_5_energy'\\]"):
        lab.grade_lab_proteasome_ex5({**ENERGIES, "fragment_5_energy": -1.0})


def test_ex6_packs_the_total_energy() -> None:
    answer, exercise = submitted(
        lab.grade_lab_proteasome_ex6, {"ixazomib_total_energy": -42.5}
    )
    assert exercise == "ex6" and answer == {"ixazomib_total_energy": -42.5}


def test_ex6_rejects_a_boolean_and_a_string() -> None:
    with pytest.raises(ValueError, match="boolean"):
        lab.grade_lab_proteasome_ex6({"ixazomib_total_energy": True})
    with pytest.raises(ValueError, match="must be a number"):
        lab.grade_lab_proteasome_ex6({"ixazomib_total_energy": "PENDING"})


def test_non_dict_bundle_is_a_type_error() -> None:
    with pytest.raises(TypeCheckError):
        lab.grade_lab_proteasome_ex1(-1.0)  # ty: ignore[invalid-argument-type]


def test_nothing_is_submitted_when_the_bundle_is_rejected() -> None:
    with patch(GRADE) as grade, pytest.raises(ValueError):
        lab.grade_lab_proteasome_ex1({"hartree_fock_energy": None})
    grade.assert_not_called()
