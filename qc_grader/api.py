import os
import requests

from typing import Optional
from urllib.parse import urljoin


QC_API_NAME = 'IBM Quantum Challenge'
QC_API_VERSION = '2020'

QC_GRADING_LOCAL: list = ['http://127.0.0.1:5000']
QC_GRADING_STAGING: list = ['https://qac-grading-dev.quantum-computing.ibm.com']
QC_GRADING: list = ['https://qac-grading.quantum-computing.ibm.com']

_api_auth_url: Optional[str] = None
_api_submit_url: Optional[str] = None

if 'auth-dev' not in os.getenv('QXAuthURL', 'auth-dev'):
    grading_urls = QC_GRADING_LOCAL + QC_GRADING
else:
    grading_urls = QC_GRADING_LOCAL + QC_GRADING_STAGING


def get_server_endpoint(lab_id: Optional[str] = None, ex_id: Optional[str] = None) -> Optional[str]:
    endpoint = os.getenv('QC_GRADING_ENDPOINT')

    if not endpoint:
        for server_url in grading_urls:
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


def get_auth_endpoint() -> Optional[str]:
    # https://auth-dev.quantum-computing.ibm.com/api/challenges/answers
    global _api_auth_url
    if not _api_auth_url:
        url = os.getenv('QXAuthURL')
        if not url:
            url = 'https://auth-dev.quantum-computing.ibm.com/api'
            # print(f'Using auth api server at {url}')

        _api_auth_url = normalize_final_slash(url)

    return _api_auth_url


def get_submission_endpoint() -> Optional[str]:
    # https://auth-dev.quantum-computing.ibm.com/api/challenges/answers
    global _api_submit_url
    if not _api_submit_url:
        if 'auth-dev' not in os.getenv('QXAuthURL', 'auth-dev'):
            # url = 'https://api.quantum-computing.ibm.com/api'
            url = 'https://auth.quantum-computing.ibm.com/api'
        else:
            url = 'https://auth-dev.quantum-computing.ibm.com/api'

        _api_submit_url = normalize_final_slash(url)

    return _api_submit_url


def get_access_token() -> str:
    iqx_token = os.getenv('QXToken')
    baseurl = get_auth_endpoint()
    endpoint = urljoin(baseurl, './users/loginWithToken')
    response = requests.post(endpoint, json={'apiToken': iqx_token})
    response.raise_for_status()
    return response.json()['id']


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

    if not response.ok:
        if response.status_code == 403:
            result = f'Unable to access service ({response.reason})'
        else:
            result = response.json()['error']['message']
        raise Exception(result)

    return response.json()


def normalize_final_slash(url: str) -> str:
    if url[-1] != '/':
        url += '/'

    return url
