import json

from typing import Callable, Type

from typeguard import typechecked


from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Gate
from qiskit.circuit.library import QFT
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import StagedPassManager, CouplingMap, AnalysisPass, TransformationPass

from qc_grader.grader.grade import grade
from .utils import get_qc_in


_challenge_id = 'qgss_2025'



@typechecked
def grade_lab0_ex1(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab0-ex1', _challenge_id)


@typechecked
def grade_lab0_ex2(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab0-ex2', _challenge_id)



