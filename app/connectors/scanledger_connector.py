import requests
from app.config import config
from app.connectors.base import BaseConnector
from app.schemas import DownloadReportFormat

ROUTES = {
    "projects": "projects",
    "project_detail": "projects/{project_id}",
    "project_ips_download": "projects/{project_id}/ips/download",
    "project_files": "projects/{project_id}/upload",
    "ips_list": "projects/{project_id}/ips",
    "ips_import": "projects/{project_id}/ips/import",
    "ips_download": "projects/{project_id}/ips/download",
    "ip_detail": "projects/{project_id}/ips/{ip_address}",
}


class ScanledgerConnector(BaseConnector):
    """ScanledgerConnector class to handle HTTP requests to ScanLedger backend."""

    def __init__(self, backend_base_url: str, auth_token: str):
        super().__init__(backend_base_url, auth_token)

    # --- PROJECT methods ---

    def create_project(self, project_name: str):
        response = self.make_request(
            ROUTES["projects"],
            method="POST",
            json_body={"project_name": project_name}
        )
        return self._handle_response(response)

    def get_projects(self):
        response = self.make_request(ROUTES["projects"])
        return self._handle_response(response)

    def get_project(self, project_id: str):
        endpoint = ROUTES["project_detail"].format(project_id=project_id)
        response = self.make_request(endpoint)
        return self._handle_response(response)

    def delete_project(self, project_id: str) -> requests.Response:
        endpoint = ROUTES["project_detail"].format(project_id=project_id)
        return self.make_request(endpoint, method="DELETE")

    # --- IP methods ---

    def get_ips(self, project_id: str, skip: int = None, limit: int = None, has_ports: bool = True):
        query = {"skip": skip, "limit": limit, "has_ports": has_ports}
        endpoint = ROUTES["ips_list"].format(project_id=project_id)
        response = self.make_request(endpoint, query_params=query)
        return self._handle_response(response)

    def create_ips(self, project_id: str, ip_list: list, mode: str = "insert"):
        endpoint = ROUTES["ips_list"].format(project_id=project_id)
        response = self.make_request(
            endpoint,
            method="POST",
            json_body={"new_ips": ip_list, "mode": mode}
        )
        return self._handle_response(response)

    def delete_ips(self, project_id: str) -> requests.Response:
        endpoint = ROUTES["ips_list"].format(project_id=project_id)
        return self.make_request(endpoint, method="DELETE")

    def import_ips(self, project_id: str, file_path: str, mode: str = "insert"):
        endpoint = ROUTES["ips_import"].format(project_id=project_id)
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = self.make_request(
                endpoint,
                method="POST",
                query_params={"mode": mode},
                files=files
            )
        return self._handle_response(response)

    def download_ips(
        self,
        project_id: str,
        skip: int = None,
        limit: int = None,
        has_ports: bool = True,
        format: str = DownloadReportFormat.XML.value
    ):
        query = {
            "skip": skip,
            "limit": limit,
            "has_ports": has_ports,
            "format": format
        }
        endpoint = ROUTES["ips_download"].format(project_id=project_id)
        response = self.make_request(endpoint, query_params=query)
        return self._handle_response(response, return_content=True)

    def get_ip(self, project_id: str, ip_address: str):
        endpoint = ROUTES["ip_detail"].format(
            project_id=project_id,
            ip_address=ip_address
        )
        response = self.make_request(endpoint)
        return self._handle_response(response)

    def update_ip(self, project_id: str, ip_address: str, update_fields: dict):
        endpoint = ROUTES["ip_detail"].format(
            project_id=project_id,
            ip_address=ip_address
        )
        response = self.make_request(
            endpoint,
            method="PUT",
            json_body=update_fields
        )
        return self._handle_response(response)

    def delete_ip(self, project_id: str, ip_address: str) -> requests.Response:
        endpoint = ROUTES["ip_detail"].format(
            project_id=project_id,
            ip_address=ip_address
        )
        return self.make_request(endpoint, method="DELETE")


# --- Global connector instance ---

scanledger = ScanledgerConnector(
    backend_base_url=config.backend_base_url,
    auth_token=config.token
)
