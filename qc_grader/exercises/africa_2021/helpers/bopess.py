from qiskit_nature.results.bopes_sampler_result import BOPESSamplerResult


def bopessresult_to_dict(result: BOPESSamplerResult) -> str:
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

    return result_dict
