import typer
from app.utils.printer import Printer
from app.messages.info import Info
from app.messages.errors import Errors
from app.messages.confirmations import CONFIRMATIONS
from app.core.ips.services import IpsService
from app.core.common.enums import ImportMode, DownloadReportFormat
from app.utils.context import get_current_project_id
from app.core.project.services import ProjectService
from app.core.profile.services import ProfileService


ips_app = typer.Typer(no_args_is_help=True)


@ips_app.command("list", help="List all IPs in the current project")
def list_ips(project_id: str = typer.Option(None), skip: int = typer.Option(None), limit: int = typer.Option(None), has_ports: bool = typer.Option(True)):
    project_id = get_current_project_id(project_id)
    project = ProfileService.get_project_by_id(project_id)

    ips = IpsService.list_ips(project_id, skip, limit, has_ports)
    if not ips:
        Printer.warning(Info.IPs.NO_IPS_FOUND.format(project_id=project_id, project_name=project.name))
        return
    
    Printer.print_active_project(project)
    print()
    rows = [(ip.ip, len(ip.ports or [])) for ip in ips]
    Printer.column_table(["ip", "port_count"], rows)
    print()


@ips_app.command("create", help="Create new IPs in the current project")
def create_ips(ip: list[str] = typer.Option(...), project_id: str = typer.Option(None)):
    project_id = get_current_project_id(project_id)
    ip_list = [{"ip": addr} for addr in ip]
    result = IpsService.create_ips(project_id, ip_list)
    if result:
        Printer.success(Info.IPs.CREATED.format(count=len(result), project=project_id))
    else:
        Printer.error(Errors.IP.ADD_FAILED.format(ip=", ".join(ip), project=project_id))
    print()


@ips_app.command("import", help="Import IPs from a file into the current project")
def import_ips(file: str = typer.Option(..., "-f", "--file"), project_id: str = typer.Option(None), mode: ImportMode = typer.Option(ImportMode.INSERT)):
    project_id = get_current_project_id(project_id)
    project = ProfileService.get_project_by_id(project_id)
    result = IpsService.import_ips(project_id, file, mode)
    Printer.print_active_project(project)
    if result:
        Printer.plain(Info.IPs.IMPORTED.format(project=project_id, result=f"{len(result)} IP{'s' if len(result) != 1 else ''}"))
    elif result == []:
        Printer.plain(Info.IPs.NO_NEW_IPS.format(project=project_id))
    else:
        Printer.error(Errors.IP.ADD_FAILED.format(ip="*", project=project_id))
    print()


@ips_app.command("download", help="Download IPs report in the specified format")
def download_ips(
    format: DownloadReportFormat = typer.Option(DownloadReportFormat.XML),
    skip: int = typer.Option(None),
    limit: int = typer.Option(None),
    has_ports: bool = typer.Option(True),
    project_id: str = typer.Option(None),
    out: str = typer.Option(None, help="Optional path to save the downloaded report"),
):
    project_id = get_current_project_id(project_id)
    project = ProfileService.get_project_by_id(project_id)
    Printer.print_active_project(project)
    try:
        data = IpsService.download_ips(project_id, skip, limit, has_ports, format)
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    if data is None:
        Printer.error(Errors.IP.FAILED_DOWNLOAD.format(project=project_id))
        raise typer.Exit(1)

    try:
        final_path = IpsService.get_output_path(project_id, format, out)
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    final_path.parent.mkdir(parents=True, exist_ok=True)

    with open(final_path, "wb") as f:
        f.write(data)

    Printer.success(Info.IPs.DOWNLOADED.format(project=project_id))
    Printer.plain(Info.General.SAVED_TO.format(path=final_path))
    print()


@ips_app.command("delete", help="Delete specific IP or all IPs in the current project")
def delete_ips(ip: str = typer.Argument(None), project_id: str = typer.Option(None)):
    project_id = get_current_project_id(project_id)
    project = ProfileService.get_project_by_id(project_id)
    Printer.print_active_project(project)
    if ip:
        success = IpsService.delete_ip(project_id, ip)
        if success:
            Printer.success(Info.IPs.DELETED.format(project=project_id))
        else:
            Printer.error(Errors.IP.DELETE_FAILED.format(ip=ip, project=project_id))
        return
    # Delete ALL
    confirm = typer.confirm(CONFIRMATIONS.GENERAL.DELETE_ALL_IPS.format(project_id=project_id), default=False)
    if not confirm:
        Printer.plain(Info.General.ABORTED)
        raise typer.Exit(0)
    success = IpsService.delete_all_ips(project_id)
    if success:
        Printer.success(Info.IPs.DELETED.format(project=project_id))
    else:
        Printer.error(Errors.IP.DELETE_FAILED.format(ip="*", project=project_id))
        raise typer.Exit(1)
    

@ips_app.command("get", help="Get details of a specific IP in the current project")
def get_ip(ip: str = typer.Argument(None), project_id: str = typer.Option(None), has_ports: bool = typer.Option(True)):
    project_id = get_current_project_id(project_id)
    project = ProfileService.get_project_by_id(project_id)
    Printer.print_active_project(project)
    if ip:
        ip_obj = IpsService.get_ip(project_id, ip)
        if not ip_obj:
            Printer.error(Errors.IP.NOT_FOUND.format(ip=ip))
            raise typer.Exit(1)
        Printer.key_value_table(ip_obj)
        return
    # List all IPs
    ips = IpsService.list_ips(project_id, skip=None, limit=None, has_ports=has_ports)
    if not ips:
        Printer.warning(Info.IPs.NO_IPS_FOUND.format(project_id=project_id, project_name=project.name))
        return
    Printer.grouped_ip_table(ips)
