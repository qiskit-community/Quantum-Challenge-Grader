from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_operators_ex1() -> None:
    grade('', 'operators-1', _id)
