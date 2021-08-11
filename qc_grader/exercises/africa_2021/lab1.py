from typing import List, Union

from qiskit_optimization import QuadraticProgram

from qc_grader.grade import grade_json, submit_json


criteria: dict = {}


def grade_ex1a(module_names: List[str]) -> None:
    ok, _ = grade_json(module_names, 'ex1', 'partA', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex1b(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    ok, _ = grade_json(answer, 'ex1', 'partB', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def grade_ex1c(tonnage_qaoa: Union[int, float], tonnage_vqe: Union[int, float]) -> None:
    answer = {
        'tonnage_qaoa': tonnage_qaoa,
        'tonnage_vqe': tonnage_vqe
    }
    ok, _ = grade_json(answer, 'ex1', 'partC', **criteria)
    if ok:
        print('Feel free to submit your answer.\r\n')


def submit_ex1a(module_names: List[str]) -> None:
    submit_json(module_names, 'ex1', 'partA', **criteria)


def submit_ex1b(quadratic_program: QuadraticProgram) -> None:
    answer = {
        'qp': quadratic_program.export_as_lp_string()
    }
    submit_json(answer, 'ex1', 'partB', **criteria)


def submit_ex1c(tonnage_qaoa: Union[int, float], tonnage_vqe: Union[int, float]) -> None:
    answer = {
        'tonnage_qaoa': tonnage_qaoa,
        'tonnage_vqe': tonnage_vqe
    }
    submit_json(answer, 'ex1', 'partC', **criteria)
