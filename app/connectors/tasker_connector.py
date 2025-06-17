import requests

from app.config import config
from app.connectors.base import BaseConnector


class TaskerConnector(BaseConnector):
    """Handles HTTP requests to the Tasker backend."""

    ROUTES = {
        "stop_scan_nmap": "tasks/{project_id}/stop-nmap",
        "get_scan_status": "tasks/{project_id}/status",
        "start_scan_nmap": "tasks/{project_id}/run-nmap",
        "get_workers_ips": "workers/ips",
    }

    def __init__(self, backend_base_url: str, auth_token: str):
        super().__init__(backend_base_url, auth_token)

    def stop_scan_nmap(self, project_id: str) -> requests.Response:
        endpoint = self.ROUTES["stop_scan_nmap"].format(project_id=project_id)
        return self.make_request(endpoint, method="GET")

    def get_scan_status(self, project_id: str) -> requests.Response:
        endpoint = self.ROUTES["get_scan_status"].format(project_id=project_id)
        return self.make_request(endpoint, method="GET")

    def start_scan_nmap(self, project_id: str, data: dict) -> requests.Response:
        endpoint = self.ROUTES["start_scan_nmap"].format(project_id=project_id)
        return self.make_request(
            endpoint,
            method="POST",
            json_body=data
        )

    def get_workers_ips(self) -> requests.Response:
        endpoint = self.ROUTES["get_workers_ips"]
        return self.make_request(endpoint, method="GET")


# Global connector instance

tasker = TaskerConnector(
    backend_base_url=config.tasker_base_url,
    auth_token=config.token
)
