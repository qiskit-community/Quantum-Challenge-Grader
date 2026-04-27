# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


from fractions import Fraction
import numpy

from io import BytesIO

from qiskit import QuantumCircuit, qpy
from qiskit.quantum_info import SparsePauliOp, Statevector


def dump_numpy_ndarray(obj: numpy.ndarray):
    with BytesIO() as container:
        numpy.save(container, obj, allow_pickle=False)
        array = container.getvalue()
    return {"__class__": "numpy.ndarray", "ndarray": array.decode("ISO-8859-1")}


def dump_numpy_complex(obj: numpy.complex128):
    return {"__class__": "numpy.complex128", "re": obj.real, "im": obj.imag}


def dump_complex(obj: complex):
    return {"__class__": "complex", "re": obj.real, "im": obj.imag}


def dump_fraction(obj: Fraction):
    return {
        "__class__": "Fraction",
        "numerator": obj.numerator,
        "denominator": obj.denominator,
    }


def dump_quantum_circuit(obj: QuantumCircuit):
    with BytesIO() as container:
        qpy.dump(obj, container)
        circuit = container.getvalue()
    return {"__class__": "QuantumCircuit", "qc": circuit.decode("ISO-8859-1")}


def dump_state_vector(obj: Statevector):
    return {"__class__": "Statevector", "data": obj.data}


def dump_sparse_pauli_op(obj: SparsePauliOp):
    return {"__class__": "SparsePauliOp", "op": obj.to_list()}
