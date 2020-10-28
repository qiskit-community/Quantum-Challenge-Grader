from qiskit.providers.ibmq.job import IBMQJob

from qc_grader.grade import grade, submit


def grade_ex2a(job: IBMQJob) -> None:
    grade(job, 'week2', 'exA')


def submit_ex2a(job: IBMQJob) -> None:
    submit(job, 'week2', 'exA')


def grade_ex2b(job: IBMQJob) -> None:
    grade(job, 'week2', 'exB')


def submit_ex2b(job: IBMQJob) -> None:
    submit(job, 'week2', 'exB')
