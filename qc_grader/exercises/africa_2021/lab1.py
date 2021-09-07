from typing import List, Union

from qiskit_optimization import QuadraticProgram

from qc_grader.grade import grade_and_submit


def grade_ex1a(module_names: List[str]) -> None:
    grade_and_submit(module_names, 'ex1', 'partA')


def grade_ex1b(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    grade_and_submit(answer, 'ex1', 'partB')


def grade_ex1c(tonnage_qaoa: Union[int, float], tonnage_vqe: Union[int, float]) -> None:
    answer = {
        'tonnage_qaoa': tonnage_qaoa,
        'tonnage_vqe': tonnage_vqe
    }
    grade_and_submit(answer, 'ex1', 'partC')


def grade_ex1d(job_id: str) -> None:
    grade_and_submit(job_id, 'ex1', 'partD', is_job_id=True)
