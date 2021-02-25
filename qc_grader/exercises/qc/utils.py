import logging

from typing import List, Tuple, Optional, Union

from qiskit import Aer, execute, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import CXGate


logger = logging.getLogger('qc_grading_server')

ValidationResult = Tuple[bool, Optional[Union[str, int, float]]]


class SubmissionError(BaseException):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def get_tests(question_number: int, part_number: int) -> Tuple[List, List]:
    """Returns test inputs and expected results for questions 1 & 2
       args:
               question_number (int): Question number of the challenge, can only be 1 or 2
               part_number (int): Part number within the question. Can be 1, 2 or 3 if
                                  question_number == 1, or 1 or 2 if question_number == 2
       returns:
           Tuple(list): test_inputs and expected_outputs for input into verify_circuit()
    """
    test_inputs = []
    expected_outputs = []

    if question_number == 1:
        test_inputs = ["{0:04b}".format(i) for i in range(16)]
        expected_outputs = ["{0:03b}".format(i.count('1'))[3-part_number] for i in test_inputs]
    elif question_number == 2:
        from numpy.random import randint
        if part_number == 1:
            test_inputs = ["{0:015b}".format(randint(2**15)) for i in range(15)]
            expected_outputs = ["{0:04b}".format(i.count('1')) for i in test_inputs]
        elif part_number == 2:
            test_inputs = ["{0:016b}".format(randint(2**15)) for i in range(15)]
            expected_outputs = ["{0:05b}".format(i.count('1')) for i in test_inputs]

    return test_inputs, expected_outputs


def verify_circuit(
        qc: QuantumCircuit,
        test_inputs: List[str],
        exp_outputs: List[str]
        ) -> bool:
    """Checks if a circuit is a valid submission.
       args:
               qc (QuantumCircuit): Quantum circuit to test. Cannot have any classical
                                   registers, must have two QuantumRegisters of size
                                   n and m, and with names 'input' and 'output' resp.
       returns:
               Bool: True if circuit is valid, working submission. Otherwise False.
    """
    svsim = Aer.get_backend('statevector_simulator')
    qasmsim = Aer.get_backend('qasm_simulator')
    n = sum(qubit.register.name == 'input' for qubit in qc.qubits)
    m = sum(qubit.register.name == 'output' for qubit in qc.qubits)
    s = len(qc.qubits) - (n+m)

    # Do some quick checks first
    if n != len(test_inputs[0]):
        raise SubmissionError(
            f"Circuit must have {len(test_inputs[0])} qubits in register 'input'."
        )
    if m != len(exp_outputs[0]):
        raise SubmissionError(
            f"Circuit must have {len(exp_outputs[0])} qubits in register 'output'."
        )
    if qc.clbits != []:
        raise SubmissionError("Circuit cannot have a classical register")

    # Begin logic tests
    for trial in range(len(test_inputs)):
        # Create circuit with correct inputs
        qr_n = QuantumRegister(n, 'input')
        qr_m = QuantumRegister(m, 'output')
        pre_qc = QuantumCircuit(qr_n, qr_m)
        for q in range(n):
            if test_inputs[trial][::-1][q] == '1':
                pre_qc.x(qr_n[q])

        post_qc = QuantumCircuit(qr_n, qr_m)
        for q in range(n):
            if test_inputs[trial][::-1][q] == '1':
                post_qc.x(qr_n[q])

        for q in range(m):
            if exp_outputs[trial][::-1][q] == '1':
                post_qc.x(qr_m[q])

        test_qc = pre_qc + qc + post_qc
        test_qc.measure_all()
        if len(test_qc.qubits) != len(qc.qubits):  # most likely mismatch b/c incorrect reg names
            raise SubmissionError("Could not interpret circuit correctly. Circuit must contain "
                                  "at least two registers with names 'input', 'output'.")

        # Simulate and check results
        if n < 10:
            # slower but more rigorous
            results = execute(test_qc, svsim).result().get_counts()
        else:
            results = execute(test_qc, qasmsim).result().get_counts()
        if len(results.keys()) > 1:
            raise SubmissionError(
                f"Failed on input: {test_inputs[trial]} (expected output: {exp_outputs[trial]})"
            )
        output = list(results)[0]
        if '1' in output:
            raise SubmissionError(
                f"Failed on input: {test_inputs[trial]} (expected output: {exp_outputs[trial]})"
            )
    return True


def precheck_exercise(
    qc: QuantumCircuit,
    question_number: int,
    part_number: int
) -> bool:
    print('Checking your circuit...')
    test_inputs, expected_outputs = get_tests(question_number, part_number)

    try:
        is_correct = verify_circuit(qc, test_inputs, expected_outputs)
    except SubmissionError as err:
        return False, err.message

    return True, None
