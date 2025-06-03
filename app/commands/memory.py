import typer
from app.memory import memory
from app.utils import printer
from app.connectors.scanledger_connector import scanledger

memory_app = typer.Typer(no_args_is_help=True)

# ─────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────

@memory_app.command("list")
def list_memory():
    """Show saved projects and last used project."""
    data = memory.load()
    projects = data.get("projects", {})
    last_project = data.get("last_project")

    printer.plain("Saved projects:")
    if not projects:
        printer.warning("No saved projects.")
    else:
        rows = [(name, pid) for name, pid in projects.items()]
        printer.column_table(["Project Name", "ID"], rows)

    print()
    print()
    printer.plain("Last used project:")
    if last_project:
        printer.plain(f"  {last_project}")
    else:
        printer.warning("No last project set.")
    print()


@memory_app.command("set-default")
def set_default(project_id: str):
    """Set the last used project by ID."""
    if not memory.project_id_exists(project_id):
        # Try fetching the project from the server
        try:
            project = scanledger.get_project(project_id)
        except RuntimeError:
            printer.error(f"Project ID '{project_id}' not found in memory or server.")
            raise typer.Exit(1)

        # Fallback name for saving if none exists
        project_name = project.get("name") or f"imported-{project_id[:6]}"
        memory.save_project(project_name, project_id)

    else:
        memory.set_last_project(project_id)

    printer.success(f"Set last used project to '{project_id}' as the default.")
    print()


@memory_app.command("clear")
def clear_memory():
    """Clear all saved projects and last used project."""
    confirm = typer.confirm("Are you sure you want to clear all saved memory?", default=False)
    if confirm:
        memory.clear()
        printer.success("Memory cleared.")
    else:
        printer.info("Aborted. Memory not cleared.")
    print()
