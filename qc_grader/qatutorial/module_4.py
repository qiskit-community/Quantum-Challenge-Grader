from typeguard import typechecked

from qc_grader.grader.grade import grade


_id = 'qml_tutorials'


@typechecked
def grade_module_4_ex1() -> None:
    grade('', 'module-4', _id)
