import sys
import time
from pathlib import Path

from pydantic import ValidationError
from rich.text import Text
from rich.live import Live
from io import StringIO

from app.connectors.tasker_connector import tasker
from app.utils.io_utils import load_yaml_file
from app.utils.printer import Printer
from app.messages.errors import Errors
from app.messages.info import Info
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
        response = tasker.stop_scan_nmap(project_id)
        if response.status_code == 200:
            try:
                return RevokeResponse.model_validate_json(response.text)
            except Exception as e:
                raise RuntimeError(Errors.General.PARSE_FAILED.format(error=e))
        raise RuntimeError(Errors.Scan.STOP_FAILED.format(project_id=project_id))

    @staticmethod
    def get_scan_status(project_id: str) -> ProjectTaskSummary:
        response = tasker.get_scan_status(project_id)
        if response.status_code == 200:
            return ProjectTaskSummary(**response.json())
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

    @staticmethod
    def interactive_scan_status(console, project_id: str, project_name: str, refresh_time: int):
        start_time = time.time()
        total_tasks = None

        with Live(console=console, refresh_per_second=4) as live:
            try:
                while True:
                    text, remaining = ScanService._generate_status_text(project_id, project_name, total_tasks, start_time)

                    if total_tasks is None:
                        total_tasks = remaining

                    if remaining == 0:
                        break  # Do not update, exit cleanly

                    live.update(Text(text))
                    time.sleep(refresh_time)
            except KeyboardInterrupt:
                Printer.warning("Stopped interactive status tracking.")

        final_text, _ = ScanService._generate_status_text(project_id, project_name, total_tasks, start_time, suppress_no_tasks=True)
        print(final_text)

    @staticmethod
    def static_scan_status(project_id: str, project_name: str):
        status = ScanService.get_scan_status(project_id)
        Printer.success(Info.Scan.STATUS_FETCHED.format(project_id=project_id, project_name=project_name or "-"))

        if status.active_or_queued == 0:
            Printer.plain(Info.Scan.NO_TASKS.format(project_name=project_name, project_id=project_id))
        else:
            Printer.task_summary_table(status)

    @staticmethod
    def _generate_status_text(project_id: str, project_name: str, total: int, start_time: float, suppress_no_tasks: bool = False):
        try:
            status = ScanService.get_scan_status(project_id)
        except RuntimeError as e:
            return f"[red]Error fetching status:[/red] {str(e)}", 0

        buffer = [Info.Scan.STATUS_FETCHED.format(project_id=project_id, project_name=project_name or "-")]

        if status.active_or_queued == 0:
            if not suppress_no_tasks:
                buffer.append(Info.Scan.NO_TASKS.format(project_name=project_name, project_id=project_id))
            return "\n".join(buffer), 0

        buffer.append("")

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        Printer.task_summary_table(status)

        sys.stdout = old_stdout
        buffer.append(mystdout.getvalue().rstrip())

        elapsed = int(time.time() - start_time) if start_time else 0
        buffer.append(f"\nRemaining: {status.active_or_queued}/{total or status.active_or_queued} | Elapsed: {elapsed}s")

        return "\n".join(buffer), status.active_or_queued
