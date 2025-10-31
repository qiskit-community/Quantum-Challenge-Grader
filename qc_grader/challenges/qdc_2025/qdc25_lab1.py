from typeguard import typechecked

from qiskit import QuantumCircuit
from qc_grader.grader.grade import grade
from qiskit_ibm_runtime.ibm_backend import IBMBackend
import numpy
from typing import Protocol, runtime_checkable, List, Tuple, Dict, Any
from typeguard import check_type

@runtime_checkable
class HeavyHexLike(Protocol):
    plaquettes_width: int
    plaquettes_height: int
    coords: List[Tuple[float, float]]
    edges: Dict[Tuple[float, float], Any]
    vertices: Dict[Tuple[int, int], Any]

    def coords_to_logical_qb(self, coords: Any) -> Any: ...
    def edges_connected_to_node(self, node_coords: Tuple[int, int]) -> List[Tuple[float, float]]: ...
    def nodes_connected_to_edge(self, edge_coords: Tuple[float, float]) -> Tuple[Tuple[int, int], Tuple[int, int]]: ...
    def find_qubits_downward(self) -> List[int]: ...
    def find_qubits_upward(self) -> List[int]: ...

_challenge_id = "qdc_2025"


@typechecked
def submit_name(name: str) -> None:
    status, score, message = grade(
        name, "submit-name", _challenge_id, return_response=True
    )
    if status == False:
        print(message)
    else:
        print("Team name submitted.")


@typechecked
def grade_lab1_ex1(qc: QuantumCircuit) -> None:
    grade(qc, "lab1-ex1", _challenge_id)


def grade_lab1_ex2(qc: QuantumCircuit, lattice: HeavyHexLike) -> None:
    check_type(qc, QuantumCircuit)
    check_type(lattice, HeavyHexLike)
    plaq_width = lattice.plaquettes_width
    plaq_height = lattice.plaquettes_height
    answer_dict = {"plaq_width": plaq_width, "plaq_height": plaq_height, "qc": qc}
    grade(answer_dict, "lab1-ex2", _challenge_id)


def grade_lab1_ex3(qc: QuantumCircuit, lattice: HeavyHexLike) -> None:
    check_type(qc, QuantumCircuit)
    check_type(lattice, HeavyHexLike)
    plaq_width = lattice.plaquettes_width
    plaq_height = lattice.plaquettes_height
    answer_dict = {"plaq_width": plaq_width, "plaq_height": plaq_height, "qc": qc}
    grade(answer_dict, "lab1-ex3", _challenge_id)


def grade_lab1_ex4(
    isa_circuits: QuantumCircuit, lattice: HeavyHexLike, dt: float, backend: IBMBackend
) -> None:
    check_type(isa_circuits, QuantumCircuit)
    check_type(lattice, HeavyHexLike)
    check_type(dt, float)
    check_type(backend, IBMBackend)

    plaq_width = lattice.plaquettes_width
    plaq_height = lattice.plaquettes_height

    answer_dict = {
        "isa_circuits": isa_circuits,
        "plaq_width": plaq_width,
        "plaq_height": plaq_height,
        "dt": dt,
    }
    grade(answer_dict, "lab1-ex4", _challenge_id)


@typechecked
def grade_lab1_ex5(
    best_expectation_vals: numpy.ndarray,
    qubit: int,
    dt: float,
    classical_exp_vals: numpy.ndarray,
) -> None:
    answer_dict = {
        "best_expectation_vals": best_expectation_vals,
        "qubit": qubit,
        "dt": dt,
        "classical_exp_vals": classical_exp_vals,
    }
    grade(answer_dict, "lab1-ex5", _challenge_id)

