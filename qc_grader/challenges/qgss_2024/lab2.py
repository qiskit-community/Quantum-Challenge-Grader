import json
from typeguard import typechecked

from qiskit_experiments.framework import ExperimentData, ExperimentEncoder
from qiskit.quantum_info import PTM

from qc_grader.grader.grade import grade


_challenge_id = 'qgss_2024'


@typechecked
def grade_lab2_ex1(
    backend,
    exp_data: ExperimentData,
    t1_ptm: PTM
) -> None:
    # In case it's still running...
    exp_data.block_for_results()

    if err := exp_data.errors():
        print(f"It looks like your experiment raised an error: {err}")
        return

    json_exp_data = json.dumps(exp_data, cls=ExperimentEncoder)
    grade({
        'backend_name': backend.name,
        'experiment_data': json_exp_data,
        'ptm_data': t1_ptm.data,
    }, 'lab2-ex1', _challenge_id)


@typechecked
def grade_lab2_ex2(max_feasible_circuit_depth: int) -> None:
    grade(max_feasible_circuit_depth, 'lab2-ex2', _challenge_id)
