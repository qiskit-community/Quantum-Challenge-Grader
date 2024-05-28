from math import pi

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap


def get_qc_in(nq, pg):
    # QFT circuit, feel free to use a previously transpiled QFT circuit
    qc_qft = transpile(QFT(nq, do_swaps=False), coupling_map=CouplingMap.from_line(5),
                        basis_gates=GenericBackendV2(nq).operation_names, seed_transpiler=307)
    # part of the circuit including the Peres gate
    qc_inner = QuantumCircuit(nq)
    for i in range(1, nq - 1):
        qc_inner.append(pg, [nq - i - 2, nq - i - 1, nq - 1])

    qc_in = QuantumCircuit(nq)
    # add QFT circuit to qc_in
    qc_in.compose(qc_qft, range(nq), inplace=True)

    # perform swap gates
    for i in range(nq // 2):
        qc_in.cx(i, nq - i - 1)
        qc_in.cx(nq - i - 1, i)
        qc_in.cx(i, nq - i - 1)

    qc_in.rz(pi, nq - 1)
    # add circuit with peres gates
    qc_in.compose(qc_inner, range(nq), inplace=True)

    # perform swap gates
    for i in range(nq // 2):
        qc_in.cx(i, nq - i - 1)
        qc_in.cx(nq - i - 1, i)
        qc_in.cx(i, nq - i - 1)
    # add inverse QFT circuit
    qft_inv = transpile(qc_qft.inverse(), coupling_map=CouplingMap.from_line(5),
                        basis_gates=GenericBackendV2(nq).operation_names, seed_transpiler=307)
    qc_in.compose(qft_inv, range(nq), inplace=True)
    return qc_in
