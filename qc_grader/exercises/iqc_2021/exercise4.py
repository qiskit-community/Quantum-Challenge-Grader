from qc_grader.grade import grade_json, submit_json


def format_submission(
    f12: float,
    qubit_index: int,
    backend_name: str
) -> dict:
    return {
        'f12': f12,
        'qubit_index': qubit_index,
        'backend_name': backend_name
    }


def grade_ex4(
    f12: float,
    qubit_index: int,
    backend_name: str
) -> None:
    try:
        submission = format_submission(f12, qubit_index, backend_name)
        ok, _ = grade_json(submission, 'ex4')
        if ok:
            print('Feel free to submit your answer.\r\n')
    except Exception as err:
        print(err)


def submit_ex4(
    f12: float,
    qubit_index: int,
    backend_name: str
) -> None:
    try:
        submission = format_submission(f12, qubit_index, backend_name)
        submit_json(submission, 'ex4')
    except Exception as err:
        print(err)
