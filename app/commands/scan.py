import time
from pathlib import Path
from typing import Optional, Annotated
from itertools import cycle

import yaml
import typer
from rich.progress import Progress
from rich.live import Live
from rich.text import Text
from pydantic import ValidationError

from app.memory import memory
from app.connectors.tasker_connector import tasker
from app.utils import printer
from app.messages import info, errors

from app.schemas import RunNmapRequest, OpenPortsOpts, ServiceOpts, ImportMode, PreparedTarget

scan_app = typer.Typer(no_args_is_help=True)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def process_scan_response(response: dict[str, dict]):
    sent_ips = [(ip, target.get("hostnames", [])) for ip, target in response.items() if target.get("valid")]
    failed_ips = [(ip, target.get("reason") or "unknown") for ip, target in response.items() if not target.get("valid")]

    if sent_ips:
        printer.success("Sent to scan:")
        for ip, hostnames in sent_ips:
            if hostnames:
                print(f"  - {ip} ({', '.join(hostnames)})")
            else:
                print(f"  - {ip}")
    else:
        printer.warning("No targets were accepted for scanning.")

    if failed_ips:
        printer.warning("Rejected targets:")
        for ip, reason in failed_ips:
            print(f"  - {ip} (reason: {reason})")
        
        return False

    return True


def load_targets_from_file(file_path: Path) -> list[str]:
    if not file_path.exists():
        printer.error(errors.Scan.TARGETS_FILE_NOT_FOUND.format(path=file_path))
        raise typer.Exit(1)
    with file_path.open("r") as f:
        return [line.strip() for line in f if line.strip()]


def load_scan_yaml(config_path: Path) -> RunNmapRequest:
    if not config_path.exists():
        printer.error(errors.Scan.CONFIG_NOT_FOUND.format(path=config_path))
        raise typer.Exit(1)

    try:
        with config_path.open("r") as f:
            yaml_data = yaml.safe_load(f)
    except Exception as e:
        printer.error(errors.Scan.CONFIG_READ_FAILED.format(error=e))
        raise typer.Exit(1)

    try:
        scan = RunNmapRequest(**yaml_data)
    except ValidationError as e:
        printer.error(errors.Scan.CONFIG_VALIDATION_FAILED.format(error=e))
        raise typer.Exit(1)

    if scan.hosts_file and not scan.hosts:
        file_path = Path(scan.hosts_file)
        if not file_path.exists():
            printer.error(errors.Scan.TARGETS_FILE_NOT_FOUND.format(path=file_path))
            raise typer.Exit(1)
        with file_path.open("r") as f:
            scan.hosts = [line.strip() for line in f if line.strip()]
        if not scan.hosts:
            printer.error(errors.Scan.NO_TARGETS_FOUND)
            raise typer.Exit(1)

    return scan


def get_project_id() -> str:
    project_id = memory.get_last_project_id()
    if not project_id:
        printer.error(errors.Project.ID_REQUIRED)
        raise typer.Exit(1)
    return project_id


def display_scan_progress(project_id: str, refresh_time: int) -> int:
    try:
        initial = tasker.get_scan_status(project_id).get("active_or_queued", 0)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if initial == 0:
        printer.plain("No active or queued scans found.")
        raise typer.Exit(0)

    total = initial or 1
    current = initial
    spinner = cycle(["[/]", "[-]", "[\\]", "[|]"])
    last_update = time.time()
    start_time = time.time()

    with Live(refresh_per_second=10) as live:
        while current > 0:
            now = time.time()

            if now - last_update >= refresh_time:
                try:
                    response = tasker.get_scan_status(project_id)
                    current = response.get("active_or_queued", 0)

                    if current == 0:
                        break
                except RuntimeError as e:
                    printer.error(str(e))
                    raise typer.Exit(1)
                last_update = now

            spin = next(spinner)
            elapsed = int(now - start_time)
            live.update(Text(f"{spin} Scanning: {current}/{total} remaining | elapsed: {elapsed}s"))
            time.sleep(0.17)

    elapsed = int(time.time() - start_time)
    printer.plain(f"Total scan time: {elapsed} seconds")
    return elapsed

# ─────────────────────────────────────────────────────────────
# CLI Commands
# ─────────────────────────────────────────────────────────────

