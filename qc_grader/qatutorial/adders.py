from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_adders_ex1() -> None:
    grade('', 'adders-1', _id)
