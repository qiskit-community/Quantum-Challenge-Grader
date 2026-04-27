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
import json
import numpy

from typing import Any

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

from . import serializer


def to_json(obj: Any) -> str:
    return json.dumps(obj, skipkeys=True, cls=GraderJSONEncoder)


class GraderJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        # The order sometimes matters: subclasses should appear before their parent class,
        # such as numpy.complex128 before complex.
        if isinstance(o, numpy.ndarray):
            return serializer.dump_numpy_ndarray(o)
        if isinstance(o, numpy.complex128):
            return serializer.dump_numpy_complex(o)
        if isinstance(o, complex):
            return serializer.dump_complex(o)
        if isinstance(o, Fraction):
            return serializer.dump_fraction(o)
        if isinstance(o, QuantumCircuit):
            return serializer.dump_quantum_circuit(o)
        if isinstance(o, Statevector):
            return serializer.dump_state_vector(o)
        if isinstance(o, SparsePauliOp):
            return serializer.dump_sparse_pauli_op(o)
        return json.JSONEncoder.default(self, o)
