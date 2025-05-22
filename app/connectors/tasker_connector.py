from app.config import config
from app.connectors.base import BaseConnector

# --- Centralized ROUTES ---

ROUTES = {
    "stop_scan_nmap": "tasks/{project_id}/stop-nmap",
    "get_scan_status": "tasks/{project_id}/status",
    "start_scan_nmap": "tasks/{project_id}/run-nmap",
    "get_workers_ips": "workers/ips",
}


class TaskerConnector(BaseConnector):
    """TaskerConnector class to handle HTTP requests to Tasker backend."""

    def __init__(self, backend_base_url: str, auth_token: str):
        super().__init__(backend_base_url, auth_token)

    # --- API methods ---

    def stop_scan_nmap(self, project_id: str):
        endpoint = ROUTES["stop_scan_nmap"].format(project_id=project_id)
        response = self.make_request(endpoint, method="GET")
        return self._handle_response(response)

    def get_scan_status(self, project_id: str):
        endpoint = ROUTES["get_scan_status"].format(project_id=project_id)
        response = self.make_request(endpoint, method="GET")
        return self._handle_response(response)

    def start_scan_nmap(self, project_id: str, data: dict):
        endpoint = ROUTES["start_scan_nmap"].format(project_id=project_id)
        response = self.make_request(
            endpoint,
            method="POST",
            json_body=data
        )
        return self._handle_response(response)

    def get_workers_ips(self):
        endpoint = ROUTES["get_workers_ips"]
        response = self.make_request(endpoint, method="GET")
        return self._handle_response(response)


# --- Global instance ---

tasker = TaskerConnector(
    backend_base_url=config.tasker_base_url,
    auth_token=config.token
)
