
from fractions import Fraction
from functools import wraps
import json
import logging
import inspect

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import warnings

from qiskit import IBMQ, QuantumCircuit
from qiskit.algorithms.optimizers import OptimizerResult
from qiskit.circuit import Barrier, Gate, Instruction, Measure, Parameter
from qiskit.circuit.library import UGate, U3Gate, CXGate, TwoLocal
from qiskit.opflow.primitive_ops.pauli_op import PauliOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit_aer.jobs import AerJob
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_provider import IBMProvider, IBMProviderError
from qiskit.quantum_info import SparsePauliOp
from networkx.classes import Graph
from qiskit_ibm_provider.job import IBMCircuitJob as IBMQJob
from qiskit.qobj import PulseQobj, QasmQobj
from qiskit.result import ProbDistribution, QuasiDistribution
from qiskit.algorithms.minimum_eigensolvers.vqe import VQEResult

from networkx import Graph



class QObjEncoder(json.encoder.JSONEncoder):
    def default(self, obj: Any) -> Any:
        import numpy as np

        if isinstance(obj, np.integer):
            return {'__class__': 'np.integer', 'int': int(obj)}
        if isinstance(obj, np.floating):
            return {'__class__': 'np.floating', 'float': float(obj)}
        if isinstance(obj, np.ndarray):
            return {'__class__': 'np.ndarray', 'list': obj.tolist()}
        if isinstance(obj, complex):
            return {'__class__': 'complex', 're': obj.real, 'im': obj.imag}
        if isinstance(obj, Fraction):
            return {'__class__': 'Fraction', 'numerator': obj.numerator, 'denominator': obj.denominator}
        if isinstance(obj, Parameter):
            return {'__class__': 'Parameter', 'name': obj.name, 'uuid': str(obj._uuid)}

        return json.JSONEncoder.default(self, obj)