@scan_app.command("start")
def start_scan(
    config_path: Annotated[
        Path,
        typer.Option("-c", "--config", help="Path to scan configuration YAML file", show_default=True)
    ] = Path("scan_configs/default.yaml"),

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
        help="UUID of the project to start the scan on (default: last used project)"
    ),

    mode: Optional[ImportMode] = typer.Option(
        None,
        help="Import mode: insert, replace, update, or append"
    )

):
    """Start a scan using a YAML config and optional target file or host list."""

    scan_request = load_scan_yaml(config_path)

    # Target resolution
    if hosts:
        scan_request.hosts = [h.strip() for h in hosts.split(",") if h.strip()]
    elif targets_file:
        scan_request.hosts = load_targets_from_file(targets_file)
    elif from_config:
        if not scan_request.hosts:
            printer.error(errors.Scan.NO_TARGETS_FOUND)
            raise typer.Exit(1)
    else:
        printer.error(errors.Scan.NO_HOSTS_PROVIDED)
        raise typer.Exit(1)

    if not scan_request.hosts:
        printer.error(errors.Scan.NO_TARGETS_FOUND)
        raise typer.Exit(1)

    # Attach import mode if provided
    if mode:
        scan_request.mode = mode

    project_id = project_id or get_project_id()
    if not project_id:
        printer.error("No project_id provided and no last project_id found in memory.")
        raise typer.Exit(1)

    try:
        response = tasker.start_scan_nmap(project_id, scan_request.model_dump(exclude_unset=True))
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if response:
        printer.success(info.Scan.TARGETS_SENT.format(project=project_id))

        # NEW PART → get workers count and print
        try:
            workers_result = tasker.get_workers_ips()
            if not workers_result or "workers" not in workers_result:
                worker_count = "unknown"
            else:
                worker_count = len(workers_result["workers"])
        except RuntimeError:
            worker_count = "unknown"

        # Print message with targets and workers count
        target_count = len(scan_request.hosts)


        # Process response as before
        result = process_scan_response(response)
        if not result:
            raise typer.Exit(1)
        print()
        printer.plain(
            f"Scan initiated: {target_count} targets, {worker_count} workers active. Processing started."
        )
    else:
        printer.error(errors.Scan.START_FAILED.format(project=project_id))

    print()


@scan_app.command("stop")
def stop_scan(
    project_id: Optional[str] = typer.Argument(
        None,
        help="UUID of the project to stop the scan for (default: last used project)"
    )
):
    """Stop an ongoing scan for the given project."""

    project_id = project_id or memory.get_last_project_id()
    if not project_id:
        printer.error("No project_id provided and no last project_id found in memory.")
        raise typer.Exit(1)
    
    try:
        response = tasker.stop_scan_nmap(project_id)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if response:
        printer.success(info.Scan.STOPPED.format(project=project_id))
    else:
        printer.error(errors.Scan.STOP_FAILED.format(project=project_id))
    print()


@scan_app.command("status")
def get_scan_status(
    project_id: Optional[str] = typer.Argument(None, help="UUID of the project (default: last used)"),
    refresh_time: int = typer.Option(5, help="Refresh interval in seconds"),
    interactive: bool = typer.Option(False, "-i", "--interactive", help="Track with progress bar (default: off)")
):
    """Get scan status with optional progress bar."""
    project_id = project_id or get_project_id()

    if interactive:
        display_scan_progress(project_id, refresh_time)
        printer.success(info.Scan.COMPLETED.format(project=project_id))
    else:
        try:
            response = tasker.get_scan_status(project_id)
        except RuntimeError as e:
            printer.error(str(e))
            raise typer.Exit(1)

        if response:
            value = response.get("active_or_queued", "Unknown")
            printer.success(info.Scan.STATUS.format(project=project_id, status=value))
        else:
            printer.error(errors.Scan.STATUS_FAILED.format(project=project_id))

    print()


@scan_app.command("preview")
def preview_scan(
    config_path: Annotated[
        Path,
        typer.Option("-c", "--config", help="Path to scan configuration YAML file", show_default=True)
    ] = Path("scan_configs/default.yaml")
):
    """Preview the final Nmap commands (open ports and service discovery) for the given YAML config."""
    scan_request = load_scan_yaml(config_path)
    cmds = scan_request.to_nmap_commands()

    printer.plain(info.Other.OPEN_PORTS_CMD)
    printer.plain(cmds["open_ports_command"])
    print()

    printer.plain(info.Other.SERVICE_CMD)
    printer.plain(cmds["service_command"])
    print()


@scan_app.command("options")
def show_scan_options():
    """List all available scan options and their descriptions."""
    printer.success("Available Scan Options:")

    printer.header(info.Other.OPEN_PORTS_CMD)
    open_ports_dict = {
        field_name: f"{field.description or 'No description'} | Default: {field.default if field.default is not None else 'None'}"
        for field_name, field in OpenPortsOpts.model_fields.items()
    }
    printer.key_value_table(open_ports_dict)

    printer.header(info.Other.SERVICE_CMD)
    service_dict = {
        field_name: f"{field.description or 'No description'} | Default: {field.default if field.default is not None else 'None'}"
        for field_name, field in ServiceOpts.model_fields.items()
        if not field.exclude
    }
    printer.key_value_table(service_dict)

    print()
