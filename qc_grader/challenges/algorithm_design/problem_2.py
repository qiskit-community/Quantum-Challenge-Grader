from typeguard import typechecked
from qiskit.circuit.library import TwoLocal
from qc_grader.grader.grade import grade


_challenge_id = 'algorithm_design'


@typechecked
def grade_problem_2a(reference_circuit: TwoLocal) -> None:
    grade(reference_circuit, 'problem_2a', _challenge_id)


@typechecked
def grade_problem_2b(reference_circuit: TwoLocal, variational_form: TwoLocal, ansatz) -> None:
    grade({
        'reference_circuit': reference_circuit,
        'variational_form': variational_form,
        'ansatz': ansatz
    }, 'problem_2b', _challenge_id)
