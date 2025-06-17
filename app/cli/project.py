# app/cli/project.py

import typer
from app.utils.printer import Printer
from app.messages.info import Info
from app.messages.errors import Errors
from app.core.project.services import ProjectService
from app.core.project.models import Project
from app.core.profile.services import ProfileService
from app.cli.ips import ips_app


project_app = typer.Typer(no_args_is_help=True)
project_app.add_typer(ips_app, name="ips", help="IP management commands")


@project_app.command("list")
def list_projects():
    """List all projects."""
    try:
        projects = ProjectService.list_projects()
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    if not projects:
        Printer.warning(Info.Project.NO_PROJECTS_FOUND)
        print()
        return

    Printer.print_model_table(Project, [p.model_dump() for p in projects])
    print()


@project_app.command("create")
def create_project(name: str):
    """Create a new project."""
    try:
        project = ProjectService.create_project(name)
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    if not project:
        Printer.error(Errors.Project.CANNOT_CREATE)
        print()
        return

    Printer.success(Info.Project.CREATED.format(name=project.project_name, id=project.id))
    Printer.key_value_table(project)

    new_project_id = project.id
    saved_project_id = ProjectService.get_saved_project_id()

    if not saved_project_id:
        ProjectService.save_project(new_project_id)
        Printer.plain(Info.Project.FIRST_PROJECT_SAVED)
        print()
        return

    # Show existing project
    Printer.plain(Info.Project.EXISTING_PROJECT.format(
        project_name="unknown",  # no cached names
        project_id=saved_project_id
    ))

    confirm = typer.confirm(Info.Project.CONFIRM_REPLACE, default=False)
    if confirm:
        ProjectService.save_project(new_project_id)
        Printer.plain(Info.Project.MEMORY_UPDATED)
    else:
        Printer.plain(Info.Project.MEMORY_NOT_UPDATED)

    print()


@project_app.command("get")
def get_project(
    project_id: str | None = typer.Argument(
        None, help="Project ID (if not provided, will use the saved project in profile)"
    )
):
    """Get project details."""
    try:
        project_id = project_id or ProjectService.get_saved_project_id()
        if not project_id:
            Printer.error(Errors.Project.ID_REQUIRED)
            raise typer.Exit(1)

        project = ProjectService.get_project(project_id)
        if project:
            Printer.key_value_table(project)
        else:
            Printer.error(Errors.Project.NOT_FOUND)

        print()

    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)


@project_app.command("delete")
def delete_project(project_id: str):
    """Delete a project by ID."""
    try:
        success = ProjectService.delete_project(project_id)
        if success:
            Printer.success(Info.Project.DELETED.format(project_id=project_id))
        else:
            Printer.error(Errors.Project.NOT_FOUND)
            raise typer.Exit(1)

    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)


@project_app.command("set-active")
def set_default_project(project_id: str):
    """Set the default project for the current profile (validated via ScanLedger)."""
    try:
        success = ProjectService.set_default_project(project_id)
        if not success:
            Printer.error(Errors.Project.NOT_FOUND)
            raise typer.Exit(1)

        Printer.success(Info.Project.PROJECT_SET.format(project_id=project_id))
        print()
    except RuntimeError as e:
        Printer.error(str(e))
        raise typer.Exit(1)
