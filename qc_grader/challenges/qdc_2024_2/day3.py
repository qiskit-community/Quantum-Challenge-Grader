from typing import Callable, Tuple, List, Union, Optional
from qiskit import QuantumCircuit
import numpy as np
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime.debug_tools import Neat
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorOptions
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit.quantum_info import SparsePauliOp
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime.options import NoiseLearnerOptions
from qiskit_ibm_runtime import RuntimeJob, RuntimeJobV2
from qiskit_ibm_runtime.noise_learner import NoiseLearner
from qiskit.primitives import PrimitiveResult
from qiskit_ibm_runtime import IBMBackend
from qc_grader.grader.grade import grade
from typeguard import typechecked
import qiskit_ibm_runtime


_challenge_id = 'qdc_2024'


def circuit_ex1(paramsx,repetitions):
    qc = QuantumCircuit(14)
    for j in range(repetitions):
        # 1st "layer"
        for i in range(14):
            qc.rx(paramsx[i,0],i)
        qc.barrier()
        qc.cz(range(3),range(1,4))
        qc.cz(2,4)
        qc.cz(4,5)
        qc.cz(5,6)
        qc.cz(5,7)
        qc.cz(7,8)
        qc.cz(8,9)
        qc.cz(9,10)
        qc.cz(8,11)
        qc.cz(11,12)
        qc.cz(12,13)
        qc.barrier()
        # 2nd "layer"
        for i in range(14):
            qc.rx(paramsx[i,1],i)
        qc.barrier()
        qc.cz(0,1)
        qc.cz(1,3)
        qc.cz(3,2)
        qc.cz(3,4)
        qc.cz(4,6)
        qc.cz(6,5)
        qc.cz(6,7)
        qc.cz(7,8)
        qc.cz(8,10)
        qc.cz(10,9)
        qc.cz(8,11)
        qc.cz(11,12)
        qc.cz(12,13)
        qc.barrier()

    return qc


def circuit_ex3(params):
    qc = QuantumCircuit(8)
    qc.h(range(8))
    for j in range(2):
        qc.cz(range(0,4,2),range(1,5,2))
        qc.cz(range(1,4,2),range(2,5,2))
        qc.cz(range(4,8-1),range(5,8))
        for i in range(8):
            qc.rx(params[i,j],i)
    return qc


def get_noisy_vals(repetitions):
    paramsx = np.zeros((14,2))
    qc = circuit_ex1(paramsx,repetitions)
    service = QiskitRuntimeService(channel='ibm_quantum')
    backend = service.backend('ibm_nazca') # CHOOSE THE RIGHT BACKEND
    pm = generate_preset_pass_manager(backend=backend, optimization_level=0, seed_transpiler=1)

    # Transpiling the circuit for the correct backend and adapt the observables
    optimized_circuit = pm.run(qc)
    layout = optimized_circuit.layout
    observables = []
    observables.append(SparsePauliOp("Z" * (14)))
    optimized_observables = [obs.apply_layout(layout=layout) for obs in observables]

    pubs=[(optimized_circuit,optimized_observables)]
    # optimized_circuit.draw(idle_wires=0)

    # We need to turn the circuit into a clifford circuit before using NEAT
    noise_model = None  # option to specify a custom `NoiseModel`

    # Initialize a neat object
    analyzer = Neat(backend, noise_model)
    clifford_pubs = analyzer.to_clifford(pubs)

    # We first want to calculate the ideal value, which should be 1
    ideal_vals = analyzer.ideal_sim(clifford_pubs, seed_simulator=10)

    # Now we calculate the noisy value to compare it
    noisy_vals  = analyzer.noisy_sim(clifford_pubs, seed_simulator=10)
    noisy_vals = noisy_vals[0].vals[0]
    return noisy_vals


@typechecked
def grade_day3a_ex1(repetitions: int):

    answer = [get_noisy_vals(repetitions), get_noisy_vals(repetitions+1)]
    print(answer)
    grade(
        answer,
        "day3a-ex1",
        _challenge_id,
    )


@typechecked
def grade_day3a_ex2(num_unique_layers: int):

    answer = num_unique_layers

    grade(
        answer,
        "day3a-ex2",
        _challenge_id,
    )


