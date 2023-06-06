from qiskit_aer.noise import NoiseModel
from typeguard import typechecked

from qc_grader.grader.grade import grade

_challenge_id = "qgss_2023"


@typechecked
def grade_lab5_ex1(noise_model: NoiseModel) -> None:
    grade(noise_model, "ex5-1", _challenge_id, byte_string=True)


@typechecked
def grade_lab5_ex2(new_shots: int) -> None:
    grade(new_shots, "ex5-2", _challenge_id, byte_string=True)


@typechecked
def grade_lab5_ex3(noise_model: NoiseModel) -> None:
    grade(noise_model, "ex5-3", _challenge_id, byte_string=True)
