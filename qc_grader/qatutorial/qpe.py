from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_qpe_ex1() -> None:
    grade('', 'qpe-1', _id)
