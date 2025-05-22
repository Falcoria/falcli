import typer

from app.connectors.tasker_connector import tasker
from app.utils import printer
from app.schemas import WorkerIP
from app.messages import errors


workers_app = typer.Typer(no_args_is_help=True)



@workers_app.command("ips")
def list_worker_ips():
    """List external IP addresses of all active workers."""
    try:
        result = tasker.get_workers_ips()
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(code=1)

    if not result or "workers" not in result:
        printer.error(errors.Worker.FAILED_TO_GET_IPS)
        raise typer.Exit(code=1)

    # Transform to list of dicts
    ip_data = [
        {"hostname": hostname, "ip": ip}
        for hostname, ip in result["workers"].items()
    ]

    printer.print_model_table(WorkerIP, ip_data)