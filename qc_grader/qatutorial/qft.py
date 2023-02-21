from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_qft_ex1() -> None:
    grade('', 'qft-1', _id)
