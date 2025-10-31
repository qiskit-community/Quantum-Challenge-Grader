from typeguard import typechecked

from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade
from typeguard import check_type
import numpy as np
from datetime import datetime
import pickle
from moocore import hypervolume
import networkx as nx
from .qmoo_files import load_problem
from typing import Callable


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
def grade_lab5_ex1(gen_cvecs: Callable) -> None:
    samples = []
    for _ in range(3):
        for n in [10, 100, 1000]:
            v = gen_cvecs(n_samples=n)
            check_type(v, np.array)
            if v.shape != (n, 3):
                print("Wrong shape generated for", n, "samples, shape=", v.shape, "expected=", (n, 3))
                continue

            if not np.issubdtype(v.dtype, np.number):
                print("Numpy array includes non-numbers!")
                continue

            samples.append(v)  

    answer_dict = {"samples": samples}
    grade(answer_dict, "lab5-ex1", _challenge_id)


@typechecked
def grade_lab5_ex2(user_hv: float) -> None:
    check_type(user_hv, float)    
    answer_dict = {"user_hv": user_hv}
    grade(answer_dict, "lab5-ex2", _challenge_id)


@typechecked
def grade_lab5_ex3(qc: QuantumCircuit) -> None:
    check_type(qc, QuantumCircuit)
    answer_dict = {"qc": qc}
    grade(answer_dict, "lab5-ex3", _challenge_id)


@typechecked
def grade_lab_5_ex4(user_hv: float, samples: np.array, isa_qc: QuantumCircuit, params: dict, job_ids: list) -> None:
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
    pickle.dump(params, open(fn_params, 'wb'))
    pickle.dump(job_ids, open(fn_job, 'wb'))

    moo_graphs, _, upper, lower = load_problem("./instances/3_regular_static_80q/", False)
    n_obj = len(moo_graphs)

    adj_m = [nx.adjacency_matrix(moo_graphs[i]).toarray() for i in range(n_obj)]
    post_samples = samples

    fis = np.stack(
        [np.sum((post_samples @ adj_m[i]) * (1 - post_samples), axis=1) for i in range(n_obj)], axis=1)

    hv = hypervolume(fis, ref=lower, maximise=True)

    if abs(hv - user_hv) > 1000:
        print("The hypervolume submitted by the user does not match the implied hypervolume")
        return None
    
    answer_dict = {
        "hv": user_hv,
    }
    grade(answer_dict, "lab5-ex4", _challenge_id)
