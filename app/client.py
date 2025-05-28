import typer
from typing import Optional

from app.__version__ import __version__
from app.commands.project import project_app
from app.commands.config import config_app
from app.commands.memory import memory_app
from app.commands.scan import scan_app
from app.commands.workers import workers_app
from app.commands.fast_scan import fast_scan

def version_callback(value: bool):
    if value:
        typer.echo(f"Falcon CLI version: {__version__}")
        raise typer.Exit()


app = typer.Typer(no_args_is_help=True)

# Correct way to add the --version option
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    )
):
    pass


app.add_typer(project_app, name="project", help="Manage projects and IP data.")
app.add_typer(config_app, name="config", help="Configure CLI settings and backend URLs.")
app.add_typer(memory_app, name="memory", help="View or clear stored memory state.")
app.add_typer(scan_app, name="scan", help="Start, stop, or preview scans.")
app.add_typer(workers_app, name="workers", help="Manage worker nodes and their IPs.")
app.command("fast-scan", help="Start a quick scan, track it, and download report")(fast_scan)