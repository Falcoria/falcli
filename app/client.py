import typer

from app.commands.project import project_app
from app.commands.config import config_app
from app.commands.memory import memory_app
from app.commands.scan import scan_app
from app.commands.workers import workers_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(project_app, name="project", help="Manage projects and IP data.")
app.add_typer(config_app, name="config", help="Configure CLI settings and backend URLs.")
app.add_typer(memory_app, name="memory", help="View and modify stored memory (e.g., last used project).")
app.add_typer(scan_app, name="scan", help="Start, stop, and preview Nmap scans.")
app.add_typer(workers_app, name="workers", help="Manage worker nodes and their IPs.")

