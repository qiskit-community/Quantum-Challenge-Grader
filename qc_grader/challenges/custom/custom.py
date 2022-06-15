#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2022
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from pathlib import Path
from typeguard import typechecked
from typing import Optional

from qiskit import QuantumCircuit
import numpy as np

from qc_grader.grader.grade import grade


challenge_id = Path(__file__).parent.name

CRYPTO_INSTALL_INSTRUCTIONS = """
To encrypt solution unitaries, you must install extra cryptographic packages.
Please try:

    pip install rsa
    pip install cryptography

Then restart the kernel and try again."""

@typechecked
def grade_custom_unitary(answer: QuantumCircuit, solution: dict) -> None:
    answer.metadata = {'solution': solution}
    grade(answer, 'unitary', challenge_id)

@typechecked
def encrypt_solution(unitary: np.array) -> None:
    """This function encrypts unitaries for use as the `solution` argument
    in `grade_custom_unitary`.
    """
    try:
        # Don't want to make this a req. for everyone using the grader, just
        # people that want to create questions
        import rsa
        from cryptography.fernet import Fernet
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(str(e) + CRYPTO_INSTALL_INSTRUCTIONS)

    # Encrypt unitary using new Fernet key
    unitary = np.array(unitary).data.tobytes()
    fkey = Fernet.generate_key()
    encrypted_unitary = Fernet(fkey).encrypt(unitary)

    # Now encrypt Fernet key using server's public key
    public_key = rsa.key.PublicKey(
        int('1681804555246373551170764072174202413960288905646845'
            '0819529006277701602644204098940486860670878549877440'
            '1228272654806107490150126902640733636802975981987966'
            '3569704744432396154762514996470376831294019919481865'
            '4222643969362572460983738729604039628300569363008399'
            '7969598025969505322402023905163635014069104327652089'
            '0139826323156243809718022863666552906794247439925191'
            '8254269496734484160321582123718490100841764139812597'
            '8471709131090361955348903007605451831158753993950927'
            '5081617058269583077709119155262252882531784070982975'
            '7808947050454461300173774335020490232088862608148203'
            '085002382107820305010304613035789843684618283'), 65537)

    encrypted_key = rsa.encrypt(
        fkey, public_key
    )
    solution = {'unitary': encrypted_unitary.decode('latin-1'),
               'key': encrypted_key.decode('latin-1')}

    print('String below describes the Python `dict` containing '
          'your encrypted unitary. Paste this as the `solution` '
          'argument into `grade_custom_unitary`:\n')
    print(str(solution))
