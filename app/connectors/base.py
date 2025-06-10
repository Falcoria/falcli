import requests
import urllib3

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
        query_params: dict = None,
        json_body: dict = None,
        timeout: int = 60,
        files=None
    ):
        """Perform HTTP request. Raise RuntimeError on failure."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method in ["GET", "DELETE"]:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=query_params,
                    timeout=timeout,
                    verify=False
                )
            elif files is not None:
                response = self.session.post(
                    url=url,
                    files=files,
                    params=query_params,
                    timeout=timeout,
                    verify=False
                )
            elif method in ["POST", "PUT"]:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=query_params,
                    json=json_body,
                    timeout=timeout,
                    verify=False
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response

        except requests.ConnectionError as e:
            raise RuntimeError(f"Server is unreachable: {e}") from e

        except requests.Timeout as e:
            raise RuntimeError(f"Request timed out: {e}") from e

        except requests.HTTPError as e:
            raise RuntimeError(f"HTTP {e.response.status_code}: {e.response.text}") from e

        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Unexpected error during request: {e}") from e

    def _handle_response(self, response, expect_json: bool = True, return_content: bool = False):
        if return_content:
            return response.content

        if not expect_json:
            return response.status_code

        try:
            return response.json()
        except Exception:
            return None
