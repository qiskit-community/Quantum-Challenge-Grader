import os
import requests

from typing import Optional

QC_API_NAME = 'IBM Quantum Challenge'
QC_API_VERSION = '2020'
QC_API_URLS: list = [
    'http://127.0.0.1:5000',
    'https://qac-grading-dev.quantum-computing.ibm.com'
]


def get_server_endpoint(lab_id: Optional[str] = None, ex_id: Optional[str] = None) -> Optional[str]:
    endpoint = os.getenv('QC_GRADING_ENDPOINT')

    if not endpoint:
        for server_url in QC_API_URLS:
            try:
                response = requests.get(url=server_url)
                response.raise_for_status()

                if response.json().get(QC_API_NAME) == QC_API_VERSION:
                    if lab_id and ex_id:
                        question_name = f'{lab_id}/{ex_id}'
                        available_validations = response.json().get('available validations')

                        if not available_validations or question_name in available_validations:
                            endpoint = server_url
                            break
                        else:
                            continue

                    endpoint = server_url
                    break
            except Exception as e:
                pass

    return normalize_final_slash(endpoint) if endpoint else None


def send_request(
    endpoint: str,
    query: Optional[dict] = None,
    body: Optional[dict] = None,
    method: str = 'POST',
    header: Optional[dict] = None
) -> dict:
    header = header if header else {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request(
        method,
        url=endpoint,
        params=query,
        json=body,
        headers=header
    )
    response.raise_for_status()

    return response.json()


def normalize_final_slash(url: str) -> str:
    if url[-1] != '/':
        url += '/'

    return url