class CustomJSONEncoder(json.encoder.JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, IBMQJob):
            payload = self.serialize_job(obj)
        elif isinstance(obj, AerJob):
            payload = self.serialize_aerjob_result(obj)
        elif isinstance(obj, QuantumCircuit):
            print(obj, **kwargs)
            payload = self.circuit_to_json(obj, **kwargs)
        elif isinstance(obj, PauliSumOp):
            payload = self.paulisumop_to_json(obj)
        elif isinstance(obj, PauliOp):
            payload = self.pauliop_to_json(obj)
        elif isinstance(obj, SparsePauliOp):
            payload = self.sparsepauliop_to_json(obj)
        elif isinstance(obj, (PulseQobj, QasmQobj)):
            payload = self.qobj_to_json(obj)
        elif isinstance(obj, SamplerResult):
            payload = self.samplerresult_to_json(obj)
        elif isinstance(obj, EstimatorResult):
            payload = self.estimatorresult_to_json(obj)
        elif isinstance(obj, Graph):
            payload = self.graph_to_json(obj)
        elif isinstance(obj, QuasiDistribution):
            payload = self.quasidistribution_to_json(obj)
        elif isinstance(obj, ProbDistribution):
            payload = self.probdistribution_to_json(obj)
        elif isinstance(obj, VQEResult):
            payload = self.vqeresult_to_json(obj)
        elif isinstance(obj, NoiseModel):
            payload = self.noisemodel_to_json(obj)
        elif isinstance(obj, TwoLocal):
            payload = self.circuit_to_json(obj)
        elif isinstance(obj, (complex, float, int)):
            payload = str(obj)
        elif isinstance(obj, str):
            payload = obj
        else:
            payload = json.dumps(obj, skipkeys=True, cls=QObjEncoder)

        return payload


    def serialize_job(self, job: IBMQJob) -> Optional[Dict[str, str]]:
        from qiskit.providers import JobStatus

        job_status = job.status()

        if job_status in [JobStatus.CANCELLED, JobStatus.ERROR]:
            print(f'Job did not successfully complete: {job_status.value}.')
            return None
        elif job_status is not JobStatus.DONE:
            print(f'Job has not yet completed: {job_status.value}.')
            print(f'Please wait for the job (id: {job.job_id()}) to complete then try again.')
            return None

        download_url, result_url = self.get_job_urls(job)

        if not download_url or not result_url:
            print('Unable to obtain job URLs')
            return None

        return json.dumps({
            'download_url': download_url,
            'result_url': result_url
        })
    

    def serialize_aerjob_result(self, job: AerJob) -> Optional[Dict[str, str]]:
        from qiskit.providers import JobStatus

        job_status = job.status()

        if job_status in [JobStatus.CANCELLED, JobStatus.ERROR]:
            print(f'Job did not successfully complete: {job_status.value}.')
            return None
        elif job_status is not JobStatus.DONE:
            print(f'Job has not yet completed: {job_status.value}.')
            print(f'Please wait for the job (id: {job.job_id()}) to complete then try again.')
            return None

        return json.dumps(job.result().to_dict())


    def get_job_urls(
        self,
        job: Union[str, IBMQJob],
        hub: Optional[str] = None,
        group: Optional[str] = None,
        project: Optional[str] = None,
        load_account_fallback: Optional[bool] = True
    ) -> Tuple[Optional[str], Optional[str]]:
        try:
            job_id = job.job_id() if isinstance(job, IBMQJob) else job
            provider = self.get_provider(hub, group, project, load_account_fallback)
            download_url = provider._api_client.account_api.job(job_id).download_url()['url']
            result_url = provider._api_client.account_api.job(job_id).result_url()['url']
            return download_url, result_url
        except Exception:
            return None, None


    def circuit_to_dict( 
        self,
        qc: QuantumCircuit,
        parameter_binds: Optional[List[Dict[Parameter, float]]] = None
    ) -> Dict[str, Any]:
        from qiskit import assemble
        if not parameter_binds:
            qobj = assemble(qc)
        else:
            qobj = assemble(qc, parameter_binds=parameter_binds)
        return qobj.to_dict()


    def circuit_to_json(
        self,
        qc: Union[TwoLocal, QuantumCircuit],
        parameter_binds: Optional[List] = None,
        byte_string: bool = False
    ) -> str:
        if not byte_string and not isinstance(qc, TwoLocal) and (qc.num_parameters == 0 or parameter_binds is not None):
            circuit = self.circuit_to_dict(qc, parameter_binds)
            byte_string = False
        else:
            import pickle
            circuit = pickle.dumps(qc).decode('ISO-8859-1')
            byte_string = True

        return json.dumps({
            'qc': circuit,
            'byte_string': byte_string
        }, cls=QObjEncoder)


    def qobj_to_json(self, qobj: Union[PulseQobj, QasmQobj]) -> str:
        return json.dumps(qobj.to_dict(), cls=QObjEncoder)


    def sparsepauliop_to_json(self, op: SparsePauliOp) -> str:
        return json.dumps(op.to_list(), cls=QObjEncoder)


    def paulisumop_to_json(self, op: PauliSumOp) -> str:
        return json.dumps(op.primitive.to_list(), cls=QObjEncoder)


    def pauliop_to_json(self, op: PauliOp) -> str:
        return json.dumps({
            'primitive': op.primitive.to_label(),
            'coeff': op.coeff
        }, cls=QObjEncoder)


    def noisemodel_to_json(self, noise_model: NoiseModel) -> str:
        return json.dumps(noise_model.to_dict(), cls=QObjEncoder)


    def optimizerresult_to_json(
        self,
        op: OptimizerResult
    ) -> str:
        result = {}
        for name, value in inspect.getmembers(op):
            if (
                not name.startswith('_')
                and not inspect.ismethod(value)
                and not inspect.isfunction(value)
                and hasattr(op, name)
            ):
                result[name] = value
        return json.dumps(result, cls=QObjEncoder)


    def samplerresult_to_json(
        self,
        op: SamplerResult
    ) -> str:
        return json.dumps({
            'metadata': op.metadata,
            'quasi_dists': [self.quasidistribution_to_json(d) for d in op.quasi_dists]
        }, cls=QObjEncoder)


    def graph_to_json(
        self,
        g: Graph
    ) -> str:
        return json.dumps({
            'nodes': list(g.nodes(data=True)),
            'edges': list(g.edges(data=True))
        }, cls=QObjEncoder)


    def estimatorresult_to_json(
        self,
        op: EstimatorResult
    ) -> str:
        return json.dumps({
            'metadata': op.metadata,
            'values': op.values
        }, cls=QObjEncoder)


    def quasidistribution_to_json(
        self,
        op: QuasiDistribution
    ) -> str:
        return json.dumps({
            'data': str(op),
            'shots': op.shots if hasattr(op, 'shots') else None,
            'stddev_upper_bound': op.stddev_upper_bound if hasattr(op, 'stddev_upper_bound') else None
        }, cls=QObjEncoder)


    def probdistribution_to_json(
        self,
        op: ProbDistribution
    ) -> str:
        return json.dumps({
            'data': str(op),
            'shots': op.shots,
        }, cls=QObjEncoder)
        

    def vqeresult_to_json(
        self,
        result: VQEResult
    ) -> str:
        return json.dumps({
            'eigenvalue': result.eigenvalue
            # TODO: figure out what other parmeters need to be included
        }, cls=QObjEncoder)


    def to_json(self, result: Any, skip: List[str] = []) -> str:
        if result is None:
            return ''
        as_dict = {}
        import inspect
        for name, value in inspect.getmembers(result):
            if not name.startswith('_') and name not in skip and \
                    not inspect.ismethod(value) and not inspect.isfunction(value):
                as_dict[name] = value

        return json.dumps(as_dict, cls=QObjEncoder)


    def get_provider(
        self,
        hub: Optional[str] = None,
        group: Optional[str] = None,
        project: Optional[str] = None,
        load_account_fallback: Optional[bool] = True
    ) -> IBMProvider:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            ibmq_logger = logging.getLogger('qiskit_ibm_provider')
            current_level = ibmq_logger.level
            ibmq_logger.setLevel(logging.ERROR)

            provider = None

            # get providers
            if hub or group or project:
                try:
                    providers = IBMQ.providers()
                except IBMProviderError:
                    IBMQ.load_account()
                    providers = IBMQ.providers()

                # get correct provider
                for p in providers:
                    if (
                        (hub in p.credentials.hub if hub else True)
                        and (group in p.credentials.group if group else True)
                        and (project in p.credentials.project if project else True)
                    ):
                        # correct provider found
                        provider = p
                        break

            # handle no correct provider found
            if provider is None and load_account_fallback:
                provider = IBMQ.load_account()

            ibmq_logger.setLevel(current_level)
            return provider

