import typer

from app.cli.profile import profile_app
from app.cli.project import project_app
from app.cli.workers import workers_app
from app.cli.scan import scan_app


app = typer.Typer(no_args_is_help=True)


app.add_typer(profile_app, name="profile", help="Manage Falcoria profiles")
app.add_typer(project_app, name="project", help="Manage Falcoria projects")
app.add_typer(workers_app, name="workers", help="Manage Falcoria workers")
app.add_typer(scan_app, name="scan", help="Manage Falcoria scans")