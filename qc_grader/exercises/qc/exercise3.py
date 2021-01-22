from qiskit import Aer, QuantumCircuit, QuantumRegister, execute
from qiskit.circuit import Parameter
from qiskit.circuit.library import CXGate

import base64
import json
import numpy as np

from qc_grader.exercises import SubmissionError
from qc_grader.grade import grade_json, submit_json
    

class ComplexEncoder(json.encoder.JSONEncoder):
    def default(self, obj):
        """If obj is a complex number encode by storing 'real' and 'imag' parts
            in a dictionary
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, complex):
            return {
                "__complex__": True,
                "real": obj.real,
                "imag": obj.imag
            }
        return json.JSONEncoder.default(self, obj)


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


def _validate_and_run_circuit(qc: QuantumCircuit, m: int) -> bool:
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
    print(f'Verifying your circuit for m={m} ...')

    usim = Aer.get_backend('unitary_simulator')

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

    trial_submissions = []

    for trials in range(30):
        a = np.random.rand()*np.pi*2
        b = np.random.rand()*np.pi*2
        param = {
            alpha: a,
            beta: b
        }
        submission = execute(qc, usim, parameter_binds=[param]).result().get_unitary()
        
        trial_submissions.append({
            'alpha': a,
            'beta': b,
            'unitary': submission
        })
        
    return trial_submissions


def validate_ex3(circuit: QuantumCircuit, m: int) -> dict:
    runs = _validate_and_run_circuit(circuit, m)
    g, d, n = get_cost_vars(circuit)
    submission = {
        'output': json.dumps(runs, cls=ComplexEncoder),
        'qc': { 'm': m, 'G': g, 'D': d, 'nqubits': n }
    }
    return submission


def grade_ex3(submissions: list) -> None:
    if grade_json(submissions, 'ex3'):
        print('Feel free to submit your answer.\r\n')


def submit_ex3(submissions: list) -> None:
    submit_json(submissions, 'ex3')
