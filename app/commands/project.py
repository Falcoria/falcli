import typer

from app.connectors.scanledger_connector import scanledger
from app.memory import memory
from app.messages import errors, info
from app.utils import printer
from app.commands.ips import ips_app
from app.schemas import Project


project_app = typer.Typer(no_args_is_help=True)
project_app.add_typer(ips_app, name="ips", help="IP management commands")

# --- Commands ---

from app.utils.printer import print_model_table
from app.schemas import Project  # your Pydantic model

@project_app.command("list")
def list_projects():
    """List all projects."""
    try:
        raw_projects = scanledger.get_projects()
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)
    
    if not raw_projects:
        printer.warning(info.Project.NO_PROJECTS_FOUND)
        print()
        return

    print_model_table(Project, raw_projects)
    print()


@project_app.command("create")
def create_project(name: str):
    """Create a new project."""

    # Wrap only the request
    try:
        result = scanledger.create_project(name)
    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)

    if not result:
        printer.error(errors.Project.CANNOT_CREATE)
        print()
        return

    project = Project.model_validate(result)

    printer.success(info.Project.CREATED.format(name=project.project_name, id=project.id))
    printer.key_value_table(project)

    new_project_id = project.id

    summary = memory.get_saved_project_summary()

    if summary is None:
        memory.save_project(project.project_name, new_project_id)
        printer.plain(info.Project.FIRST_PROJECT_SAVED)
        print()
        return

    current_saved_name, current_saved_id = summary

    print()
    printer.plain(info.Project.EXISTING_PROJECT.format(
        project_name=current_saved_name,
        project_id=current_saved_id
    ))
    confirm = typer.confirm(info.Project.CONFIRM_REPLACE, default=False)

    if confirm:
        memory.save_project(project.project_name, new_project_id)
        printer.plain(info.Project.MEMORY_UPDATED)
    else:
        printer.plain(info.Project.MEMORY_NOT_UPDATED)

    print()



@project_app.command("get")
def get_project(
    project_id: str = typer.Argument(
        None, help="Project ID (if not provided, will use the last saved project)"
    )
):
    """Get project details."""
    try:
        project_id = project_id or memory.get_last_project_id()
        if not project_id:
            printer.error(errors.Project.ID_REQUIRED)
            raise typer.Exit(1)

        project = scanledger.get_project(project_id)
        if project:
            printer.key_value_table(project)
        else:
            printer.error(errors.Project.NOT_FOUND)

        print()

    except RuntimeError as e:
        printer.error(str(e))
        raise typer.Exit(1)


@project_app.command("delete")
def delete_project(project_id: str):
    """Delete a project by ID."""
    try:
        response = scanledger.delete_project(project_id)

        if response.status_code == 204:
            try:
                memory.delete_project_by_id(project_id)
            except Exception as e:
                # TODO: Handle memory deletion error
                pass
            printer.success(info.Project.DELETED.format(project_id=project_id))
        else:
            printer.error(errors.HTTP.ERROR.format(status=response.status_code, message=response.text))
            raise typer.Exit(1)

    except RuntimeError as e:
        printer.error(f"{e}")
        raise typer.Exit(1)
