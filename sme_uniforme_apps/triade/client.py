import requests
from dataclasses import dataclass

from .exceptions import TriadeTransientError


@dataclass
class TriadeClientResponse:
    status_code: int
    data: object
    text: str

    @property
    def is_success(self):
        return 200 <= self.status_code < 300


class TriadeHttpClient:
    def __init__(self, base_url, api_token, timeout_seconds=30, session=None):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": "Bearer {}".format(self.api_token),
                "Content-Type": "application/json",
            }
        )

    def create_batch(self, payload):
        return self._request("POST", "/integration/v1/batches", json_payload=payload)

    def start_submission(self, batch_id):
        return self._request(
            "POST", "/integration/v1/submissions/{}/start".format(batch_id)
        )

    def get_batch(self, batch_id):
        return self._request("GET", "/integration/v1/batches/{}".format(batch_id))

    def _request(self, method, path, json_payload=None):
        url = "{}/{}".format(self.base_url, path.lstrip("/"))
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_payload,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise TriadeTransientError(
                "Falha de comunicacao com o TRIADE: {}".format(exc)
            )

        data = None
        if response.text:
            try:
                data = response.json()
            except ValueError:
                data = None

        return TriadeClientResponse(
            status_code=response.status_code,
            data=data,
            text=response.text,
        )
