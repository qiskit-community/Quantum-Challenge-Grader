from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_swaptest_ex1() -> None:
    grade('', 'swaptest-1', _id)
