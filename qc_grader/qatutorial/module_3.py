from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qml_tutorials'


@typechecked
def grade_module_3_ex1() -> None:
    grade('', 'module-3', _id)
