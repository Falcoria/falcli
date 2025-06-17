import typer

from app.core.workers.services import get_workers_ips
from app.utils.printer import Printer
from app.messages.errors import Errors
from app.messages.info import Info
from app.core.workers.models import WorkerIPView


workers_app = typer.Typer(no_args_is_help=True)


@workers_app.command("ips", help="List external IP addresses of all active workers.")
def list_worker_ips():
    """List external IP addresses of all active workers."""
    try:
        ip_data = get_workers_ips()
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(code=1)

    if not ip_data:
        Printer.error(Errors.Worker.FAILED_TO_GET_IPS)
        raise typer.Exit(code=1)

    Printer.success(Info.Worker.FETCHED_WORKER_IPS)
    view_data = [WorkerIPView.from_worker_ip(ip) for ip in ip_data]

    Printer.print_model_table(WorkerIPView, [ip.model_dump() for ip in view_data])
    print()

    # Add summary line:
    Printer.plain(f"{len(ip_data)} workers online.")
