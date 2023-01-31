from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_LCU_ex1() -> None:
    grade('', 'lcu-1', _id)
