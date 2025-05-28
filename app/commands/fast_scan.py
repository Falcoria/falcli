import typer
import uuid
from pathlib import Path
from typing import Optional

from app.memory import memory
from app.utils import printer
from app.messages import info, errors
from app.connectors.scanledger_connector import scanledger
from app.connectors.tasker_connector import tasker
from app.config import config
from app.schemas import ImportMode
from app.commands.scan import (
    load_scan_yaml,
    load_targets_from_file,
    display_scan_progress,
)
from app.commands.project import delete_project
from app.commands.ips import get_ip, list_ips



def generate_random_project_name() -> str:
    return f"autoproj-{uuid.uuid4().hex[:8]}"


def fast_scan(
    config_path: Path = typer.Option(Path("scan_configs/default.yaml"), "--config", "-c", help="Path to scan configuration YAML file"),
    targets_file: Optional[Path] = typer.Option(None, help="Path to file with target hosts (overrides hosts from config)"),
    hosts: Optional[str] = typer.Option(None, help="Comma-separated list of hosts to scan (overrides all other sources)"),
    from_config: bool = typer.Option(False, help="Use hosts from YAML config (required if not using --hosts or --targets-file)"),
    mode: Optional[ImportMode] = typer.Option(None, help="Import mode: insert, replace, update, or append"),
    refresh_time: int = typer.Option(1, help="Refresh interval in seconds"),
    format: str = typer.Option("xml", help="Report format (e.g., xml)"),
    delete: bool = typer.Option(False, "--delete", help="Delete the project after report is downloaded"),
):
    """Start a quick scan, track it, download report, and show IP table."""

    scan_request = load_scan_yaml(config_path)

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

    if mode:
        scan_request.mode = mode

    name = generate_random_project_name()
    try:
        project = scanledger.create_project(project_name=name)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(code=1)

    printer.success(info.Project.CREATED.format(name=name, id=project["id"]))

    try:
        response = tasker.start_scan_nmap(project["id"], scan_request.model_dump(exclude_unset=True))
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if response:
        printer.success(info.Scan.STARTED.format(project=project["id"]))
    else:
        printer.error(errors.Scan.START_FAILED.format(project=project["id"]))
        raise typer.Exit(1)

    elapsed = display_scan_progress(project["id"], refresh_time)

    # Reuse get_ip to print the IP table
    print()
    printer.header("Scanned IPs:")
    get_ip(ip=None, project_id=project["id"])
    

    printer.header("Summary:")
    list_ips(project_id=project["id"], skip=None, limit=None, has_ports=True)

    printer.plain(f"Total scan time: {elapsed} seconds")
    print()
    # Download report
    try:
        data = scanledger.download_ips(
            project["id"],
            skip=None,
            limit=None,
            has_ports=True,
            format=format,
        )
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if data is None:
        printer.error(errors.IP.FAILED_DOWNLOAD.format(project=project["id"]))
        raise typer.Exit(1)

    config.report_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.report_dir / f"{project['id']}_ips.{format}"
    with open(output_path, "wb") as f:
        f.write(data)

    printer.success(info.IPs.DOWNLOADED.format(project=project["id"]))
    printer.plain(f"Saved to: {output_path}")

    if delete:
        try:
            delete_project(project["id"])
        except RuntimeError as e:
            printer.error(str(e))
            raise typer.Exit(1)

    print()