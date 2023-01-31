from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_hadamardtest_ex1() -> None:
    grade('', 'hadamardtest-1', _id)
