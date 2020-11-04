
EXERCISES = [
    'week1/exA', 'week1/exB',
    'week2/exA', 'week2/exB',
    'week3/exA',
]


def get_question_id(lab_id: str, ex_id: str) -> int:
    try:
        return EXERCISES.index(f'{lab_id}/{ex_id}') + 1
    except Exception:
        return -1
