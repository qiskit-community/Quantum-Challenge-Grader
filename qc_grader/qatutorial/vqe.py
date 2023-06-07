from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_vqe_ex1() -> None:
    grade('', 'vqe-1', _id)
