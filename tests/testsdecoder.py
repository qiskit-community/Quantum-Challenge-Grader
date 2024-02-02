from qc_grader_json.custom_decoder import CustomJSONDecoder
import unittest
import numpy as np
from numpy.testing import assert_array_equal



class TestDecoder(unittest.TestCase):

    def setUp(self):
        self.decoder = CustomJSONDecoder()


    def test_qcuircuit(self) -> None:
        '''Should be passed.'''

        self.maxDiff = None

        json_input = (
            '{"qc": {'
            '"qobj_id": "4a4d1fcb-07b6-4cbe-b310-b72ae7cacf4b", '
            '"header": {}, '
            '"config": {'
            '"shots": 1024, "memory": false, "parameter_binds": [], "meas_level": 2, '
            '"init_qubits": true, "parametric_pulses": [], "memory_slots": 0, "n_qubits": 2'
            '}, '
            '"schema_version": "1.3.0", "type": "QASM", '
            '"experiments": [{'
            '"config": {"n_qubits": 2, "memory_slots": 0}, '
            '"header": {'
            '"qubit_labels": [["q", 0], ["q", 1]], "n_qubits": 2, "qreg_sizes": [["q", 2]], '
            '"clbit_labels": [], "memory_slots": 0, "creg_sizes": [], "name": "circuit-171", '
            '"global_phase": 0.0, "metadata": {}'
            '}, '
            '"instructions": [{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}]'
            '}'
            ']}, '
            '"byte_string": false}'
        )

        actual_obj = self.decoder.decode_answer(json_input)
        del actual_obj['qc']['qobj_id'] # removing field that changes between executions
        
        expected_obj = {
            'qc': {
            'header': {},
            'config': {'shots': 1024,
            'memory': False,
            'parameter_binds': [],
            'meas_level': 2,
            'init_qubits': True,
            'parametric_pulses': [],
            'memory_slots': 0,
            'n_qubits': 2},
            'schema_version': '1.3.0',
            'type': 'QASM',
            'experiments': [{'config': {'n_qubits': 2, 'memory_slots': 0},
                'header': {'qubit_labels': [['q', 0], ['q', 1]],
                'n_qubits': 2,
                'qreg_sizes': [['q', 2]],
                'clbit_labels': [],
                'memory_slots': 0,
                'creg_sizes': [],
                'name': 'circuit-171',
                'global_phase': 0.0,
                'metadata': {}},
                'instructions': [{'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]}]}]},
            'byte_string': False
        }


        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_pulse_qobj(self) -> None:
        '''Should be passed.'''

        json_input = (
            '{"header": {}, '
            '"config": {'
            '"meas_level": 2, "meas_return": 2, '
            '"pulse_library": [{"name": "my_pulse", "samples": [0.1, 0.2, 0.3]}], '
            '"qubit_lo_freq": [5.0], "meas_lo_freq": [6.0], "shots": 1024'
            '}, '
            '"schema_version": "1.2.0", "type": "PULSE", "experiments": []}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {
            'header': {},
            'config': {'meas_level': 2,
            'meas_return': 2,
            'pulse_library': [{'name': 'my_pulse', 'samples': [0.1, 0.2, 0.3]}],
            'qubit_lo_freq': [5.0],
            'meas_lo_freq': [6.0],
            'shots': 1024},
            'schema_version': '1.2.0',
            'type': 'PULSE',
            'experiments': []
        }
        
        
        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_aer_job(self) -> None:
        '''Should be passed.'''

        json_input = (
            '{"backend_name": "qasm_simulator", '
            '"backend_version": "0.13.1", '
            '"header": null, '
            '"status": "COMPLETED", '
            '"success": true, '
            '"results": ['
            '{'
            '"shots": 1024, '
            '"success": true, '
            '"data": {}, '
            '"meas_level": 2, '
            '"header": {'
            '"creg_sizes": [], '
            '"global_phase": 0.0, '
            '"memory_slots": 0, '
            '"n_qubits": 2, '
            '"qreg_sizes": [["q", 2]], '
            '"metadata": {}'
            '}, '
            '"status": "DONE", '
            '"metadata": {'
            '"num_bind_params": 1, '
            '"runtime_parameter_bind": false, '
            '"parallel_state_update": 8, '
            '"parallel_shots": 1, '
            '"batched_shots_optimization": false, '
            '"remapped_qubits": false, '
            '"active_input_qubits": [], '
            '"device": "CPU", '
            '"measure_sampling": false, '
            '"num_clbits": 0, '
            '"max_memory_mb": 16384, '
            '"input_qubit_map": [], '
            '"num_qubits": 0, '
            '"method": "stabilizer", '
            '"required_memory_mb": 0'
            '}'
            '}'
            '], '
            '"metadata": {'
            '"max_memory_mb": 16384, '
            '"omp_enabled": true, '
            '"max_gpu_memory_mb": 0, '
            '"parallel_experiments": 1'
            '}}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {
            'backend_name': 'qasm_simulator',
            'backend_version': '0.13.1',
            'header': None,
            'status': 'COMPLETED',
            'success': True,
            'results': [{'shots': 1024,
            'success': True,
            'data': {},
            'meas_level': 2,
            'header': {'creg_sizes': [],
                'global_phase': 0.0,
                'memory_slots': 0,
                'n_qubits': 2,
                'qreg_sizes': [['q', 2]],
                'metadata': {}},
            'status': 'DONE',
            'metadata': {'num_bind_params': 1,
                'runtime_parameter_bind': False,
                'parallel_state_update': 8,
                'parallel_shots': 1,
                'batched_shots_optimization': False,
                'remapped_qubits': False,
                'active_input_qubits': [],
                'device': 'CPU',
                'measure_sampling': False,
                'num_clbits': 0,
                'max_memory_mb': 16384,
                'input_qubit_map': [],
                'num_qubits': 0,
                'method': 'stabilizer',
                'required_memory_mb': 0}}],
            'metadata': {'max_memory_mb': 16384,
            'omp_enabled': True,
            'max_gpu_memory_mb': 0,
            'parallel_experiments': 1}
        }


        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_pauli_sum_op(self) -> None:
        '''Should be passed.'''
        
        json_input = (
            '[["X", {"__class__": "complex", "re": 1.0, "im": 0.0}], '
            '["Y", {"__class__": "complex", "re": 1.0, "im": 0.0}]]'
        )

        actual_obj = self.decoder.decode_answer(json_input, list)
        
        expected_obj = [['X', (1+0j)], ['Y', (1+0j)]]

        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_sparse_pauli_op(self) -> None:
        '''Should be passed.'''

        json_input = (
            '[["X", {"__class__": "complex", "re": 1.0, "im": 0.0}], '
            '["Z", {"__class__": "complex", "re": 0.0, "im": 1.0}]]'
        )

        actual_obj = self.decoder.decode_answer(json_input, list)
        
        expected_obj = [['X', (1+0j)], ['Z', 1j]]

        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_quasidistribution(self) -> None:
        '''Should be passed.'''
        
        json_input = (
            '{"data": "{0: 0.5, 3: 0.5, 7: 0.7}", '
            '"shots": null, "stddev_upper_bound": null}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {
            'data': '{0: 0.5, 3: 0.5, 7: 0.7}',
            'shots': None, 'stddev_upper_bound': None
        }
        
        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_probdistribution(self) -> None:
        '''Should be passed.'''
        
        json_input = (
            '{"data": "{0: 0.5, 1: 0.5, 15: 0.9}", '
            '"shots": null}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {
            'data': '{0: 0.5, 1: 0.5, 15: 0.9}',
            'shots': None
        }
        
        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_noise_model(self) -> None:
        '''Should be passed.'''

        json_input = (
            '{"errors": ['
                '{"type": "qerror", "operations": ["rz"], '
                '"instructions": ['
                    '[{"name": "id", "qubits": [0]}], '
                    '[{"name": "x", "qubits": [0]}], '
                    '[{"name": "y", "qubits": [0]}], '
                    '[{"name": "z", "qubits": [0]}]'
                '], '
                '"probabilities": [0.99775, 0.00075, 0.00075, 0.00075]'
            '}, '
                '{"type": "qerror", "operations": ["sx"], '
                '"instructions": ['
                    '[{"name": "id", "qubits": [0]}], '
                    '[{"name": "x", "qubits": [0]}], '
                    '[{"name": "y", "qubits": [0]}], '
                    '[{"name": "z", "qubits": [0]}]'
                '], '
                '"probabilities": [0.99775, 0.00075, 0.00075, 0.00075]'
            '}, '
                '{"type": "qerror", "operations": ["x"], '
                '"instructions": ['
                    '[{"name": "id", "qubits": [0]}], '
                    '[{"name": "x", "qubits": [0]}], '
                    '[{"name": "y", "qubits": [0]}], '
                    '[{"name": "z", "qubits": [0]}]'
                '], '
                '"probabilities": [0.99775, 0.00075, 0.00075, 0.00075]'
            '}, '
                '{"type": "qerror", "operations": ["cx"], '
                '"instructions": ['
                    '[{"name": "pauli", "params": ["II"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["IX"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["IY"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["IZ"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["XI"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["XX"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["XY"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["XZ"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["YI"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["YX"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["YY"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["YZ"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["ZI"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["ZX"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["ZY"], "qubits": [0, 1]}], '
                    '[{"name": "pauli", "params": ["ZZ"], "qubits": [0, 1]}]'
                '], '
                '"probabilities": ['
                    '0.9156250000000001, 0.005625000000000001, 0.005625000000000001, '
                    '0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
                    '0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
                    '0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
                    '0.005625000000000001, 0.005625000000000001, 0.005625000000000001, '
                    '0.005625000000000001'
                ']'
            '}'
            ']}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {
            'errors': [{
            'type': 'qerror',
            'operations': ['rz'],
            'instructions': [
                [{'name': 'id', 'qubits': [0]}],
                [{'name': 'x', 'qubits': [0]}],
                [{'name': 'y', 'qubits': [0]}],
                [{'name': 'z', 'qubits': [0]}]],
            'probabilities': [0.99775, 0.00075, 0.00075, 0.00075]},
            {'type': 'qerror',
            'operations': ['sx'],
            'instructions': [
                [{'name': 'id', 'qubits': [0]}],
                [{'name': 'x', 'qubits': [0]}],
                [{'name': 'y', 'qubits': [0]}],
                [{'name': 'z', 'qubits': [0]}]],
            'probabilities': [0.99775, 0.00075, 0.00075, 0.00075]},
            {'type': 'qerror',
            'operations': ['x'],
            'instructions': [
                [{'name': 'id', 'qubits': [0]}],
                [{'name': 'x', 'qubits': [0]}],
                [{'name': 'y', 'qubits': [0]}],
                [{'name': 'z', 'qubits': [0]}]],
            'probabilities': [0.99775, 0.00075, 0.00075, 0.00075]},
            {'type': 'qerror',
            'operations': ['cx'],
            'instructions': [
                [{'name': 'pauli', 'params': ['II'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['IX'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['IY'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['IZ'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['XI'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['XX'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['XY'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['XZ'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['YI'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['YX'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['YY'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['YZ'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['ZI'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['ZX'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['ZY'], 'qubits': [0, 1]}],
                [{'name': 'pauli', 'params': ['ZZ'], 'qubits': [0, 1]}]],
            'probabilities': [
                0.9156250000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001,
                0.005625000000000001]}]
        }
    

        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')

    
    def test_sampler_result(self) -> None:
        '''Should be passed.'''

        json_input = (
            '{"metadata": [{"sample_size": 1024}], '
            '"quasi_dists": ["{\\"data\\": \\"{0: 0.5, 3: 0.5}\\", '
            '\\"shots\\": null, \\"stddev_upper_bound\\": null}"]}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
       
        expected_obj = {
            'metadata': [{'sample_size': 1024}],
            'quasi_dists': ['{"data": "{0: 0.5, 3: 0.5}", "shots": null, "stddev_upper_bound": null}']
            }
    
        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_estimator_result(self) -> None:
        '''Should be passed.'''

        json_input = (
            '{"metadata": [{"sample_size": 1024}, '
            '{"sample_size": 2048}], "values": {"__class__": "np.ndarray", '
            '"list": [1.0, -0.5]}}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)

        expected_obj = {
            'metadata': [{'sample_size': 1024}, {'sample_size': 2048}],
            'values': np.array([ 1. , -0.5])
            }
        
        self.assertEqual(actual_obj['metadata'], expected_obj['metadata'], "Metadata does not match")

        try:
            assert_array_equal(actual_obj['values'], expected_obj['values'])
        except AssertionError as e:
            self.fail(f"Arrays do not match: {e}")
        

    def test_vqe_result(self) -> None:
        '''Should be passed.'''

        json_input = '{"eigenvalue": 1.0}'
        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {'eigenvalue': 1.0}

        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')


    def test_graph(self) -> None:
        '''Should be passed.'''
        
        json_input = (
            '{"nodes": [[1, {}], [2, {}], [3, {}]], '
            '"edges": [[1, 2, {}], [1, 3, {}]]}'
        )

        actual_obj = self.decoder.decode_answer(json_input, dict)
        
        expected_obj = {
            'nodes': [[1, {}], [2, {}], [3, {}]],
            'edges': [[1, 2, {}], [1, 3, {}]]
        }

        self.assertEqual(actual_obj, expected_obj, 'actual and expected outputs are not the same')



if __name__ == '__main__':
    unittest.main()
    