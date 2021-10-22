import os
import requests

from typing import Optional, Tuple
from urllib.parse import urljoin

from . import __version__, challenge_name, challenge_version


# challenge name and version
CHALLENGE_NAME: str = os.getenv('QC_NAME', challenge_name)
CHALLENGE_VERSION: str = os.getenv('QC_VERSION', challenge_version)

# possible challenge API endpoints
QC_GRADING_LOCAL: list = ['http://127.0.0.1:5000']
QC_GRADING_STAGING: list = ['https://qac-grading-dev.quantum-computing.ibm.com']
QC_GRADING: list = ['https://qac-grading.quantum-computing.ibm.com']

_api_auth_url: Optional[str] = None
_api_submit_url: Optional[str] = None
_api_challenge_url: Optional[str] = None
_api_challenge_exercises: list = []

if 'auth-dev' not in os.getenv('QXAuthURL', 'auth-dev'):
    grading_urls = QC_GRADING_LOCAL + QC_GRADING
else:
    grading_urls = QC_GRADING_LOCAL + QC_GRADING_STAGING


class MaxContentError(BaseException):
    def __init__(self, content_length: int, max_content_length: int) -> None:
        self.message = f'Max content length ({max_content_length}) exceeded: {content_length}'

    def __str__(self) -> str:
        return self.message


def get_challenge(challenge_name: Optional[str], challenge_version: Optional[str]) -> Tuple[Optional[str], list]:
    exercises = []
    endpoint = None
    for server_url in grading_urls:
        try:
            response = requests.get(url=server_url)
            response.raise_for_status()

            if response.json().get(challenge_name) == challenge_version:
                exercises = response.json().get('available validations')
                endpoint = normalize_final_slash(server_url)
                break
        except Exception as err:
            pass
    return endpoint, exercises


def get_server_endpoint() -> Optional[str]:
    global _api_challenge_url
    if not _api_challenge_url:
        endpoint = os.getenv('QC_GRADING_ENDPOINT')
        if endpoint:
            _api_challenge_url = normalize_final_slash(endpoint)
        else:
            _api_challenge_url, _ = get_challenge(CHALLENGE_NAME, CHALLENGE_VERSION)
    return _api_challenge_url


def get_challenge_question_set() -> Optional[str]:
    global _api_challenge_exercises
    if not _api_challenge_exercises:
        _, _api_challenge_exercises = get_challenge(CHALLENGE_NAME, CHALLENGE_VERSION)
    return _api_challenge_exercises


def get_auth_endpoint() -> Optional[str]:
    # https://auth-dev.quantum-computing.ibm.com/api/challenges/answers
    global _api_auth_url
    if not _api_auth_url:
        url = os.getenv('QXAuthURL')
        if not url:
            url = 'https://auth-dev.quantum-computing.ibm.com/api'

        _api_auth_url = normalize_final_slash(url)

    return _api_auth_url


def get_submission_endpoint() -> Optional[str]:
    # https://auth-dev.quantum-computing.ibm.com/api/challenges/answers
    global _api_submit_url
    if not _api_submit_url:
        if 'auth-dev' not in os.getenv('QXAuthURL', 'auth-dev'):
            url = 'https://auth.quantum-computing.ibm.com/api'
        else:
            url = 'https://auth-dev.quantum-computing.ibm.com/api'

        _api_submit_url = normalize_final_slash(url)

    return _api_submit_url


def is_staging() -> bool:
    return 'auth-dev' in os.getenv('QXAuthURL', 'auth-dev')


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
    header: Optional[dict] = {},
    max_content_length: Optional[int] = None
) -> dict:
    default_header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Client-Version': __version__
    }
    header = {**default_header, **header}

    if max_content_length:
        content_length = compute_content_length(endpoint, body=body)
        if content_length >= max_content_length:
            raise MaxContentError(content_length, max_content_length)

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
            try:
                result = response.json()
                if 'error' in result:
                    result = result['error']
                if 'message' in result:
                    result = result['message']
            except:
                result = response.reason
        raise Exception(result)

    return response.json()


def notify_provider(access_token: str):
    server = get_server_endpoint()
    provider_response = send_request(
        urljoin(server, './provider'),
        header={
            'X-Access-Token': access_token
        }
    )


def compute_content_length(
    endpoint: str,
    query: Optional[dict] = None,
    body: Optional[dict] = None,
    method: str = 'POST',
    header: Optional[dict] = None
) -> int:
    from requests import Request
    header = header if header else {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Client-Version': __version__
    }

    req = Request(
        method,
        url=endpoint,
        params=query,
        json=body,
        headers=header
    )
    prepped = req.prepare()
    return int(prepped.headers['Content-Length'])

def normalize_final_slash(url: str) -> str:
    if url[-1] != '/':
        url += '/'

    return url
