import typer

from app.core.profile.services import ProfileService
from app.utils.printer import Printer
from app.messages.errors import Errors


def get_current_project_id(project_id: str | None) -> str:
    project_id = project_id or ProfileService.get_saved_project_id()
    if not project_id:
        Printer.error(Errors.Project.ID_REQUIRED)
        raise typer.Exit(1)
    return project_id
