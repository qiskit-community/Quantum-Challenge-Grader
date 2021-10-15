import jsonpickle
import numpy.typing as npt

from typeguard import typechecked

from qiskit_optimization import QuadraticProgram

from qc_grader.grade import grade_and_submit


@typechecked
def grade_ex1a(qp: QuadraticProgram) -> None:
    answer = jsonpickle.encode(qp.export_as_lp_string())
    grade_and_submit(answer, '1a')


@typechecked
def grade_ex1b(numpy_results: npt.ArrayLike) -> None:
    answer = jsonpickle.encode(numpy_results)
    grade_and_submit(answer, '1b')


@typechecked
def grade_ex1c(numpy_results: npt.ArrayLike) -> None:
    answer = jsonpickle.encode(numpy_results)
    grade_and_submit(answer, '1c')
