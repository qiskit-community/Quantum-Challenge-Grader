from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_officehours_ex1() -> None:
    grade('', 'officehours-1', _id)
