# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from typing import Callable

from qiskit import QuantumCircuit
from qiskit.providers.ibmq.job import IBMQJob

from .grade import prepare_grading_job, grade, submit


__version__ = '0.1.0'


def grade_ex_1a(circuit: QuantumCircuit) -> None:
    grade(circuit, 'week1', 'exA')


def grade_ex_1b(answer: int) -> None:
    grade(answer, 'week1', 'exB')


def grade_ex_2a(job: IBMQJob) -> None:
    grade(job, 'week2', 'exA')


def grade_ex_2b(job: IBMQJob) -> None:
    grade(job, 'week2', 'exB')


def grade_ex_3(job: IBMQJob) -> None:
    grade(job, 'week3', 'exA')


def prepare_ex_3(solver_func: Callable) -> IBMQJob:
    return prepare_grading_job(solver_func, 'week3', 'exA')
