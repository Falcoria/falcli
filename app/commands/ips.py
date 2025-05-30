import typer

from app.connectors.scanledger_connector import scanledger
from app.memory import memory
from app.messages import errors, info
from app.utils import printer
from app.config import config
from app.schemas import ImportMode, IP

ips_app = typer.Typer(no_args_is_help=True)

# ─────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────

@ips_app.command("list")
def list_ips(
    project_id: str = typer.Option(None, help="Project ID (default: last used)"),
    skip: int = typer.Option(None, help="Skip records"),
    limit: int = typer.Option(None, help="Limit number of records"),
    has_ports: bool = typer.Option(True, help="Only IPs with ports")
):
    """List IPs in the project."""
    project_id = project_id or memory.get_last_project_id()
    if not project_id:
        printer.error(errors.Project.ID_REQUIRED)
        raise typer.Exit(1)

    try:
        raw_ips = scanledger.get_ips(project_id, skip=skip, limit=limit, has_ports=has_ports)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if not raw_ips:
        printer.warning(info.IPs.FETCHED.format(project=project_id) + " No IPs found.")
        print()
        return

    ips = [IP.model_validate(ip) for ip in raw_ips]
    rows = [(ip.ip, len(ip.ports or [])) for ip in ips]
    printer.column_table(["ip", "port_count"], rows)
    print()


#@ips_app.command("create")
def create_ips(
    ip: list[str] = typer.Option(..., help="IP(s) to add", prompt=True),
    project_id: str = typer.Option(None, help="Project ID (default: last used)")
):
    """Add new IPs to the project."""
    project_id = project_id or memory.get_last_project_id()
    if not project_id:
        printer.error(errors.Project.ID_REQUIRED)
        raise typer.Exit()

    ip_list = [{"ip": addr} for addr in ip]
    result = scanledger.create_ips(project_id, ip_list)
    if result:
        printer.success(info.IPs.CREATED.format(count=len(result), project=project_id))
    else:
        printer.error(errors.IP.ADD_FAILED.format(ip=", ".join(ip), project=project_id))
    print()


@ips_app.command("import")
def import_ips(
    file: str = typer.Option(..., "-f", "--file", help="Path to Nmap XML report"),
    project_id: str = typer.Option(None, help="Project ID (default: last used)"),
    mode: ImportMode = typer.Option(
        ImportMode.INSERT,
        help="Import mode: insert, replace, update, or append"
    )
):
    """Import IPs from an Nmap XML report."""
    project_id = project_id or memory.get_last_project_id()
    if not project_id:
        printer.error(errors.Project.ID_REQUIRED)
        raise typer.Exit(1)

    try:
        result = scanledger.import_ips(project_id, file, mode=mode.value)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if result:
        printer.plain(
            info.IPs.IMPORTED.format(
                project=project_id,
                result=f"{len(result)} IP{'s' if len(result) != 1 else ''}"
            )
        )
    elif result == []:
        printer.plain(info.IPs.NO_NEW_IPS.format(project=project_id))
    else:
        printer.error(errors.IP.ADD_FAILED.format(ip="*", project=project_id))

    print()


@ips_app.command("download")
def download_ips(
    format: str = typer.Option("xml", help="Format: xml"),
    skip: int = typer.Option(None, help="Skip records"),
    limit: int = typer.Option(None, help="Limit number of records"),
    has_ports: bool = typer.Option(True, help="Only IPs with ports"),
    project_id: str = typer.Option(None, help="Project ID (default: last used)")
):
    """Download IPs report and save to scan_reports directory."""
    project_id = project_id or memory.get_last_project_id()
    if not project_id:
        printer.error(errors.Project.ID_REQUIRED)
        raise typer.Exit(1)

    try:
        data = scanledger.download_ips(
            project_id,
            skip=skip,
            limit=limit,
            has_ports=has_ports,
            format=format
        )
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if data is None:
        printer.error(errors.IP.FAILED_DOWNLOAD.format(project=project_id))
        raise typer.Exit(1)

    config.report_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.report_dir / f"{project_id}_ips.{format}"

    with open(output_path, "wb") as f:
        f.write(data)

    printer.success(info.IPs.DOWNLOADED.format(project=project_id))
    printer.plain(f"Saved to: {output_path}")
    print()


@ips_app.command("delete")
def delete_ips(
    ip: str = typer.Argument(None, help="IP address to delete. If omitted, deletes ALL IPs."),
    project_id: str = typer.Option(None, help="Project ID")
):
    """
    Delete a specific IP or all IPs from a project.
    """
    project_id = project_id or memory.get_last_project_id()

    if not project_id:
        msg = (
            errors.Project.ID_REQUIRED
            if ip else errors.Project.PROJECT_ID_REQUIRED
        )
        printer.error(msg)
        raise typer.Exit(1)

    if ip:
        try:
            result = scanledger.delete_ip(project_id, ip)
        except RuntimeError as e:
            printer.error(errors.IP.DELETE_FAILED.format(ip=ip, project=project_id))
            raise typer.Exit(1)

        if result is None or result == 204:
            printer.success(info.IPs.DELETED.format(ip=ip, project=project_id))
        return

    # --- Delete ALL ---
    confirm = typer.confirm(f"Are you sure you want to delete ALL IPs from project {project_id}?")
    if not confirm:
        printer.plain("Aborted.")
        raise typer.Exit(0)

    try:
        result = scanledger.delete_ips(project_id)
    except RuntimeError as e:
        printer.error(errors.IP.DELETE_FAILED.format(ip="*", project=project_id))
        raise typer.Exit(1)

    if result.status_code == 204:
        printer.success(info.IPs.DELETED.format(project=project_id))
    else:
        printer.error(errors.IP.DELETE_FAILED.format(ip="*", project=project_id))
        raise typer.Exit(1)


@ips_app.command("get")
def get_ip(
    ip: str = typer.Argument(None, help="IP address to get. If omitted, lists all IPs."),
    project_id: str = typer.Option(None, help="Project ID (default: last used)"),
    has_ports: bool = typer.Option(True, help="Only IPs with ports")
):
    """
    Get a specific IP or list all IPs from a project.
    """
    project_id = project_id or memory.get_last_project_id()
    if not project_id:
        printer.error(errors.Project.ID_REQUIRED)
        raise typer.Exit(1)

    if ip:
        try:
            ip_data = scanledger.get_ip(project_id, ip)
        except RuntimeError as e:
            printer.error(str(e))
            raise typer.Exit(1)

        if not ip_data:
            printer.error(errors.IP.NOT_FOUND.format(ip=ip))
            raise typer.Exit(1)

        parsed = IP.model_validate(ip_data)
        printer.key_value_table(parsed)
        return

    try:
        raw_ips = scanledger.get_ips(project_id, skip=None, limit=None, has_ports=has_ports)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if not raw_ips:
        printer.plain(info.IPs.NO_IPS_FOUND.format(project=project_id))
        return

    ips = [IP.model_validate(ip) for ip in raw_ips]
    printer.grouped_ip_table(ips)