@typechecked
def grade_day3a_ex3(qc: QuantumCircuit):

    np.random.seed(10)
    params = np.random.uniform(0,np.pi/2,size=(8,2))
    original_circuit = circuit_ex3(params)
    answer = qc
    
    if Statevector(qc) != Statevector(original_circuit):
        return "The circuits are not equivalent. Try again."


    grade(
        answer,
        "day3a-ex3",
        _challenge_id,
    )


@typechecked
def grade_day3a_ex4(learner_options: NoiseLearnerOptions, chosen_circuit: int):

    max_layers = learner_options.max_layers_to_learn
    strategy = learner_options.twirling_strategy
    answer = (max_layers, strategy, chosen_circuit)

    grade(
        answer,
        "day3a-ex4",
        _challenge_id,
    )


@typechecked
def submit_day3a_ex5(ex5_func: Callable, backend: Optional[IBMBackend] = None):

    if backend is None:
         backend = QiskitRuntimeService(channel='ibm_quantum').backend('test_eagle_us-east')

    np.random.seed(10)
    paramsx = np.random.uniform(0,np.pi/2,(14,2))
    optimized_circuit, transpiled_circuit = ex5_func(paramsx)

    original_circuit = circuit_ex1(paramsx,1)

    depth_threshold = 20 # after CZ manipulation and opt_level=3 you get around 20 layers (usually in the range [15,25])

    if Statevector(optimized_circuit) != Statevector(original_circuit):
        return "The circuits are not equivalent. Try again."

    if transpiled_circuit.depth(lambda x: len(x.qubits) == 2) > depth_threshold:
        return "The circuits is still too deep. Try again."
    
    pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
    transpiled_circuit = pm.run(transpiled_circuit)

    options = NoiseLearnerOptions()
    options.layer_pair_depths = (0,1)
    options.num_randomizations = 1
    options.shots_per_randomization = 1
    options.max_layers_to_learn = 100

    learner = NoiseLearner(backend, options)

    job = learner.run([transpiled_circuit])

    return job


@typechecked
def grade_day3a_ex5(job: Union[RuntimeJob, RuntimeJobV2]):

    if job.status() != "DONE":
        return "The job is not done."
    answer=[str(job.result()[i]) for i in range(len(job.result()))]
    grade(
        answer,
        "day3a-ex5",
        _challenge_id,
    )


@typechecked
def submit_day3b_ex1(options: EstimatorOptions, pub: Tuple[QuantumCircuit, List[List[SparsePauliOp]],np.ndarray],backend: Optional[IBMBackend] = None):

    if backend == None:
        backend = QiskitRuntimeService(channel='ibm_quantum').backend('ibm_cusco')

    if type(options.twirling.num_randomizations) != qiskit_ibm_runtime.options.utils.UnsetType:
        if options.twirling.num_randomizations > 100:
            return "You are using too many randomization for the Pauli twirling. Set a lower number."
    estimator = Estimator(backend,options=options)
    
    job = estimator.run([pub])

    return job

@typechecked
def grade_day3b_ex1(job: Union[RuntimeJob, RuntimeJobV2]):

    if job.status() != 'DONE':
        return "The job is not done."

    result = job.result()
    expvals = result[0].data.evs
    answer = np.mean(np.abs(1-expvals))
    status, score, message = grade(
        answer,
        "day3b-ex1",
        _challenge_id,
        return_response=True
    )

    if status:
        print(f'Your score is {score/(2**30)}')
    else:
        print(f'Oops 😕! {"Your answer is incorrect" if message is None else message}')

@typechecked
def submit_feedback_3a_1(feedback: str) -> None:
    grade(feedback, 'feedback-3a-1', _challenge_id)


@typechecked
def submit_feedback_3a_2(feedback: str) -> None:
    grade(feedback, 'feedback-3a-2', _challenge_id)


@typechecked
def submit_feedback_3a_3(feedback: str) -> None:
    grade(feedback, 'feedback-3a-3', _challenge_id)
    

@typechecked
def submit_feedback_3b_1(feedback: str) -> None:
    grade(feedback, 'feedback-3b-1', _challenge_id)


@typechecked
def submit_feedback_3b_2(feedback: str) -> None:
    grade(feedback, 'feedback-3b-2', _challenge_id)


@typechecked
def submit_feedback_3b_3(feedback: str) -> None:
    grade(feedback, 'feedback-3b-3', _challenge_id)
