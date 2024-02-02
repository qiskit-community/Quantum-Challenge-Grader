import json
import pickle
import requests

from fractions import Fraction
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Union, cast

import numpy as np

import qiskit.quantum_info as qi
from qiskit import QuantumCircuit, Aer, execute, assemble
from qiskit.algorithms.optimizers import OptimizerResult
from qiskit.assembler import disassemble
from qiskit.circuit import Barrier, Gate, Instruction, Measure, Parameter
from qiskit.circuit.library import UGate, U2Gate, U3Gate, CXGate, TwoLocal
from qiskit.opflow.primitive_ops.pauli_op import PauliOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_provider.utils.qobj_utils import dict_to_qobj
from qiskit.quantum_info import SparsePauliOp
from qiskit.qobj import QasmQobj, PulseQobj
from qiskit.quantum_info import Pauli
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob
from qiskit.result import Result
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.result import QuasiDistribution, ProbDistribution
from qiskit.algorithms.minimum_eigensolvers.vqe import VQEResult

from networkx import Graph
import logging

logger = logging.getLogger('qc_grading_server')



class CustomJSONDecoder(json.JSONDecoder):
    def decode_answer(
        self,
        answer: Any,
        answer_type: Optional[str] = None
    ) -> Union[Tuple, QuantumCircuit, int, str]:
        
        if answer_type == IBMQJob.__name__:
            answer_dict = json.loads(answer)
            circuits, result = self.download_circuit(
                answer_dict['download_url'],
                answer_dict['result_url']
            )
            return (circuits, result)
        elif answer_type == Result.__name__:
            result_dict = self.json_to_dict(answer)
            return Result.from_dict(result_dict)
        elif answer_type == QuantumCircuit.__name__:
            return self.json_to_circuit(answer)
        elif answer_type == PulseQobj.__name__:
            return self.json_to_pulseqobj(answer)
        elif answer_type == PauliSumOp.__name__:
            return self.json_to_paulisumop(answer)
        elif answer_type == SparsePauliOp.__name__:
            return self.json_to_sparsepauliop(answer)
        elif answer_type == Graph.__name__:
            return self.json_to_graph(answer)
        elif answer_type == PauliOp.__name__:
            return self.json_to_pauliop(answer)
        elif answer_type == SamplerResult.__name__:
            return self.json_to_SamplerResult(answer)
        elif answer_type == EstimatorResult.__name__:
            return self.json_to_EstimatorResult(answer)
        elif answer_type == QuasiDistribution.__name__:
            return self.json_to_QuasiDistribution(answer)
        elif answer_type == VQEResult.__name__:
            return self.json_to_vqeresult(answer)
        elif answer_type == OptimizerResult.__name__:
            return self.json_to_optimizerresult(answer)
        elif answer_type == NoiseModel.__name__:
            return self.json_to_noisemodel(answer)
        elif answer_type == TwoLocal.__name__:
            return self.deserialize_two_local(answer)
        elif answer_type == int.__name__:
            return int(answer)
        elif answer_type == float.__name__:
            return float(answer)
        elif answer_type == complex.__name__:
            return complex(answer)
        elif answer_type == bool.__name__:
            return answer.lower() == 'true'
        elif answer_type == str.__name__:
            return answer
        else:
            return self.json_to_dict(answer)
        

    def download_circuit(self, download_url: str, result_url: str) -> Tuple[List[QuantumCircuit], Result]:
        try:
            circuit_dict = requests.get(download_url).json()
            result_dict = requests.get(result_url).json()
        except Exception as err:
            logger.warning(f'Failed to download circuit: {err}')
            raise Exception('error downloading circuit')

        circuits: List[QuantumCircuit] = []
        try:
            # circuits = dict_to_circuit(circuit_dict)
            circuits, _, _ = disassemble(dict_to_qobj(circuit_dict))
        except Exception as err:
            logger.warning(f'Failed to disassemble circuit: {err}')

        result = None
        try:
            result = Result.from_dict(result_dict)
        except Exception as err:
            logger.warning(f'Failed to create result: {err}')

        if not result:
            raise Exception('error processing result')

        return circuits, result


    def custom_decode(self, dct: Any) -> Any:
        if isinstance(dct, dict):
            if dct.get('__class__') == 'complex':
                return complex(dct['re'], dct['im'])
            if dct.get('__class__') == 'np.ndarray':
                return np.asarray(dct['list'])
            if dct.get('__class__') == 'np.integer':
                return int(dct['int'])
            if dct.get('__class__') == 'np.floating':
                return float(dct['float'])
            if dct.get('__class__') == 'Fraction':
                return Fraction(dct['numerator'], dct['denominator'])
            if dct.get('__class__') == 'Parameter':
                import uuid
                p = Parameter.__new__(
                    Parameter,
                    dct['name'],
                    uuid=uuid.UUID(dct['uuid'])
                )
                p.__init__(dct['name'])
                return p
        return dct


    def circuit_to_dict(self, qc: QuantumCircuit, parameter_binds: Optional[List] = None) -> dict:
        if not parameter_binds:
            qobj = assemble(qc)
        else:
            qobj = assemble(qc, parameter_binds=parameter_binds)
        return qobj.to_dict()


    def circuit_to_json(self, qc: QuantumCircuit, parameter_binds: Optional[List] = None) -> str:
        class _QobjEncoder(json.encoder.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if isinstance(obj, complex):
                    return (obj.real, obj.imag)
                return json.JSONEncoder.default(self, obj)

        return json.dumps(self.circuit_to_dict(qc, parameter_binds), cls=_QobjEncoder)


    def dict_to_circuit(self, dict_: dict) -> QuantumCircuit:
        qobj = QasmQobj.from_dict(dict_)
        return disassemble(qobj)[0][0]


    def deserialize_two_local(self, json_: Union[dict, str], byte_string: bool = False) -> TwoLocal:
        if byte_string:
            return pickle.loads(cast(str, json_).encode('ISO-8859-1'))

        answer_dict = self.json_to_dict(json_) if isinstance(json_, str) else json_
        answer_ref = answer_dict['qc'] if 'qc' in answer_dict else answer_dict
        answer_byte = answer_dict['byte_string'] if 'byte_string' in answer_dict else False

        if answer_byte:
            return pickle.loads(answer_ref.encode('ISO-8859-1'))
        elif isinstance(answer_ref, dict):
            return self.dict_to_circuit(answer_ref)
        else:
            return self.dict_to_circuit(json.loads(answer_ref))


    def json_to_circuit(self, json_: Union[dict, str], byte_string: bool = False) -> QuantumCircuit:
        if byte_string:
            return pickle.loads(cast(str, json_).encode('ISO-8859-1'))

        answer_dict = self.json_to_dict(json_) if isinstance(json_, str) else json_
        answer_qc = answer_dict['qc'] if 'qc' in answer_dict else answer_dict
        answer_byte = answer_dict['byte_string'] if 'byte_string' in answer_dict else False

        if answer_byte:
            return pickle.loads(answer_qc.encode('ISO-8859-1'))
        elif isinstance(answer_qc, dict):
            return self.dict_to_circuit(answer_qc)
        else:
            return self.dict_to_circuit(json.loads(answer_qc))


    def json_to_dict(self, json_: str) -> dict:
        return json.loads(json_, object_hook=self.custom_decode)


    def json_to_paulisumop(self, json_: str) -> PauliSumOp:
        def to_pauli_list(item: List) -> Tuple:
            if isinstance(item[1], complex):
                return (item[0], item[1])
            return (item[0], complex(item[1][0], item[1][1]))

        list_ = json.loads(json_, object_hook=self.custom_decode)
        pauli_list = list(map(to_pauli_list, list_))
        return PauliSumOp.from_list(pauli_list)


    def json_to_pauliop(self, json_: str) -> PauliOp:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        return PauliOp(
            Pauli(dict_['primitive']),
            dict_['coeff']
        )


    def json_to_sparsepauliop(self, json_: str) -> SparsePauliOp:
        def to_pauli_list(item: List) -> Tuple:
            if isinstance(item[1], complex):
                return (item[0], item[1])
            return (item[0], complex(item[1][0], item[1][1]))

        list_ = json.loads(json_, object_hook=self.custom_decode)
        pauli_list = list(map(to_pauli_list, list_))
        return SparsePauliOp.from_list(pauli_list)


    def json_to_optimizerresult(self, json_: str) -> OptimizerResult:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        result = OptimizerResult()
        result.x = dict_['x']
        result.fun = dict_['fun']
        result.jac = dict_['jac']
        result.nfev = dict_['nfev']
        result.njev = dict_['njev']
        result.nit = dict_['nit']
        return result


    def json_to_SamplerResult(self, json_: str) -> SamplerResult:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        return SamplerResult(
            [self.json_to_QuasiDistribution(d) for d in dict_["quasi_dists"]],
            dict_["metadata"]
        )


    def json_to_EstimatorResult(self, json_: str) -> EstimatorResult:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        return EstimatorResult(
            dict_["values"],
            dict_["metadata"]
        )


    def json_to_QuasiDistribution(self, json_: str) -> QuasiDistribution:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        import ast
        return QuasiDistribution(
            ast.literal_eval(dict_['data']),
            dict_['shots'],
            dict_['stddev_upper_bound']
        )


    def json_to_ProbDistribution(self, json_: str) -> ProbDistribution:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        import ast
        return ProbDistribution(
            ast.literal_eval(dict_['data']),
            dict_['shots'],
        )


    def json_to_graph(self, json_: str) -> Graph:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        g = Graph()
        g.add_nodes_from(dict_['nodes'])
        g.add_edges_from(dict_['edges'])
        return g


    def json_to_vqeresult(self, json_: str) -> VQEResult:
        dict_ = json.loads(json_, object_hook=self.custom_decode)
        result = VQEResult()
        result.eigenvalue = dict_['eigenvalue']
        # TODO: figure out what other parmeters need to be included
        return result


    def json_to_noisemodel(self, json_: str) -> NoiseModel:
        return NoiseModel.from_dict(json.loads(json_, object_hook=self.custom_decode))


    def json_to_pulseqobj(self, json_: str) -> PulseQobj:
        return PulseQobj.from_dict(json.loads(json_, object_hook=self.custom_decode))















# import json
# import pickle
# import requests

# from fractions import Fraction
# from functools import wraps
# from typing import Any, Callable, List, Optional, Tuple, Union, cast

# import numpy as np

# import qiskit.quantum_info as qi
# from qiskit import QuantumCircuit, Aer, execute, assemble
# from qiskit.algorithms.optimizers import OptimizerResult
# from qiskit.assembler import disassemble
# from qiskit.circuit import Barrier, Gate, Instruction, Measure, Parameter
# from qiskit.circuit.library import UGate, U2Gate, U3Gate, CXGate, TwoLocal
# from qiskit.opflow.primitive_ops.pauli_op import PauliOp
# from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
# from qiskit.primitives import SamplerResult, EstimatorResult
# from qiskit_aer.noise import NoiseModel
# from qiskit_ibm_provider.utils.qobj_utils import dict_to_qobj
# from qiskit.quantum_info import SparsePauliOp
# from qiskit.qobj import QasmQobj, PulseQobj
# from qiskit.quantum_info import Pauli
# from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob
# from qiskit.result import Result
# from qiskit.primitives import SamplerResult, EstimatorResult
# from qiskit.result import QuasiDistribution, ProbDistribution
# from qiskit.algorithms.minimum_eigensolvers.vqe import VQEResult

# from networkx import Graph

# #from .general import logger

# class CustomJSONDecoder(json.JSONDecoder):
#     def __init__(self, answer: Any, answer_type: Optional[str] = None):
#         self.answer = answer
#         self.answer_type = answer_type

#     def decode_answer(
#         self,
#     ) -> Union[Tuple, QuantumCircuit, int, str]:

#         if self.answer_type == IBMQJob.__name__:
#             answer_dict = json.loads(self.answer)
#             circuits, result = self.download_circuit(
#                 answer_dict['download_url'],
#                 answer_dict['result_url']
#             )
#             return (circuits, result)
#         elif self.answer_type == Result.__name__:
#             result_dict = self.json_to_dict(self.answer)
#             return Result.from_dict(result_dict)
#         elif self.answer_type == QuantumCircuit.__name__:
#             return self.json_to_circuit(self.answer)
#         elif self.answer_type == PulseQobj.__name__:
#             return self.json_to_pulseqobj(self.answer)
#         elif self.answer_type == PauliSumOp.__name__:
#             return self.json_to_paulisumop(self.answer)
#         elif self.answer_type == SparsePauliOp.__name__:
#             return self.json_to_sparsepauliop(self.answer)
#         elif self.answer_type == Graph.__name__:
#             return self.json_to_graph(self.answer)
#         elif self.answer_type == PauliOp.__name__:
#             return self.json_to_pauliop(self.answer)
#         elif self.answer_type == SamplerResult.__name__:
#             return self.json_to_SamplerResult(self.answer)
#         elif self.answer_type == EstimatorResult.__name__:
#             return self.json_to_EstimatorResult(self.answer)
#         elif self.answer_type == QuasiDistribution.__name__:
#             return self.json_to_QuasiDistribution(self.answer)
#         elif self.answer_type == VQEResult.__name__:
#             return self.json_to_vqeresult(self.answer)
#         elif self.answer_type == OptimizerResult.__name__:
#             return self.json_to_optimizerresult(self.answer)
#         elif self.answer_type == NoiseModel.__name__:
#             return self.json_to_noisemodel(self.answer)
#         elif self.answer_type == TwoLocal.__name__:
#             return self.deserialize_two_local(self.answer)
#         elif self.answer_type == int.__name__:
#             return int(self.answer)
#         elif self.answer_type == float.__name__:
#             return float(self.answer)
#         elif self.answer_type == complex.__name__:
#             return complex(self.answer)
#         elif self.answer_type == bool.__name__:
#             return self.answer.lower() == 'true'
#         elif self.answer_type == str.__name__:
#             return self.answer
#         else:
#             return self.json_to_dict(self.answer)
        
#     def download_circuit(self, download_url: str, result_url: str) -> Tuple[List[QuantumCircuit], Result]:
#         try:
#             circuit_dict = requests.get(download_url).json()
#             result_dict = requests.get(result_url).json()
#         except Exception as err:
#             logger.warning(f'Failed to download circuit: {err}')
#             raise Exception('error downloading circuit')

#         circuits: List[QuantumCircuit] = []
#         try:
#             # circuits = dict_to_circuit(circuit_dict)
#             circuits, _, _ = disassemble(dict_to_qobj(circuit_dict))
#         except Exception as err:
#             logger.warning(f'Failed to disassemble circuit: {err}')

#         result = None
#         try:
#             result = Result.from_dict(result_dict)
#         except Exception as err:
#             logger.warning(f'Failed to create result: {err}')

#         if not result:
#             raise Exception('error processing result')

#         return circuits, result

#     def custom_decode(self, dct: Any) -> Any:
#         if isinstance(dct, dict):
#             if dct.get('__class__') == 'complex':
#                 return complex(dct['re'], dct['im'])
#             if dct.get('__class__') == 'np.ndarray':
#                 return np.asarray(dct['list'])
#             if dct.get('__class__') == 'np.integer':
#                 return int(dct['int'])
#             if dct.get('__class__') == 'np.floating':
#                 return float(dct['float'])
#             if dct.get('__class__') == 'Fraction':
#                 return Fraction(dct['numerator'], dct['denominator'])
#             if dct.get('__class__') == 'Parameter':
#                 import uuid
#                 p = Parameter.__new__(
#                     Parameter,
#                     dct['name'],
#                     uuid=uuid.UUID(dct['uuid'])
#                 )
#                 p.__init__(dct['name'])
#                 return p
#         return dct

#     def circuit_to_dict(self, qc: QuantumCircuit, parameter_binds: Optional[List] = None) -> dict:
#         if not parameter_binds:
#             qobj = assemble(qc)
#         else:
#             qobj = assemble(qc, parameter_binds=parameter_binds)
#         return qobj.to_dict()

#     def circuit_to_json(self, qc: QuantumCircuit, parameter_binds: Optional[List] = None) -> str:
#         class _QobjEncoder(json.encoder.JSONEncoder):
#             def default(self, obj: Any) -> Any:
#                 if isinstance(obj, np.ndarray):
#                     return obj.tolist()
#                 if isinstance(obj, complex):
#                     return (obj.real, obj.imag)
#                 return json.JSONEncoder.default(self, obj)

#         return json.dumps(self.circuit_to_dict(qc, parameter_binds), cls=_QobjEncoder)

#     def dict_to_circuit(self, dict_: dict) -> QuantumCircuit:
#         qobj = QasmQobj.from_dict(dict_)
#         return disassemble(qobj)[0][0]

#     def deserialize_two_local(self, json_: Union[dict, str], byte_string: bool = False) -> TwoLocal:
#         if byte_string:
#             return pickle.loads(cast(str, json_).encode('ISO-8859-1'))

#         answer_dict = self.json_to_dict(json_) if isinstance(json_, str) else json_
#         answer_ref = answer_dict['qc'] if 'qc' in answer_dict else answer_dict
#         answer_byte = answer_dict['byte_string'] if 'byte_string' in answer_dict else False

#         if answer_byte:
#             return pickle.loads(answer_ref.encode('ISO-8859-1'))
#         elif isinstance(answer_ref, dict):
#             return self.dict_to_circuit(answer_ref)
#         else:
#             return self.dict_to_circuit(json.loads(answer_ref))

#     def json_to_circuit(self, json_: Union[dict, str], byte_string: bool = False) -> QuantumCircuit:
#         if byte_string:
#             return pickle.loads(cast(str, json_).encode('ISO-8859-1'))

#         answer_dict = self.json_to_dict(json_) if isinstance(json_, str) else json_
#         answer_qc = answer_dict['qc'] if 'qc' in answer_dict else answer_dict
#         answer_byte = answer_dict['byte_string'] if 'byte_string' in answer_dict else False

#         if answer_byte:
#             return pickle.loads(answer_qc.encode('ISO-8859-1'))
#         elif isinstance(answer_qc, dict):
#             return self.dict_to_circuit(answer_qc)
#         else:
#             return self.dict_to_circuit(json.loads(answer_qc))

#     def json_to_dict(self, json_: str) -> dict:
#         return json.loads(json_, object_hook=self.custom_decode)

#     def json_to_paulisumop(self, json_: str) -> PauliSumOp:
#         def to_pauli_list(item: List) -> Tuple:
#             if isinstance(item[1], complex):
#                 return (item[0], item[1])
#             return (item[0], complex(item[1][0], item[1][1]))

#         list_ = json.loads(json_, object_hook=self.custom_decode)
#         pauli_list = list(map(to_pauli_list, list_))
#         return PauliSumOp.from_list(pauli_list)

#     def json_to_pauliop(self, json_: str) -> PauliOp:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         return PauliOp(
#             Pauli(dict_['primitive']),
#             dict_['coeff']
#         )

#     def json_to_sparsepauliop(self, json_: str) -> SparsePauliOp:
#         def to_pauli_list(item: List) -> Tuple:
#             if isinstance(item[1], complex):
#                 return (item[0], item[1])
#             return (item[0], complex(item[1][0], item[1][1]))

#         list_ = json.loads(json_, object_hook=self.custom_decode)
#         pauli_list = list(map(to_pauli_list, list_))
#         return SparsePauliOp.from_list(pauli_list)

#     def json_to_optimizerresult(self, json_: str) -> OptimizerResult:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         result = OptimizerResult()
#         result.x = dict_['x']
#         result.fun = dict_['fun']
#         result.jac = dict_['jac']
#         result.nfev = dict_['nfev']
#         result.njev = dict_['njev']
#         result.nit = dict_['nit']
#         return result

#     def json_to_SamplerResult(self, json_: str) -> SamplerResult:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         return SamplerResult(
#             [self.json_to_QuasiDistribution(d) for d in dict_["quasi_dists"]],
#             dict_["metadata"]
#         )

#     def json_to_EstimatorResult(self, json_: str) -> EstimatorResult:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         return EstimatorResult(
#             dict_["values"],
#             dict_["metadata"]
#         )

#     def json_to_QuasiDistribution(self, json_: str) -> QuasiDistribution:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         import ast
#         return QuasiDistribution(
#             ast.literal_eval(dict_['data']),
#             dict_['shots'],
#             dict_['stddev_upper_bound']
#         )

#     def json_to_ProbDistribution(self, json_: str) -> ProbDistribution:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         import ast
#         return ProbDistribution(
#             ast.literal_eval(dict_['data']),
#             dict_['shots'],
#         )

#     def json_to_graph(self, json_: str) -> Graph:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         g = Graph()
#         g.add_nodes_from(dict_['nodes'])
#         g.add_edges_from(dict_['edges'])
#         return g

#     def json_to_vqeresult(self, json_: str) -> VQEResult:
#         dict_ = json.loads(json_, object_hook=self.custom_decode)
#         result = VQEResult()
#         result.eigenvalue = dict_['eigenvalue']
#         # TODO: figure out what other parmeters need to be included
#         return result

#     def json_to_noisemodel(self, json_: str) -> NoiseModel:
#         return NoiseModel.from_dict(json.loads(json_, object_hook=self.custom_decode))

#     def json_to_pulseqobj(self, json_: str) -> PulseQobj:
#         return PulseQobj.from_dict(json.loads(json_, object_hook=self.custom_decode))
