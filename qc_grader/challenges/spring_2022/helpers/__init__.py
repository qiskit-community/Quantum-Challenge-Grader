from typing import List
import numpy as np

# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Instruction, Parameter
from qiskit.tools.jupyter import *
from qiskit.visualization import *


def generate_ZZ(t: Parameter) -> Instruction:
    ZZ_qr = QuantumRegister(2)
    ZZ_qc = QuantumCircuit(ZZ_qr, name='ZZ')
    ZZ_qc.cnot(0, 1)
    ZZ_qc.rz(2 * t, 1)
    ZZ_qc.cnot(0, 1)
    ZZ = ZZ_qc.to_instruction()
    return ZZ


def generate_XX(t: Parameter) -> Instruction:
    ZZ = generate_ZZ(t)
    XX_qr = QuantumRegister(2)
    XX_qc = QuantumCircuit(XX_qr, name='XX')
    XX_qc.h([0, 1])
    XX_qc.append(ZZ, [0, 1])
    XX_qc.h([0, 1])
    XX = XX_qc.to_instruction()
    return XX


def generate_YY(t: Parameter) -> Instruction:
    ZZ = generate_ZZ(t)
    YY_qr = QuantumRegister(2)
    YY_qc = QuantumCircuit(YY_qr, name='YY')
    YY_qc.sdg([0, 1])
    YY_qc.h([0, 1])
    YY_qc.append(ZZ, [0, 1])
    YY_qc.h([0, 1])
    YY_qc.s([0, 1])
    YY = YY_qc.to_instruction()
    return YY


def generate_tb_trotter_instruction(
    t: Parameter,
    num_qubits: int
) -> Instruction:
    XX = generate_XX(t)
    YY = generate_YY(t)

    Trot_qr = QuantumRegister(num_qubits)
    Trot_qc = QuantumCircuit(Trot_qr, name='Trot')
    for i in np.arange(0, num_qubits - 1, 2):
        Trot_qc.append(YY, [Trot_qr[i], Trot_qr[i+1]])
        Trot_qc.append(XX, [Trot_qr[i], Trot_qr[i+1]])

    for i in np.arange(1, num_qubits - 1, 2):
        Trot_qc.append(YY, [Trot_qr[i], Trot_qr[i+1]])
        Trot_qc.append(XX, [Trot_qr[i], Trot_qr[i+1]])
    Trot_gate = Trot_qc.to_instruction()

    return Trot_gate


def generate_disordered_tb_instruction(
    t: Parameter,
    deltas: List[int],
    num_qubits: int
) -> Instruction:
    Trot_qr_disorder = QuantumRegister(num_qubits)
    Trot_qc_disorder = QuantumCircuit(Trot_qr_disorder, name='Trot disorder')

    tb_trotter_instruction = generate_tb_trotter_instruction(t, num_qubits)
    Trot_qc_disorder.append(tb_trotter_instruction, [i for i in range(num_qubits)])

    for idx in range(num_qubits):
        Trot_qc_disorder.rz(2 * t * deltas[idx], idx)

    # Convert custom quantum circuit into a gate
    Trot_disorder_gate = Trot_qc_disorder.to_instruction()

    return Trot_disorder_gate
