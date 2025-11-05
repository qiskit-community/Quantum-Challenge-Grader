from typeguard import typechecked, check_type

from qiskit_serverless.core import QiskitFunction
from qc_grader.grader.grade import grade

_challenge_id = "qdc_2025"

@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status == False:
        print(message)
    else:
        print("Team name submitted.")

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
grade_kipu_function = make_validator("kipu-quantum")
