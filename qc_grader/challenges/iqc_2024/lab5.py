from typeguard import typechecked

from typing import Callable

from qiskit import QuantumCircuit

from qc_grader.grader.grade import grade, get_problem_set

_challenge_id = 'iqc_2024'

@typechecked
def grade_lab5_ex1(circuit: QuantumCircuit) -> None:
    from qiskit_ibm_runtime import SamplerV2 as Sampler
    from qiskit_aer import AerSimulator

    backend = AerSimulator()
    sampler = Sampler(backend)
    job = sampler.run([circuit])
    counts = job.result()[0].data.c.get_counts()

    answer = {
     'counts': counts,
     'circuit': circuit
    }
    
    grade(answer, 'lab5-ex1', _challenge_id)

@typechecked
def grade_lab5_ex2(
   gates_cut: set,
   swap_depth: int,
   cut_depth: float
) -> None:
   answer = {
     'gates_cut': list(gates_cut),
     'swap_depth': swap_depth,
     'cut_depth': cut_depth
   }
   grade(answer, 'lab5-ex2', _challenge_id) 

@typechecked
def grade_lab5_ex3(circuit: QuantumCircuit) -> None:
    answer{
        'ops': circuit.count_ops(),
        'lay': circuit.layout.final_index_layout()
    }
    
    grade(answer, 'lab5-ex3', _challenge_id)

@typechecked
def grade_lab5_ex4(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab5-ex4', _challenge_id)

@typechecked
def grade_lab5_ex5(circuit: QuantumCircuit) -> None:
    grade(circuit, 'lab5-ex5', _challenge_id)
