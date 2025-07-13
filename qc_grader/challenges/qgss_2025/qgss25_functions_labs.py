from typeguard import typechecked

from qiskit_serverless.core import QiskitFunction

from qc_grader.grader.grade import grade

_challenge_id = "qgss_2025"


def validate_function(
    function_provider: str,
    function_title: str,
) -> None:
    grade(function_title, function_provider, _challenge_id)


def make_validator(function_provider: str):
    @typechecked
    def validator(function: QiskitFunction) -> None:
        validate_function(
            function_provider=function_provider,
            function_title=function.title,
        )
    return validator


# Generate and assign the validators
grade_algorithmiq_function = make_validator("algorithmiq")
grade_colibritd_function = make_validator("colibritd")
grade_gdq_function = make_validator("global-data-quantum")
grade_kipu_function = make_validator("kipu-quantum")
grade_multiverse_function = make_validator("multiverse")
grade_qctrl_function = make_validator("q-ctrl")
grade_qedma_function = make_validator("qedma")
grade_qunova_function = make_validator("qunova")
