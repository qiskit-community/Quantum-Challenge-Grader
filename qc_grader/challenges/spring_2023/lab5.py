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

from typing import Callable

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade, get_problem_set


_challenge_id = 'spring_2023'


@typechecked
def grade_ex5a(circuit: QuantumCircuit) -> None:
    grade(circuit, 'ex5a', _challenge_id, byte_string=True)


@typechecked
def grade_ex5b(circuit: QuantumCircuit) -> None:
    grade(circuit, 'ex5b', _challenge_id, byte_string=True)


@typechecked
def grade_ex5c(test_ghz_func: Callable) -> None:
    _, inputs = get_problem_set('ex5c', _challenge_id)

    answer = []
    for i in inputs:
        result = test_ghz_func(i)
        answer.append((i, result))

    grade(answer, 'ex5c', _challenge_id)
