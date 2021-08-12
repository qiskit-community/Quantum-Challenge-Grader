import json

from qiskit_nature.results.bopes_sampler_result import BOPESSamplerResult

from qc_grader.util import _QobjEncoder


def bopessresult_to_json(result: BOPESSamplerResult) -> str:
    from copy import deepcopy as copy

    result_dict = copy(result.__dict__)
    result_dict['_raw_results'] = dict(
        [(k, v.__dict__) for k, v in result_dict['_raw_results'].items()]
    )

    # Convert each '_raw_result' item in the above list of results into a dictionary. Each item is a VQEResult
    for key in result_dict['_raw_results'].keys():
        result_dict['_raw_results'][key]['_raw_result'] = copy(
            result_dict['_raw_results'][key]['_raw_result'].__dict__
        )

    return json.dumps(result_dict, cls=_QobjEncoder)
