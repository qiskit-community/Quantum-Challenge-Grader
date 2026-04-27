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
        match type(o).__name__:
            case numpy.ndarray.__name__:
                return serializer.dump_numpy_ndarray(o)
            case numpy.complex128.__name__:
                return serializer.dump_numpy_complex(o)
            case complex.__name__:
                return serializer.dump_complex(o)
            case Fraction.__name__:
                return serializer.dump_fraction(o)
            case QuantumCircuit.__name__:
                return serializer.dump_quantum_circuit(o)
            case Statevector.__name__:
                return serializer.dump_state_vector(o)
            case SparsePauliOp.__name__:
                return serializer.dump_sparse_pauli_op(o)
            case _:
                return json.JSONEncoder.default(self, o)
