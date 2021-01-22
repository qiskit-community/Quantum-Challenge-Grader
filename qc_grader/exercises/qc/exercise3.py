from typing import Optional
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Parameter
from qiskit.circuit.library import CXGate

import json
import numpy as np

from qc_grader.exercises import SubmissionError
from qc_grader.grade import grade_json, submit_json
from qc_grader.util import circuit_to_json


def get_cost_vars(qc: QuantumCircuit):
    nqubits = len(qc.qubits)
    G = 0
    D = qc.depth()
    for gate, qubits, _ in qc.data:
        if len(qubits) > 1:
            if isinstance(gate, CXGate):
                G += 1
            else:
                raise SubmissionError('Only multi-qubit gates allowed are CNOTs (CXGate), found '
                                      f'{type(gate).__name__}')
    return G, D, nqubits


def _validate_and_prepare_circuit(qc: QuantumCircuit, m: int) -> bool:
    """Verifies the circuit and runs an experiment using the 'unitary_simulator'.
        Args:
           qc (QuantumCircuit): QuantumCircuit to validate. Input register must
                                have name 'input' and size 3, all other qubits will be
                                treated as scratch qubits. Circuit must have exactly two
                                parameters named 'alpha' and 'beta'.
           m (int): Index of boolean function to create oracle for (see question).
       Returns:
           List: list of a dictionary objects containing the 'alpha' and 'beta'
                    parameter values used in teh experiment and also the 'unitary'
                    result from the experiment.
    """
    print(f'\r\nVerifying your circuit for m={m} ...')

    try:
        alpha = next(x for x in qc.parameters if x.name == 'alpha')
    except StopIteration as err:
        raise SubmissionError(
            "Could not find Parameter named 'alpha'. "
            "(See: https://qiskit.org/documentation/stubs/qiskit.circuit.Parameter.html )"
        )

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
    if nqubits > 10:
        raise SubmissionError("Circuit cannot contain more than ten qubits.")

    # Make sure 'input' is always first
    qr = QuantumRegister(3, 'input')
    pre_qc = QuantumCircuit(qr)
    qc = pre_qc + qc
    if len(qc.qubits) != nqubits:  # Probably register name mismatch
        raise SubmissionError("You must name your three-qubit input register 'input'.")

    circuits = []

    for trials in range(30):
        a = np.random.rand()*np.pi*2
        b = np.random.rand()*np.pi*2
        param = {
            alpha: a,
            beta: b
        }
        
        circuits.append({
            'alpha': a,
            'beta': b,
            'qc': circuit_to_json(qc, parameter_binds=[param])
        })
        
    return circuits


def grade_ex3(circuit: QuantumCircuit, m: int) -> Optional[int]:
    runs = _validate_and_prepare_circuit(circuit, m)
    g, d, n = get_cost_vars(circuit)

    circuit_runs = {
        'circuits': json.dumps(runs),
        'cost': { 'm': m, 'G': g, 'D': d, 'nqubits': n }
    }

    ok, score = grade_json(circuit_runs, 'ex3')
    if ok:
        return score


def grade_ex3(circuit: QuantumCircuit, m: int) -> None:
    runs = _validate_and_prepare_circuit(circuit, m)
    g, d, n = get_cost_vars(circuit)

    circuit_runs = {
        'circuits': json.dumps(runs),
        'cost': { 'm': m, 'G': g, 'D': d, 'nqubits': n }
    }
    submit_json(circuit_runs, 'ex3')
