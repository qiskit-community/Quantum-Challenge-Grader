
from typing import Optional
from ..api import get_challenge_question_set


class SubmissionError(BaseException):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def get_question_id(lab_id: str, ex_id: Optional[str] = None) -> int:
    try:
        question_name = f'{lab_id}/{ex_id}' if ex_id is not None else lab_id
        question_set = get_challenge_question_set()

        if isinstance(question_set[0], dict):
            questions = list(filter(lambda q: question_name in q['name'], question_set))
            return questions[0]['id']
        else:
            return question_set.index(question_name) + 1
    except Exception:
        return -1
