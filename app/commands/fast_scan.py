import typer
import uuid
from pathlib import Path
from typing import Optional

from app.memory import memory
from app.connectors.scanledger_connector import scanledger
from app.utils import printer
from app.messages import info, errors
from app.commands.scan import start_scan  # ← reuse this!
from app.client import app as client_app


def generate_random_project_name() -> str:
    return f"autoproj-{uuid.uuid4().hex[:8]}"


@client_app.command("fast-scan")
def fast_scan(
    file: Path = typer.Option(..., "--file", "-f", help="Path to file with hosts (1 per line)")
):
    """Start a quick scan using the last or new project and a target file."""
    try:
        project_id = memory.get_last_project_id()
        project = scanledger.get_project(project_id)
    except Exception:
        name = generate_random_project_name()
        try:
            project = scanledger.create_project(name=name, description="Auto-created by fast-scan")
        except RuntimeError as e:
            printer.error(str(e))
            raise typer.Exit(code=1)

        memory.save_project(name, project["id"])
        printer.success(info.Project.CREATED.format(name=name, id=project["id"]))

    # Call shared scan command logic
    start_scan(targets_file=file, project_id=project["id"])

    print()
    printer.plain("To check scan status:  falc.py status")
    printer.plain("To download results:   falc.py project download")
    print()
