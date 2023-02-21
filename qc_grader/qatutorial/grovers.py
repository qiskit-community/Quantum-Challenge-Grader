from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_grovers_ex1() -> None:
    grade('', 'grover-1', _id)
