from qiskit import QuantumCircuit

from qc_grader.grade import grade_qobj, submit_qobj
from qiskit.qobj import PulseQobj


def grade_ex4(qobj: PulseQobj) -> None:
    ok, _ = grade_qobj(qobj, 'ex4')
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex4(qobj: PulseQobj) -> None:
    submit_qobj(qobj, 'ex4')
