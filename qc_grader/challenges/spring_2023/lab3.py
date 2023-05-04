# (C) Copyright IBM 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typeguard import typechecked

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade


_challenge_id = 'spring_2023'


@typechecked
def grade_ex3a(circuit: QuantumCircuit) -> None:
    grade(circuit, 'ex3a', _challenge_id)


@typechecked
def grade_ex3b(circuit: QuantumCircuit) -> None:
    grade(circuit, 'ex3b', _challenge_id)


@typechecked
def grade_ex3c(circuit: QuantumCircuit) -> None:
    grade(circuit, 'ex3c', _challenge_id)


@typechecked
def grade_ex3d(step1_bit: int) -> None:
    grade(step1_bit, 'ex3d', _challenge_id)
