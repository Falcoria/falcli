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

    # Transform to list of dicts with last_updated formatted
    ip_data = []
    for hostname, data in result["workers"].items():
        ip = data.get("ip", "unknown")
        last_updated = data.get("last_updated", 0)

        # Convert last_updated to readable time if > 0
        if last_updated:
            import time
            last_updated_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_updated))
        else:
            last_updated_str = "unknown"

        ip_data.append({
            "hostname": hostname,
            "ip": ip,
            "last_updated": last_updated_str
        })

    printer.print_model_table(WorkerIP, ip_data)
    print()