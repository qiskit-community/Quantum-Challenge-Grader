# (C) Copyright IBM 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import pickle
from datetime import datetime
from typing import Any, Callable

import networkx as nx
import numpy as np
from moocore import hypervolume
from qiskit import QuantumCircuit
from typeguard import check_type, typechecked

from qc_grader.grader.grade import grade_answer, submit_team_name

from .qmoo_files import load_problem

_LAB = "lab_qmoo"


def _create_grade_function(challenge: str):
    """Create a grade function for a specific challenge."""

    def _grade(answer: Any, exercise: str) -> None:
        grade_answer(answer, lab=_LAB, exercise=exercise, challenge=challenge)

    return _grade


def _create_submit_name_function(challenge: str):
    """Create a submit_name function for a specific challenge."""

    @typechecked
    def submit_name(name: str) -> None:
        submit_team_name(name, challenge)

    return submit_name


def _create_grade_lab_qmoo_ex1(_grade):
    """Create grade_lab_qmoo_ex1 function."""

    @typechecked
    def grade_lab_qmoo_ex1(gen_cvecs: Callable) -> None:
        samples = []
        for _ in range(3):
            for n in [10, 100, 1000]:
                v = gen_cvecs(n_samples=n)
                check_type(v, np.array)
                if v.shape != (n, 3):
                    print(
                        "Wrong shape generated for",
                        n,
                        "samples, shape=",
                        v.shape,
                        "expected=",
                        (n, 3),
                    )
                    continue

                if not np.issubdtype(v.dtype, np.number):
                    print("Numpy array includes non-numbers!")
                    continue

                samples.append(v)

        answer_dict = {"samples": samples}
        _grade(answer_dict, "ex1")

    return grade_lab_qmoo_ex1


def _create_grade_lab_qmoo_ex2(_grade):
    """Create grade_lab_qmoo_ex2 function."""

    @typechecked
    def grade_lab_qmoo_ex2(user_hv: float) -> None:
        check_type(user_hv, float)
        answer_dict = {"user_hv": user_hv}
        _grade(answer_dict, "ex2")

    return grade_lab_qmoo_ex2


def _create_grade_lab_qmoo_ex3(_grade):
    """Create grade_lab_qmoo_ex3 function."""

    @typechecked
    def grade_lab_qmoo_ex3(qc: QuantumCircuit) -> None:
        check_type(qc, QuantumCircuit)
        answer_dict = {"qc": qc}
        _grade(answer_dict, "ex3")

    return grade_lab_qmoo_ex3


def _create_grade_lab_qmoo_ex4(_grade):
    """Create grade_lab_qmoo_ex4 function."""

    @typechecked
    def grade_lab_qmoo_ex4(
        user_hv: float,
        samples: np.array,  # ty: ignore[invalid-type-form]
        isa_qc: QuantumCircuit,
        params: dict,
        job_ids: list,
    ) -> None:
        check_type(isa_qc, QuantumCircuit)
        check_type(user_hv, float)
        check_type(params, dict)
        check_type(job_ids, list)
        check_type(samples, np.array)

        if isa_qc is None:
            print("Invalid quantum circuit submitted")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn_samples = f"results/3_regular_static_80q/samples_{timestamp}.npz"
        fn_hvs = f"results/3_regular_static_80q/hvs_{timestamp}.npz"
        fn_params = f"results/3_regular_static_80q/params_{timestamp}.npz"
        fn_job = f"results/3_regular_static_80q/job_{timestamp}.npz"
        np.savez_compressed(fn_samples, array=samples)
        np.savez_compressed(fn_hvs, array=np.array(user_hv))
        pickle.dump(params, open(fn_params, "wb"))
        pickle.dump(job_ids, open(fn_job, "wb"))

        moo_graphs, _, upper, lower = load_problem(
            "./instances/3_regular_static_80q/", False
        )
        n_obj = len(moo_graphs)

        adj_m = [nx.adjacency_matrix(moo_graphs[i]).toarray() for i in range(n_obj)]
        post_samples = samples

        fis = np.stack(
            [
                np.sum((post_samples @ adj_m[i]) * (1 - post_samples), axis=1)
                for i in range(n_obj)
            ],
            axis=1,
        )

        hv = hypervolume(fis, ref=lower, maximise=True)

        if abs(hv - user_hv) > 1000:
            print(
                "The hypervolume submitted by the user does not match the implied hypervolume"
            )
            return None

        answer_dict = {
            "user_hv": user_hv,
        }
        _grade(answer_dict, "ex4")

    return grade_lab_qmoo_ex4
