from pathlib import Path
from typing import Optional, Annotated
import typer
from rich.console import Console
from rich.live import Live
from rich.text import Text
from datetime import datetime, timedelta, timezone
import time

from app.utils.printer import Printer
from app.messages.errors import Errors
from app.messages.info import Info
from app.core.scan.services import ScanService
from app.core.scan.models import ScanStartResponse
from app.core.common.enums import ImportMode
from app.core.profile.services import ProfileService
from app.utils.io_utils import load_lines_from_file
from app.config import config
from app.core.scan.enums import ScanCommands

scan_app = typer.Typer(no_args_is_help=True)
console = Console()

@scan_app.command(ScanCommands.START.value, help="Start a scan using a YAML config and optional target file or host list.")
def start_scan_cmd(
    config_path: Annotated[
        Path,
        typer.Option("-c", "--config", help="Path to scan configuration YAML file", show_default=True)
    ] = Path(config.scan_config_dir) / "default.yaml",

    targets_file: Optional[Path] = typer.Option(
        None,
        help="Path to file with target hosts (overrides hosts from config)"
    ),

    hosts: Optional[str] = typer.Option(
        None,
        help="Comma-separated list of hosts to scan (overrides all other sources)"
    ),

    from_config: bool = typer.Option(
        False,
        help="Explicitly use hosts from the YAML config (required if not using --hosts or --targets-file)"
    ),

    project_id: Optional[str] = typer.Option(
        None,
        help="UUID of the project to start the scan on (default: current project in profile)"
    ),

    mode: Optional[ImportMode] = typer.Option(
        None,
        help="Import mode: insert, replace, update, or append"
    )
):
    """Start a scan using a YAML config and optional target file or host list."""
    override_hosts = None
    if hosts:
        override_hosts = [h.strip() for h in hosts.split(",") if h.strip()]
    elif targets_file:
        try:
            override_hosts = load_lines_from_file(targets_file)
        except FileNotFoundError:
            Printer.error(Errors.Scan.TARGETS_FILE_NOT_FOUND.format(path=targets_file))
            raise typer.Exit(1)
    elif not from_config:
        Printer.error(Errors.Scan.NO_HOSTS_PROVIDED)
        raise typer.Exit(1)

    scan_request = ScanService.load_scan_yaml(config_path, override_hosts)

    if not scan_request.hosts:
        Printer.error(Errors.Scan.NO_TARGETS_FOUND)
        raise typer.Exit(1)

    if mode:
        scan_request.mode = mode

    if not project_id:
        project = ProfileService.get_saved_project()
        if not project:
            Printer.error(Errors.Project.ID_REQUIRED)
            raise typer.Exit(1)
        project_id = project.project_id
        project_name = project.name
    else:
        project = ProfileService.get_project_by_id(project_id)
        project_name = project.name if project else None

    try:
        response: ScanStartResponse = ScanService.start_scan(
            project_id, scan_request.model_dump(exclude_unset=True)
        )
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    Printer.success(Info.Scan.TARGETS_SENT.format(project_name=project_name, project_id=project_id))
    Printer.scan_start_header(scan_request, project_id, str(config_path))
    Printer.scan_summary_table(response.summary)
    print()

@scan_app.command(ScanCommands.STOP.value, help="Stop an ongoing scan for the given project.")
def stop_scan(
    project_id: Optional[str] = typer.Argument(
        None, help="UUID of the project to stop the scan for (default: from active profile)"
    )
):
    """Stop an ongoing scan for the given project."""
    if not project_id:
        project = ProfileService.get_saved_project()
        if not project:
            Printer.error(Errors.Project.ID_REQUIRED)
            raise typer.Exit(1)
        project_id = project.project_id
        project_name = project.name
    else:
        project = ProfileService.get_project_by_id(project_id)
        project_name = project.name if project else None

    try:
        result = ScanService.stop_scan(project_id)
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    if result.status == "stopped":
        Printer.success(Info.Scan.STOP_SUCCESS.format(project_id=project_id, project_name=project_name or "-"))
        Printer.plain(Info.Scan.REVOKED_COUNT.format(count=result.revoked))
    else:
        Printer.warning(Info.Scan.NO_TASKS.format(project_id=project_id, project_name=project_name or "-"))
    print()

@scan_app.command(ScanCommands.STATUS.value, help="Check scan task status for the given project.")
def scan_status_cmd(
    project_id: Optional[str] = typer.Option(
        None, help="UUID of the project to check scan status for (default: current project in profile)"
    ),
    interactive: bool = typer.Option(False, "-i", "--interactive", help="Continuously refresh scan status"),
    refresh_time: int = typer.Option(5, help="Refresh interval in seconds (only for interactive mode)")
):
    """Check scan task status for the given project."""
    if not project_id:
        project = ProfileService.get_saved_project()
        if not project:
            Printer.error(Errors.Project.ID_REQUIRED)
            raise typer.Exit(1)
        project_id = project.project_id
        project_name = project.name
    else:
        project = ProfileService.get_project_by_id(project_id)
        project_name = project.name if project else None

    if interactive:
        ScanService.interactive_scan_status(console, project_id, project_name, refresh_time)
    else:
        ScanService.static_scan_status(project_id, project_name)