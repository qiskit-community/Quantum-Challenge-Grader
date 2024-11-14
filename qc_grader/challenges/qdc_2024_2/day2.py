from collections import OrderedDict
from typeguard import typechecked

from typing import *
from colorama import Fore, Style
import numpy as np
from networkx import barabasi_albert_graph

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.transpiler import StagedPassManager
from qiskit.quantum_info import hellinger_distance, hellinger_fidelity, SparsePauliOp
from qiskit.circuit.library import QAOAAnsatz
from qiskit_aer import AerSimulator
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit_ibm_runtime.ibm_backend import IBMBackend
from qiskit_ibm_runtime.fake_provider import FakeTorino
from qiskit_ibm_transpiler import TranspilerService
from qiskit.circuit import ParameterVector
from .utils import build_max_cut_paulis

from qc_grader.grader.grade import grade

_challenge_id = 'qdc_2024'

DEBUG = False

backend = FakeTorino()

# define the original circuit for day 2a
num_qubits = 50
graph = barabasi_albert_graph(n=num_qubits, m=7, seed=42)
local_correlators = build_max_cut_paulis(graph)
cost_operator = SparsePauliOp.from_list(local_correlators)

dummy_initial_state = QuantumCircuit(num_qubits)
dummy_mixer_operator = QuantumCircuit(num_qubits)

cost_layer = QAOAAnsatz(
    cost_operator,
    reps=1,
    initial_state=dummy_initial_state,
    mixer_operator=dummy_mixer_operator,
    name="QAOA cost block",
)

# define the original circuit for day 2b
# Initial state = equal superposition
initial_state = QuantumCircuit(num_qubits)
initial_state.h(range(num_qubits))

qaoa_layers = 3

# Mixer operator = rx rotations
betas = ParameterVector("β", qaoa_layers)
mixer_operator = QuantumCircuit(num_qubits)
mixer_operator.rx(-2*betas[0], range(num_qubits))

# Use off-the-shelf qiskit QAOAAnsatz
qaoa_ansatz = QAOAAnsatz(
    cost_operator,
    initial_state=initial_state,
    mixer_operator=mixer_operator,
    reps=qaoa_layers,
)

def grade_day2a_ex1(pm: StagedPassManager, backend: IBMBackend):
    grade_pm(pm, backend, 'day2a-ex1', pass_score=800, circuit=cost_layer)

def grade_day2a_ex2(pm: StagedPassManager, backend: IBMBackend):
    grade_pm(pm, backend, 'day2a-ex2', pass_score=750, circuit=cost_layer)

def grade_day2a_ex3(pm: StagedPassManager, backend: IBMBackend):
    grade_pm(pm, backend, 'day2a-ex3', pass_score=700, circuit=cost_layer)

def grade_day2a_ex4(pm: TranspilerService, backend: IBMBackend):
    grade_pm(pm, backend, 'day2a-ex4', pass_score=700, circuit=cost_layer)

def grade_day2a_ex5(pm: StagedPassManager, backend: IBMBackend):
    grade_pm(pm, backend, 'day2a-ex5', pass_score=400, circuit=cost_layer)

def grade_day2b_ex1(pm: StagedPassManager, backend: IBMBackend):
    grade_pm(pm, backend, 'day2b-ex1', pass_score=170, circuit=qaoa_ansatz)

def grade_transpiled_circuit(transpiled_circuit: QuantumCircuit, backend: IBMBackend):

    # 1. check operations contain only basis gates
    if not operation_check(transpiled_circuit, backend):
        return 10000

    # 2. check the transpiled circuit maps to the target
    if not connection_check(transpiled_circuit, backend):
        print(Fore.RED + 'The connections does not match with the backend')
        return 10000

    if DEBUG:
        print(f'Total gate count: {transpiled_circuit.count_ops()}')
        print(f'1Q gate count: {transpiled_circuit.size(lambda x: x.operation.num_qubits==1)}')
        print(f'2Q gate count: {transpiled_circuit.size(lambda x: x.operation.num_qubits==2)}')
        print(f'Total depth: {transpiled_circuit.depth()}')
        print(f'1Q depth: {transpiled_circuit.depth(lambda x: x.operation.num_qubits==1)}')
        print(f'2Q depth: {transpiled_circuit.depth(lambda x: x.operation.num_qubits==2)}')

    return score_func(transpiled_circuit)

def grade_pm(pm: Union[StagedPassManager, TranspilerService], backend: IBMBackend, ex_id: str, pass_score: int, circuit: QuantumCircuit):
    total_iterations = 5  # Define total iterations for the long process
    progress = [0]  # To keep track of progress, use a mutable object like a list
    stop_event = threading.Event()
    loader_thread = threading.Thread(target=loading_animation, args=(stop_event, progress, total_iterations))
    
    # Start the loading animation
    loader_thread.start()

    # run multiple times
    score_list = []
    for i in range(1,total_iterations+1):
        transpiled_circuit = pm.run(circuit)
        score = grade_transpiled_circuit(transpiled_circuit, backend)
        score_list.append(score)
        progress[0] = i

    # Signal the loading animation to stop
    stop_event.set()

    # Ensure the loading animation thread finishes
    loader_thread.join()

    grade(
        score_list,
        ex_id,
        _challenge_id,
    )


