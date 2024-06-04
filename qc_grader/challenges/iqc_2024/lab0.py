from typing import List
from typeguard import typechecked

from matplotlib.container import BarContainer


from qiskit import QuantumCircuit
from qiskit.primitives import PrimitiveJob
from qiskit.providers import JobStatus
from qiskit.quantum_info import Pauli

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab0_ex1(observables: List[Pauli]) -> None:
    grade(observables, 'lab0-ex1', _challenge_id)


@typechecked
def grade_lab0_ex2(plt: BarContainer, job: PrimitiveJob) -> None:
    status = job.status()
    if status != JobStatus.DONE:
        print(f'Please wait for Job to complete succesfully before grading: {status}')
    else:
        answer = {
<<<<<<< HEAD
            'job_result': job.result(),
=======
            'job_result': job.result()[0].data.evs,
>>>>>>> upstream/main
            'pyplot': {
                'type': type(plt).__name__,
                'values': plt.datavalues,
                'children': [type(c).__name__ for c in plt.get_children()]
            }
        }
        grade(answer, 'lab0-ex2', _challenge_id)
