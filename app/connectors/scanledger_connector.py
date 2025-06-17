import requests

from app.config import config
from app.connectors.base import BaseConnector
from app.core.common.enums import ImportMode


class ScanledgerConnector(BaseConnector):
    """Handles HTTP requests to the ScanLedger backend."""

    ROUTES = {
        "projects": "projects",
        "project_detail": "projects/{project_id}",
        "ips_list": "projects/{project_id}/ips",
        "ips_import": "projects/{project_id}/ips/import",
        "ips_download": "projects/{project_id}/ips/download",
        "ip_detail": "projects/{project_id}/ips/{ip_address}",
    }

    def __init__(self, backend_base_url: str, auth_token: str):
        super().__init__(backend_base_url, auth_token)

    def create_project(self, name: str) -> requests.Response:
        return self.make_request(
            self.ROUTES["projects"],
            method="POST",
            json_body={"project_name": name}
        )

    def get_projects(self) -> requests.Response:
        return self.make_request(self.ROUTES["projects"])

    def get_project(self, project_id: str) -> requests.Response:
        endpoint = self.ROUTES["project_detail"].format(project_id=project_id)
        return self.make_request(endpoint)

    def delete_project(self, project_id: str) -> requests.Response:
        endpoint = self.ROUTES["project_detail"].format(project_id=project_id)
        return self.make_request(endpoint, method="DELETE")

    def get_ips(
        self,
        project_id: str,
        skip: int | None = None,
        limit: int | None = None,
        has_ports: bool = True
    ) -> requests.Response:
        query = {"skip": skip, "limit": limit, "has_ports": has_ports}
        endpoint = self.ROUTES["ips_list"].format(project_id=project_id)
        return self.make_request(endpoint, query_params=query)

    def create_ips(self, project_id: str, ip_list: list[dict], mode: str = ImportMode.INSERT.value) -> requests.Response:
        endpoint = self.ROUTES["ips_list"].format(project_id=project_id)
        return self.make_request(
            endpoint,
            method="POST",
            json_body={"new_ips": ip_list, "mode": mode}
        )

    def delete_ips(self, project_id: str) -> requests.Response:
        endpoint = self.ROUTES["ips_list"].format(project_id=project_id)
        return self.make_request(endpoint, method="DELETE")

    def import_ips(self, project_id: str, file_path: str, mode: str = ImportMode.INSERT.value) -> requests.Response:
        endpoint = self.ROUTES["ips_import"].format(project_id=project_id)
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self.make_request(
                endpoint,
                method="POST",
                query_params={"mode": mode},
                files=files
            )

    def download_ips(
        self,
        project_id: str,
        skip: int | None = None,
        limit: int | None = None,
        has_ports: bool = True,
        report_format: str = "xml"
    ) -> requests.Response:
        query = {
            "skip": skip,
            "limit": limit,
            "has_ports": has_ports,
            "format": report_format
        }
        endpoint = self.ROUTES["ips_download"].format(project_id=project_id)
        return self.make_request(endpoint, query_params=query)

    def get_ip(self, project_id: str, ip: str) -> requests.Response:
        endpoint = self.ROUTES["ip_detail"].format(
            project_id=project_id,
            ip_address=ip
        )
        return self.make_request(endpoint)

    def update_ip(self, project_id: str, ip: str, update_fields: dict) -> requests.Response:
        endpoint = self.ROUTES["ip_detail"].format(
            project_id=project_id,
            ip_address=ip
        )
        return self.make_request(
            endpoint,
            method="PUT",
            json_body=update_fields
        )

    def delete_ip(self, project_id: str, ip: str) -> requests.Response:
        endpoint = self.ROUTES["ip_detail"].format(
            project_id=project_id,
            ip_address=ip
        )
        return self.make_request(endpoint, method="DELETE")


# Global connector instance

scanledger = ScanledgerConnector(
    backend_base_url=config.scanledger_base_url,
    auth_token=config.token
)
