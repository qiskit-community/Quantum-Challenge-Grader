from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_bellstates_ex1() -> None:
    grade('', 'bell-1', _id)
