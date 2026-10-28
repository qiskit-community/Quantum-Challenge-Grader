# (C) Copyright IBM 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
IBM Quantum Developer Conference 2026 (qdc_2026) - Grading Functions

Team challenge: run ``join_team("<your team name>")`` once before grading.
"""

from qc_grader.grader.grade import (
    create_check_progress_function,
    create_join_team_function,
)

# from .lab_floquet import (
#     grade_lab_floquet_ex1_1,
#     grade_lab_floquet_ex1_2,
#     grade_lab_floquet_ex2_1,
#     grade_lab_floquet_ex2_2,
#     grade_lab_floquet_ex3_1,
#     grade_lab_floquet_ex3_2a,
#     grade_lab_floquet_ex3_2b,
#     grade_lab_floquet_ex3_3a,
#     grade_lab_floquet_ex3_3b,
#     grade_lab_floquet_ex4_1,
#     grade_lab_floquet_ex4_2,
#     grade_lab_floquet_ex4_3a,
#     grade_lab_floquet_ex4_3b,
#     grade_lab_floquet_ex4_3c,
#     grade_lab_floquet_ex4_3d,
#     grade_lab_floquet_ex4_3e,
#     grade_lab_floquet_ex5_1,
#     grade_lab_floquet_ex5_2,
# )
from .lab_iceberg import (
    grade_lab_iceberg_ex1_2,
    grade_lab_iceberg_ex1_3,
    grade_lab_iceberg_ex1_4,
    grade_lab_iceberg_ex1_5a,
    grade_lab_iceberg_ex1_5b,
    grade_lab_iceberg_ex1_6,
    grade_lab_iceberg_ex1_7,
    grade_lab_iceberg_ex1_8,
    grade_lab_iceberg_ex1_9,
    grade_lab_iceberg_ex2_1,
    grade_lab_iceberg_ex2_2,
    grade_lab_iceberg_ex2_3,
    grade_lab_iceberg_ex2_4,
    grade_lab_iceberg_ex2_5,
    grade_lab_iceberg_ex2_6,
    grade_lab_iceberg_ex2_7,
    grade_lab_iceberg_ex3_1,
    grade_lab_iceberg_ex3_2,
    grade_lab_iceberg_ex3_3,
    grade_lab_iceberg_ex3_4,
    grade_lab_iceberg_ex3_5,
    grade_lab_iceberg_ex4_1,
    grade_lab_iceberg_ex4_2,
    grade_lab_iceberg_ex5_1,
    grade_lab_iceberg_ex5_2,
)

from .lab_ole import (
    grade_lab_ole_ex1,
    grade_lab_ole_ex2,
    grade_lab_ole_ex3,
    grade_lab_ole_ex4,
    grade_lab_ole_questions,
)

# from .lab_proteasome import (
#     grade_lab_proteasome_ex1,
#     grade_lab_proteasome_ex2,
#     grade_lab_proteasome_ex3,
#     grade_lab_proteasome_ex4,
#     grade_lab_proteasome_ex5,
#     grade_lab_proteasome_ex6,
#     grade_lab_proteasome_ex7,
#     grade_lab_proteasome_ex8,
#     grade_lab_proteasome_ex9,
#     grade_lab_proteasome_ex10,
#     grade_lab_proteasome_ex11,
#     grade_lab_proteasome_ex12,
# )
# from .lab_qamoo import (
#     grade_lab_qamoo_ex1_1a,
#     grade_lab_qamoo_ex1_1b,
#     grade_lab_qamoo_ex1_1c,
#     grade_lab_qamoo_ex1_1d,
#     grade_lab_qamoo_ex1_2a,
#     grade_lab_qamoo_ex1_2b,
#     grade_lab_qamoo_ex1_2c,
#     grade_lab_qamoo_ex2_1,
#     grade_lab_qamoo_ex2_2,
# )
from .lab_verifiability import (
    grade_lab_verifiability_ex1,
    grade_lab_verifiability_ex2,
    grade_lab_verifiability_ex3,
    grade_lab_verifiability_ex4,
    grade_lab_verifiability_ex5,
    grade_lab_verifiability_ex6,
    grade_lab_verifiability_ex7,
    grade_lab_verifiability_ex8,
    grade_lab_verifiability_ex9,
    grade_lab_verifiability_ex10,
)
from .lab_tcfs import (
    grade_lab_tcfs_ex1a,
    grade_lab_tcfs_ex1b,
    grade_lab_tcfs_ex1c,
    grade_lab_tcfs_ex1d,
    grade_lab_tcfs_ex2a,
    grade_lab_tcfs_ex2b,
    grade_lab_tcfs_ex2c,
    grade_lab_tcfs_ex2d,
    grade_lab_tcfs_ex2e,
    grade_lab_tcfs_ex3d,
    grade_lab_tcfs_ex3l,
    grade_lab_tcfs_ex3t,
)

_CHALLENGE = "qdc_2026"
join_team = create_join_team_function(_CHALLENGE)
check_progress = create_check_progress_function(_CHALLENGE)


__all__ = [
    "join_team",
    "check_progress",
    # # lab_floquet
    # "grade_lab_floquet_ex1_1",
    # "grade_lab_floquet_ex1_2",
    # "grade_lab_floquet_ex2_1",
    # "grade_lab_floquet_ex2_2",
    # "grade_lab_floquet_ex3_1",
    # "grade_lab_floquet_ex3_2a",
    # "grade_lab_floquet_ex3_2b",
    # "grade_lab_floquet_ex3_3a",
    # "grade_lab_floquet_ex3_3b",
    # "grade_lab_floquet_ex4_1",
    # "grade_lab_floquet_ex4_2",
    # "grade_lab_floquet_ex4_3a",
    # "grade_lab_floquet_ex4_3b",
    # "grade_lab_floquet_ex4_3c",
    # "grade_lab_floquet_ex4_3d",
    # "grade_lab_floquet_ex4_3e",
    # "grade_lab_floquet_ex5_1",
    # "grade_lab_floquet_ex5_2",
    # # lab_verifiability
    "grade_lab_verifiability_ex1",
    "grade_lab_verifiability_ex2",
    "grade_lab_verifiability_ex3",
    "grade_lab_verifiability_ex4",
    "grade_lab_verifiability_ex5",
    "grade_lab_verifiability_ex6",
    "grade_lab_verifiability_ex7",
    "grade_lab_verifiability_ex8",
    "grade_lab_verifiability_ex9",
    "grade_lab_verifiability_ex10",
    # # lab_iceberg
    "grade_lab_iceberg_ex1_2",
    "grade_lab_iceberg_ex1_3",
    "grade_lab_iceberg_ex1_4",
    "grade_lab_iceberg_ex1_5a",
    "grade_lab_iceberg_ex1_5b",
    "grade_lab_iceberg_ex1_6",
    "grade_lab_iceberg_ex1_7",
    "grade_lab_iceberg_ex1_8",
    "grade_lab_iceberg_ex1_9",
    "grade_lab_iceberg_ex2_1",
    "grade_lab_iceberg_ex2_2",
    "grade_lab_iceberg_ex2_3",
    "grade_lab_iceberg_ex2_4",
    "grade_lab_iceberg_ex2_5",
    "grade_lab_iceberg_ex2_6",
    "grade_lab_iceberg_ex2_7",
    "grade_lab_iceberg_ex3_1",
    "grade_lab_iceberg_ex3_2",
    "grade_lab_iceberg_ex3_3",
    "grade_lab_iceberg_ex3_4",
    "grade_lab_iceberg_ex3_5",
    "grade_lab_iceberg_ex4_1",
    "grade_lab_iceberg_ex4_2",
    "grade_lab_iceberg_ex5_1",
    "grade_lab_iceberg_ex5_2",
    # # lab_proteasome
    # "grade_lab_proteasome_ex1",
    # "grade_lab_proteasome_ex2",
    # "grade_lab_proteasome_ex3",
    # "grade_lab_proteasome_ex4",
    # "grade_lab_proteasome_ex5",
    # "grade_lab_proteasome_ex6",
    # "grade_lab_proteasome_ex7",
    # "grade_lab_proteasome_ex8",
    # "grade_lab_proteasome_ex9",
    # "grade_lab_proteasome_ex10",
    # "grade_lab_proteasome_ex11",
    # "grade_lab_proteasome_ex12",
    # # lab_ole
    "grade_lab_ole_ex1",
    "grade_lab_ole_ex2",
    "grade_lab_ole_ex3",
    "grade_lab_ole_ex4",
    "grade_lab_ole_questions",
    # # lab_qamoo
    # "grade_lab_qamoo_ex1_1a",
    # "grade_lab_qamoo_ex1_1b",
    # "grade_lab_qamoo_ex1_1c",
    # "grade_lab_qamoo_ex1_1d",
    # "grade_lab_qamoo_ex1_2a",
    # "grade_lab_qamoo_ex1_2b",
    # "grade_lab_qamoo_ex1_2c",
    # "grade_lab_qamoo_ex2_1",
    # "grade_lab_qamoo_ex2_2",
    # # lab_foruier_lcu_qaoa
    "grade_lab_tcfs_ex1a",
    "grade_lab_tcfs_ex1b",
    "grade_lab_tcfs_ex1c",
    "grade_lab_tcfs_ex1d",
    "grade_lab_tcfs_ex2a",
    "grade_lab_tcfs_ex2b",
    "grade_lab_tcfs_ex2c",
    "grade_lab_tcfs_ex2d",
    "grade_lab_tcfs_ex2e",
    "grade_lab_tcfs_ex3d",
    "grade_lab_tcfs_ex3l",
    "grade_lab_tcfs_ex3t",
]
