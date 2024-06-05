from typing import List
from typeguard import typechecked

from matplotlib.container import BarContainer


from qiskit import QuantumCircuit
from qiskit.primitives import PrimitiveJob
from qiskit.providers import JobStatus
from qiskit.quantum_info import SparsePauliOp

from qc_grader.grader.grade import grade


_challenge_id = 'iqc_2024'


@typechecked
def grade_lab0_ex1(observables: List[SparsePauliOp]) -> None:
    grade(observables, 'lab0-ex1', _challenge_id)
