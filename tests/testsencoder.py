from qc_grader_json.custom_encoder import CustomJSONEncoder
import unittest
import qiskit
from qiskit.qobj import PulseQobj, PulseQobjConfig, PulseLibraryItem
from qiskit.qobj import PulseQobj, QasmQobj
from qiskit_aer.jobs import AerJob
from qiskit import Aer, QuantumCircuit, assemble, execute
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.opflow.primitive_ops.pauli_op import PauliOp, Pauli, SparsePauliOp
from qiskit.result import QuasiDistribution, ProbDistribution
from qiskit.primitives import SamplerResult, EstimatorResult
import qiskit_aer.noise as noise
from qiskit.algorithms.minimum_eigensolvers.vqe import VQEResult
from networkx.classes import Graph
import networkx as nx
import numpy as np



class TestEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = CustomJSONEncoder()


    def quantum_circuit_factory(self, num_qubits=2) -> object:
        qc = QuantumCircuit(num_qubits)
        qc.h(0)
        qc.cx(0, 1)
        return qc


    def test_qcircuit(self) -> None:
        '''Should be passed.'''

        qc = self.quantum_circuit_factory()

        expected_encoded_result = (
            '{"qc": {"qobj_id": "4a4d1fcb-07b6-4cbe-b310-b72ae7cacf4b", "header": {}, '
            '"config": {"shots": 1024, "memory": false, "parameter_binds": [], "meas_level": 2, '
            '"init_qubits": true, "parametric_pulses": [], "memory_slots": 0, "n_qubits": 2}, '
            '"schema_version": "1.3.0", "type": "QASM", "experiments": [{"config": {"n_qubits": 2, '
            '"memory_slots": 0}, "header": {"qubit_labels": [["q", 0], ["q", 1]], "n_qubits": 2, '
            '"qreg_sizes": [["q", 2]], "clbit_labels": [], "memory_slots": 0, "creg_sizes": [], '
            '"name": "circuit-171", "global_phase": 0.0, "metadata": {}}, "instructions": ['
            '{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}]}]}, "byte_string": false}'
        )

        encoded_qcircuit = self.encoder.default(qc)

        expected_encoded_result = self.remove_circuit_id(expected_encoded_result)
        encoded_qcircuit = self.remove_circuit_id(encoded_qcircuit)

        expected_encoded_result = self.remove_circuit_name(expected_encoded_result)
        encoded_qcircuit = self.remove_circuit_name(encoded_qcircuit)


        self.maxDiff = None
        self.assertEqual(encoded_qcircuit, expected_encoded_result, 'actual and expected outputs are not the same')

    
    def test_pulse_qobj(self) -> None:
        '''Should be passed.'''

        pulse_library_item = PulseLibraryItem(name="my_pulse", samples=[0.1, 0.2, 0.3])

        qobj_config = PulseQobjConfig(
            meas_level=2,
            meas_return=2,
            pulse_library=[pulse_library_item],
            qubit_lo_freq=[5.0],
            meas_lo_freq=[6.0],
            shots=1024
        )

        pulse_qobj = PulseQobj(qobj_id=None, experiments=[],config=qobj_config)
        
        actual_json = self.encoder.default(pulse_qobj)


        expected_json = (
            '{"qobj_id": "8004f656-f402-4a34-a048-b603dbca5e9d", "header": {}, '
            '"config": {"meas_level": 2, "meas_return": 2, "pulse_library": ['
            '{"name": "my_pulse", "samples": [0.1, 0.2, 0.3]}], "qubit_lo_freq": [5.0], '
            '"meas_lo_freq": [6.0], "shots": 1024}, "schema_version": "1.2.0", '
            '"type": "PULSE", "experiments": []}'
        )


        expected_json = self.remove_qobj_id(expected_json)
        actual_json = self.remove_qobj_id(actual_json)
        

        self.maxDiff = None
        self.assertEqual(actual_json, expected_json)

    
    def test_aer_job(self) -> None:
        '''Should be passed.'''

        self.maxDiff = None

        qc = self.quantum_circuit_factory()

        backend = Aer.get_backend('qasm_simulator')
        job = execute(qc, backend)
        
        expected_output = (
            '{"backend_name": "qasm_simulator", "backend_version": "0.13.1", '
            '"date": "2024-01-29T17:04:30.445944", "header": null, "qobj_id": "", '
            '"job_id": "051a1f5b-3afa-4281-85a7-768b5b90e96c", "status": "COMPLETED", '
            '"success": true, "results": [{"shots": 1024, "success": true, "data": {}, '
            '"meas_level": 2, "header": {"creg_sizes": [], "global_phase": 0.0, '
            '"memory_slots": 0, "n_qubits": 2, "name": "circuit-200", "qreg_sizes": [["q", 2]], '
            '"metadata": {}}, "status": "DONE", "seed_simulator": 563532904, "metadata": {'
            '"num_bind_params": 1, "runtime_parameter_bind": false, "parallel_state_update": 8, '
            '"parallel_shots": 1, "batched_shots_optimization": false, "remapped_qubits": false, '
            '"active_input_qubits": [], "device": "CPU", "time_taken": 3.4166e-05, '
            '"measure_sampling": false, "num_clbits": 0, "max_memory_mb": 16384, '
            '"input_qubit_map": [], "num_qubits": 0, "method": "stabilizer", '
            '"required_memory_mb": 0}, "time_taken": 3.4166e-05}], "metadata": {'
            '"time_taken_parameter_binding": 3.375e-06, "max_memory_mb": 16384, '
            '"time_taken_execute": 8.0875e-05, "omp_enabled": true, "max_gpu_memory_mb": 0, '
            '"parallel_experiments": 1}, "time_taken": 0.0010828971862792969}'
        )
        
        expected_output = self.clean_aer_json(expected_output)
        actual_output = self.encoder.default(job)
        actual_output = self.clean_aer_json(actual_output)

        self.assertEqual(actual_output, expected_output, 'actual and expected outputs are not the same')


    def test_pauli_sum_op(self) -> None:
        '''Should be passed.'''

        pauli_x = PauliOp(Pauli('X'))
        pauli_y = PauliOp(Pauli('Y'))
        pauli_sum_op = pauli_x + pauli_y

        actual_json = self.encoder.default(pauli_sum_op)
        
        expected_json = (
            '[["X", {"__class__": "complex", "re": 1.0, "im": 0.0}], '
            '["Y", {"__class__": "complex", "re": 1.0, "im": 0.0}]]'
        )

        self.assertEqual(actual_json, expected_json)


    def test_sparse_pauli_op(self) -> None:
        '''Should be passed.'''

        pauli_x = Pauli('X')
        pauli_z = Pauli('Z')

        coeffs = np.array([1.0, 1.0j])

        sparse_pauli_op = SparsePauliOp([pauli_x, pauli_z], coeffs=coeffs)

        expected_json = (
            '[["X", {"__class__": "complex", "re": 1.0, "im": 0.0}], '
            '["Z", {"__class__": "complex", "re": 0.0, "im": 1.0}]]'
        )

        actual_json = self.encoder.default(sparse_pauli_op)

        self.assertEqual(actual_json, expected_json)


    def test_quasidistribution(self) -> None:
        '''Should be passed.'''

        data = {'00': 0.5, '11': 0.5, '111': 0.7}
        quasi_dists = QuasiDistribution(data, shots=None, stddev_upper_bound=None)

        actual_json = self.encoder.default(quasi_dists)

        expected_json = (
            '{"data": "{0: 0.5, 3: 0.5, 7: 0.7}", '
            '"shots": null, "stddev_upper_bound": null}'
        )

        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')


    def test_probdistribution(self) -> None:
        '''Should be passed.'''

        data = {'00': 0.5, '1': 0.5, '1111': 0.9}
        prob_dist = ProbDistribution(data, shots=None)

        actual_json = self.encoder.default(prob_dist)

        expected_json = (
            '{"data": "{0: 0.5, 1: 0.5, 15: 0.9}", '
            '"shots": null}'
        )

        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')


    def test_noise_model(self) -> None:
        '''Should be passed.'''

        prob_1 = 0.003
        prob_2 = 0.09 

        error_1 = noise.depolarizing_error(prob_1, 1)
        error_2 = noise.depolarizing_error(prob_2, 2)

        noise_model = noise.NoiseModel()
        noise_model.add_all_qubit_quantum_error(error_1, ['rz', 'sx', 'x'])
        noise_model.add_all_qubit_quantum_error(error_2, ['cx'])

        actual_json = self.encoder.default(noise_model)

        actual_json = self.remove_noise_ids(actual_json)

        expected_json = (
            '{"errors": ['
            '{"type": "qerror", "id": "8bff0a66f4834414b1ffc69b895bd57f", "operations": ["rz"], '
            '"instructions": [[{"name": "id", "qubits": [0]}], [{"name": "x", "qubits": [0]}], '
            '[{"name": "y", "qubits": [0]}], [{"name": "z", "qubits": [0]}]], "probabilities": '
            '[0.99775, 0.00075, 0.00075, 0.00075]}, '
            '{"type": "qerror", "id": "8bff0a66f4834414b1ffc69b895bd57f", "operations": ["sx"], '
            '"instructions": [[{"name": "id", "qubits": [0]}], [{"name": "x", "qubits": [0]}], '
            '[{"name": "y", "qubits": [0]}], [{"name": "z", "qubits": [0]}]], "probabilities": '
            '[0.99775, 0.00075, 0.00075, 0.00075]}, '
            '{"type": "qerror", "id": "8bff0a66f4834414b1ffc69b895bd57f", "operations": ["x"], '
            '"instructions": [[{"name": "id", "qubits": [0]}], [{"name": "x", "qubits": [0]}], '
            '[{"name": "y", "qubits": [0]}], [{"name": "z", "qubits": [0]}]], "probabilities": '
            '[0.99775, 0.00075, 0.00075, 0.00075]}, '
            '{"type": "qerror", "id": "2d34f37511d143979f1ed58ceb23fbc1", "operations": ["cx"], '
            '"instructions": [[{"name": "pauli", "params": ["II"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["IX"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["IY"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["IZ"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["XI"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["XX"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["XY"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["XZ"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["YI"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["YX"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["YY"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["YZ"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["ZI"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["ZX"], "qubits": [0, 1]}], [{"name": "pauli", "params": ["ZY"], "qubits": [0, 1]}], '
            '[{"name": "pauli", "params": ["ZZ"], "qubits": [0, 1]}]], "probabilities": '
            '[0.9156250000000001, 0.005625000000000001, 0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
            '0.005625000000000001, 0.005625000000000001, 0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
            '0.005625000000000001, 0.005625000000000001, 0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
            '0.005625000000000001]}'
            ']}'
        )
        
        expected_json = self.remove_noise_ids(expected_json)

        self.maxDiff = None
        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')


    def test_sampler_result(self) -> None:
        '''Should be passed.'''

        quasi_dists = [QuasiDistribution({'00': 0.5, '11': 0.5})]
        metadata = [{'sample_size': 1024}]

        sampler_result = SamplerResult(quasi_dists=quasi_dists, metadata=metadata)

        actual_json = self.encoder.default(sampler_result)

        expected_json = (
            '{"metadata": [{"sample_size": 1024}], '
            '"quasi_dists": ['
            '"{\\\"data\\\": \\\"{0: 0.5, 3: 0.5}\\\", \\\"shots\\\": null, \\\"stddev_upper_bound\\\": null}"'
            ']}'
        )

        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')


    def test_estimator_result(self) -> None:
        '''Should be passed.'''

        values = np.array([1.0, -0.5])
        metadata = [{'sample_size': 1024}, {'sample_size': 2048}]

        estimator = EstimatorResult(values, metadata)

        actual_json = self.encoder.default(estimator)

        expected_json = (
            '{"metadata": [{"sample_size": 1024}, {"sample_size": 2048}], '
            '"values": {"__class__": "np.ndarray", "list": [1.0, -0.5]}}'
        )

        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')


    def test_vqe_result(self) -> None:
        '''Should be passed.'''

        vqe_result = VQEResult()

        vqe_result.eigenvalue = 1.0 
        vqe_result.optimal_parameters = {'param1': 0.5, 'param2': -0.5}
        vqe_result.optimal_point = [0.5, -0.5]
        vqe_result.optimal_value = 0.5
        vqe_result.optimizer_evals = 100
        vqe_result.optimizer_time = 10
        vqe_result.cost_function_evals = 50

        optimal_circuit = self.quantum_circuit_factory()

        vqe_result.optimal_circuit = optimal_circuit

        vqe_result.aux_operators_evaluated = [(0.5, (0.1, 1000))]

        actual_json = self.encoder.default(vqe_result)

        expected_json = '{"eigenvalue": 1.0}'

        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')


    def test_graph(self) -> None:
        '''Should be passed.'''

        graph = nx.Graph()
        graph.add_nodes_from([1, 2, 3])
        graph.add_edges_from([(1, 2), (1, 3)])

        actual_json = self.encoder.default(graph)

        expected_json = (
            '{"nodes": [[1, {}], [2, {}], [3, {}]], '
            '"edges": [[1, 2, {}], [1, 3, {}]]}'
        )

        self.assertEqual(actual_json, expected_json, 'actual and expected outputs are not the same')



    # the code below is for removing fields that change between executions
        

    def clean_aer_json(self, data: str) -> str:
        import json

        def remove_fields_from_dict(d: dict, fields: list) -> None:
            for field in fields:
                d.pop(field, None)
            for key, value in d.items():
                if isinstance(value, dict):
                    remove_fields_from_dict(value, fields)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            remove_fields_from_dict(item, fields)

        fields_to_ignore = [
            'date', 'job_id', 'qobj_id', 'seed_simulator', 'time_taken', 
            'time_taken_execute', 'time_taken_parameter_binding', 'name'
        ]

        data = json.loads(data)
        remove_fields_from_dict(data, fields_to_ignore)
        data = json.dumps(data)
        return data


    def remove_noise_ids(self, json_data: str) -> str:
        import json
        data = json.loads(json_data)
        if "errors" in data:
            for error in data["errors"]:
                if "id" in error:
                    del error["id"]
        return json.dumps(data)


    def remove_circuit_id(self, encoded_result: str) -> str:
        import json
        result_dict = json.loads(encoded_result)
        if 'qc' in result_dict and 'qobj_id' in result_dict['qc']:
            del result_dict['qc']['qobj_id']
        return json.dumps(result_dict)
    

    def remove_circuit_name(self, encoded_result: str) -> str:
        import json

        result_dict = json.loads(encoded_result)

        if 'qc' in result_dict and 'experiments' in result_dict['qc'] and 'header' in result_dict['qc']['experiments'][0]:
            result_dict['qc']['experiments'][0]['header']['name'] = 'circuit'
        return json.dumps(result_dict)
    

    def remove_qobj_id(self, encoded_result: str) -> str:
        import json
        result_dict = json.loads(encoded_result)
        if 'qobj_id' in result_dict:
            del result_dict['qobj_id']
        return json.dumps(result_dict)
    


if __name__ == '__main__':
    unittest.main()
    