def score_func(circuit: QuantumCircuit):        
    score = circuit.depth(lambda x: x.operation.num_qubits==2) + \
            circuit.depth(lambda x: x.operation.num_qubits==1) // 10
    return score


def operation_check(
    circ: QuantumCircuit, 
    backend: IBMBackend
):
    """
    Takes a backend and a circuit and see whether the gates in the circuit are supported by the backend

    Parameters : 
        backend: Target backend
        circuit (QuantumCircuit): Circuit whose gates are to be checked with the gates in the target backend
    """

    if_pass = True

    op_names_backend : list[str] = backend.operation_names
    op_names_backend.append('barrier')
    op_names_circuit_dict : dict[str,int]  = circ.count_ops().items()
    #use set.
    for keys, _ in op_names_circuit_dict:
        if keys in op_names_backend:
            None
        else: 
            print(Fore.RED + f'The backend does not support {keys} gate')
            if_pass = False
    return if_pass


def connection_check(
    circ: QuantumCircuit, 
    backend: IBMBackend
):
    """"
    Takes in a Quantum Circuit and a Backend and checks whether the conections in the circuit matches 
    with the topology of the backend. 

    Parameters: 
        backend: Target backend in which the circuit must fit.
        circuit (QuantumCircuit): Circuit whose connections are to be matched with the backend

    Returns: Message: Whether the circuit fits in the topology of the backend. 
    """

    conn_backend = get_backend_connections(backend)
    conn_circ = get_circuit_connections(circ)

    gate_conn_set_backend : dict[str,set] = {}
    for keys,items in conn_backend.items():
        gate_conn_set_backend[keys] = set(items)

    gate_conn_set_circuit : dict[str,set] = {}
    for keys,items in conn_circ.items():
        gate_conn_set_circuit[keys] = set(items)

    check_connections : list[int] = []
    for keys, items in gate_conn_set_circuit.items():
        check_connections.append(int(gate_conn_set_circuit[keys].issubset(gate_conn_set_backend[keys])))

    if 0 in check_connections:
        return False
    else : 
        return True


def get_backend_connections(
    backend: IBMBackend
) -> dict[str, list]: 
    """
    Takes a backend and returns the connections.

    Parameters : 
        Inputs a backend

    Returns: 
        The connection of the gates as a dictionary,
        the keys as gates and values as connections
    """

    instruc: list = backend.instructions
    operations: list = backend.operations
    oper_key : list[str] = []

    for items in operations:
        if isinstance(items, Instruction) and items.num_clbits == 0 :
            oper_key.append(items.name)

    list_dict : dict[str, list] = {name : [] for name in oper_key}
    for gates in range(len(oper_key)):
        for i in range(len(instruc)):
            if instruc[i][0].name == oper_key[gates]:
                qubit_tuple = instruc[i][1]
                list_dict[oper_key[gates]].append(qubit_tuple)

    return list_dict


def get_circuit_connections(
    circ : QuantumCircuit
) -> dict[str,list]: 
    """
    Takes a Quantum Circuit and returns the connections.

    Parameters : 
        Inputs a QuantumCircuit

    Returns: 
        The connection of the gates as a dictionary,
        the keys as gates and values as connections
    """

    gates_used: list = []
    for keys, _ in circ.count_ops().items():
        gates_used.append(keys)
    list_dict : dict[str,list] = {name : [] for name in gates_used}
    for gates in gates_used: 
        for i in range(len(circ.data)):
            if circ.data[i].operation.name == gates:
                qubit_tuple = ()
                for j in range(len(circ.data[i].qubits)):
                    qubit_index = circ.data[i].qubits[j]._index
                    qubit_tuple = qubit_tuple + (qubit_index,)
                list_dict[gates].append(qubit_tuple)   
    return list_dict


import threading
import itertools
import time
import sys

# Loading animation function
def loading_animation(stop_event, progress, total_iterations):
    loading_symbols = itertools.cycle(['|', '/', '-', '\\'])
    while not stop_event.is_set():
        bar_length = 40  # Length of the progress bar
        completed_length = int(bar_length * progress[0] / total_iterations)
        bar = '█' * completed_length + '-' * (bar_length - completed_length)
        percentage = (progress[0] / total_iterations) * 100
        sys.stdout.write(f'\rGrading... Running iteration {progress[0]}: {next(loading_symbols)} [{bar}] {percentage:6.2f}% ({progress[0]}/{total_iterations})')
        sys.stdout.flush()
        time.sleep(0.1)  # Adjust the speed of the animation here
    # Final update when complete
    bar = '█' * bar_length
    sys.stdout.write(f'\rGrading complete! Running iteration {progress[0]}: [{bar}] 100.00% ({total_iterations}/{total_iterations})\n')


@typechecked
def submit_feedback_2a_1(feedback: str) -> None:
    grade(feedback, 'feedback-2a-1', _challenge_id)

@typechecked
def submit_feedback_2a_2(feedback: str) -> None:
    grade(feedback, 'feedback-2a-2', _challenge_id)

@typechecked
def submit_feedback_2b_1(feedback: str) -> None:
    grade(feedback, 'feedback-2b-1', _challenge_id)
