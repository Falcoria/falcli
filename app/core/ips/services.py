from app.connectors.scanledger_connector import scanledger
from app.core.ips.models import IP
from app.core.common.enums import ImportMode, DownloadReportFormat
from app.config import load_config_safe
from pathlib import Path


class IpsService:
    @staticmethod
    def list_ips(project_id: str, skip: int | None = None, limit: int | None = None, has_ports: bool = True) -> list[IP]:
        response = scanledger.get_ips(project_id, skip=skip, limit=limit, has_ports=has_ports)
        raw_ips = response.json()
        return [IP.model_validate(ip) for ip in raw_ips]

    @staticmethod
    def create_ips(project_id: str, ip_list: list[dict]) -> list[IP] | None:
        response = scanledger.create_ips(project_id, ip_list)
        if response.status_code == 201:
            raw_ips = response.json()
            return [IP.model_validate(ip) for ip in raw_ips]
        return None

    @staticmethod
    def import_ips(project_id: str, file_path: str, mode: ImportMode) -> list[IP] | None:
        response = scanledger.import_ips(project_id, file_path, mode=mode.value)
        if response.status_code == 200:
            raw_ips = response.json()
            return [IP.model_validate(ip) for ip in raw_ips]
        return None

    @staticmethod
    def download_ips(project_id: str, skip: int | None, limit: int | None, has_ports: bool, format: DownloadReportFormat) -> bytes | None:
        response = scanledger.download_ips(project_id, skip=skip, limit=limit, has_ports=has_ports, report_format=format.value)
        if response.status_code == 200:
            return response.content
        return None

    @staticmethod
    def get_output_path(project_id: str, format: DownloadReportFormat, out: str | None) -> Path:
        config = load_config_safe()
        if not config:
            raise RuntimeError("Configuration not loaded.")

        if out:
            return Path(out)
        else:
            config.report_dir.mkdir(parents=True, exist_ok=True)
            return config.report_dir / f"{project_id}_ips.{format.value}"

    @staticmethod
    def delete_ip(project_id: str, ip: str) -> bool:
        response = scanledger.delete_ip(project_id, ip)
        return response.status_code == 204

    @staticmethod
    def delete_all_ips(project_id: str) -> bool:
        response = scanledger.delete_ips(project_id)
        return response.status_code == 204

    @staticmethod
    def get_ip(project_id: str, ip: str) -> IP | None:
        response = scanledger.get_ip(project_id, ip)
        if response.status_code == 200:
            return IP.model_validate(response.json())
        return None
