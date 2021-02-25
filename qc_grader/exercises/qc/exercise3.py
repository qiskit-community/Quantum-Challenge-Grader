from typing import List, Optional

import numpy as np

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Parameter


from qc_grader.exercises import SubmissionError
from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json


expected_circuit_count = 5
max_qubits_count = 10


def _quick_check_circuit(qc: QuantumCircuit, m: int) -> bool:
    """Check the circuit for expected parameters and input before sending to server
        for additional checks and grading.
        Args:
           qc (QuantumCircuit): QuantumCircuit to check. Input register must
                                have name 'input' and size 3, all other qubits will be
                                treated as scratch qubits. Circuit must have exactly one
                                parameter named 'beta'.
           m (int): Index of boolean function to create oracle for (see question).
       Returns:
           List: list of a dictionary objects containing the 'beta'
                    parameter value used and the JSON representation of circuit.
    """
    print(f'Checking for circuit {m} ...')

    try:
        beta = next(x for x in qc.parameters if x.name == 'beta')
    except StopIteration as err:
        if m == 0:  # beta has no effect so can forgive
            beta = Parameter('beta')
            qc = qc.copy()
            qc.rx(0*beta, 0)  # add gate including beta with no effect
        else:
            raise SubmissionError(
                "Could not find Parameter named 'beta'. "
                "(See: https://qiskit.org/documentation/stubs/qiskit.circuit.Parameter.html )"
            )

    nqubits = len(qc.qubits)
    if nqubits > max_qubits_count:
        raise SubmissionError(f'Circuit cannot contain more than {max_qubits_count} qubits.')

    # Make sure 'input' is always first
    qr = QuantumRegister(3, 'input')
    pre_qc = QuantumCircuit(qr)
    qc = pre_qc + qc
    if len(qc.qubits) != nqubits:  # Probably register name mismatch
        raise SubmissionError("You must name your three-qubit input register 'input'.")

    circuits = []

    for trials in range(30):
        b = np.random.rand()*np.pi*2
        param = {
            beta: b
        }
        
        circuits.append({
            'beta': b,
            'qc': circuit_to_json(qc, parameter_binds=[param])
        })
        
    return circuits


def _check_circuits(circuits: List[QuantumCircuit]) -> List:
    if len(circuits) != expected_circuit_count:
        raise SubmissionError(
            f'You must submit {expected_circuit_count} circuits. '
            'Review the exercise question for solution requirements.')

    circuits_checked = []
    for m, circuit in enumerate(circuits):
        checked = _quick_check_circuit(circuit, m)
        circuits_checked.append(checked)
    return circuits_checked


def grade_ex3(circuits: List[QuantumCircuit]) -> Optional[int]:
    try:
        circuits_checked = _check_circuits(circuits)
        ok, _ = grade_json(circuits_checked, 'ex3')
        if ok:
            print('Feel free to submit your answer.\r\n')
    except SubmissionError as err:
        print(err)


def submit_ex3(circuits: List[QuantumCircuit]) -> None:
    try:
        circuits_checked = _check_circuits(circuits)
        submit_json(circuits_checked, 'ex3')
    except SubmissionError as err:
        print(err)
