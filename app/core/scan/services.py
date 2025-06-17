from pathlib import Path
from pydantic import ValidationError

from app.connectors.tasker_connector import tasker
from app.utils.io_utils import load_yaml_file
from app.utils.printer import Printer
from app.messages.errors import Errors
from app.core.scan.models import RunNmapRequest, ScanStartResponse, ProjectTaskSummary, RevokeResponse


class ScanService:
    @staticmethod
    def start_scan(project_id: str, run_nmap_payload: dict) -> ScanStartResponse:
        response_data = tasker.start_scan_nmap(project_id, run_nmap_payload)

        if not response_data:
            raise RuntimeError(f"Scan start failed for project {project_id} — no response.")

        try:
            return ScanStartResponse(**response_data.json())
        except Exception as e:
            Printer.error(Errors.Scan.START_FAILED.format(error=e))
            raise RuntimeError("Failed to parse scan start response.")

    @staticmethod
    def stop_scan(project_id: str) -> RevokeResponse:
        try:
            response = tasker.stop_scan_nmap(project_id)
        except RuntimeError as e:
            raise RuntimeError(str(e))

        if response.status_code == 200:
            try:
                return RevokeResponse.model_validate_json(response.text)
            except Exception as e:
                raise RuntimeError(Errors.General.PARSE_FAILED.format(error=e))
        else:
            raise RuntimeError(Errors.Scan.STOP_FAILED.format(project_id=project_id))

    @staticmethod
    def get_scan_status(project_id: str) -> ProjectTaskSummary:
        response = tasker.get_scan_status(project_id)

        if response.status_code == 200:
            return ProjectTaskSummary(**response.json())
        else:
            Printer.error(Errors.Scan.START_FAILED.format(project=project_id))
            raise RuntimeError(Errors.Scan.GET_STATUS_FAILED.format(project=project_id))

    @staticmethod
    def load_scan_yaml(config_path: Path, override_hosts: list[str] | None = None) -> RunNmapRequest:
        if not config_path.exists():
            Printer.error(Errors.Scan.CONFIG_NOT_FOUND.format(path=config_path))
            raise SystemExit(1)

        try:
            yaml_data = load_yaml_file(config_path)
        except Exception as e:
            Printer.error(Errors.Scan.CONFIG_READ_FAILED.format(error=e))
            raise SystemExit(1)

        if override_hosts:
            yaml_data["hosts"] = override_hosts

        try:
            return RunNmapRequest(**yaml_data)
        except ValidationError as e:
            Printer.error(Errors.Scan.CONFIG_VALIDATION_FAILED.format(error=e))
            raise SystemExit(1)

