import requests
import time
import urllib3
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseConnector:
    """Base class for all connectors to provide request handling."""

    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})

    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        query_params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        timeout: int = 60,
        files=None,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> requests.Response:
        """Perform HTTP request with retries. Raise RuntimeError on failure."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(1, max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=query_params,
                    json=json_body,
                    files=files,
                    timeout=timeout,
                    verify=False
                )

                response.raise_for_status()
                return response

            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt == max_retries:
                    raise RuntimeError(f"Request failed after {max_retries} retries: {e}") from e
                time.sleep(retry_delay)

            except requests.HTTPError as e:
                raise RuntimeError(f"HTTP {e.response.status_code}: {e.response.text}") from e

            except requests.RequestException as e:
                raise RuntimeError(f"Request failed: {e}") from e

            except Exception as e:
                raise RuntimeError(f"Unexpected error during request: {e}") from e