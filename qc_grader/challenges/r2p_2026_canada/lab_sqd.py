# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from qc_grader.challenges.common.r2p_2026.lab_sqd import (
    _create_grade_function,
    _create_submit_name_function,
    _create_grade_lab_sqd_ex1,
    _create_grade_lab_sqd_ex2,
    _create_grade_lab_sqd_ex3,
    _create_grade_lab_sqd_ex4,
    _create_grade_lab_sqd_ex5,
    _create_grade_lab_sqd_ex6,
)

_CHALLENGE = "r2p_2026_canada"

_grade = _create_grade_function(_CHALLENGE)
submit_name = _create_submit_name_function(_CHALLENGE)
grade_lab_sqd_ex1 = _create_grade_lab_sqd_ex1(_grade)
grade_lab_sqd_ex2 = _create_grade_lab_sqd_ex2(_grade)
grade_lab_sqd_ex3 = _create_grade_lab_sqd_ex3(_grade)
grade_lab_sqd_ex4 = _create_grade_lab_sqd_ex4(_grade)
grade_lab_sqd_ex5 = _create_grade_lab_sqd_ex5(_grade)
grade_lab_sqd_ex6 = _create_grade_lab_sqd_ex6(_grade)
