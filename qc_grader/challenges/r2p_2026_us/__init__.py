# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from qc_grader.grader.grade import create_join_team_function

from .lab_sqd import (
    grade_lab_sqd_ex1,
    grade_lab_sqd_ex2,
    grade_lab_sqd_ex3,
    grade_lab_sqd_ex4,
    grade_lab_sqd_ex5,
    grade_lab_sqd_ex6,
)

from .lab_qmoo import (
    grade_lab_qmoo_ex1,
    grade_lab_qmoo_ex2,
    grade_lab_qmoo_ex3,
    grade_lab_qmoo_ex4,
)

from .lab_hadron import (
    grade_lab_hadron_ex1,
    grade_lab_hadron_ex2,
    grade_lab_hadron_ex3,
    grade_lab_hadron_ex4,
    grade_lab_hadron_ex5,
    grade_lab_hadron_ex6,
    grade_lab_hadron_ex7,
    grade_lab_hadron_ex8,
    grade_lab_hadron_ex9,
    grade_lab_hadron_ex10,
    grade_lab_hadron_ex11,
)

_CHALLENGE = "r2p_2026_us"
join_team = create_join_team_function(_CHALLENGE)

__all__ = [
    "join_team",
    # lab_sqd
    "grade_lab_sqd_ex1",
    "grade_lab_sqd_ex2",
    "grade_lab_sqd_ex3",
    "grade_lab_sqd_ex4",
    "grade_lab_sqd_ex5",
    "grade_lab_sqd_ex6",
    # lab_qmoo
    "grade_lab_qmoo_ex1",
    "grade_lab_qmoo_ex2",
    "grade_lab_qmoo_ex3",
    "grade_lab_qmoo_ex4",
    # lab_hadron
    "grade_lab_hadron_ex1",
    "grade_lab_hadron_ex2",
    "grade_lab_hadron_ex3",
    "grade_lab_hadron_ex4",
    "grade_lab_hadron_ex5",
    "grade_lab_hadron_ex6",
    "grade_lab_hadron_ex7",
    "grade_lab_hadron_ex8",
    "grade_lab_hadron_ex9",
    "grade_lab_hadron_ex10",
    "grade_lab_hadron_ex11",
]
