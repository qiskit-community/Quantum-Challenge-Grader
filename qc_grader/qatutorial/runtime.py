from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qa_tutorials'


@typechecked
def grade_runtime_ex1() -> None:
    grade('', 'runtime-1', _id)
