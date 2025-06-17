from pathlib import Path

import typer

from app.core.profile.services import ProfileService
from app.core.profile.models import FalcoriaProfile
from app.utils.printer import Printer
from app.messages.info import Info
from app.messages.errors import Errors
from app.utils.io_utils import load_yaml_file


profile_app = typer.Typer(name="profile", no_args_is_help=True, help="Manage Falcoria profiles")


@profile_app.command("list", help="List all available profiles")
def list_profiles():
    profiles = ProfileService.list_profiles()
    Printer.header(Info.Profile.AVAILABLE_PROFILES)
    for profile_name in profiles:
        Printer.plain(f"- {profile_name}")


@profile_app.command("show", help="Show details of a specific profile")
def show_profile(name: str = typer.Argument(None, help="Profile name (if not provided, active profile will be used)")):
    try:
        if name is None:
            name = ProfileService.get_active_profile_name()
            if not name:
                Printer.error(Errors.Profile.NO_ACTIVE_PROFILE)
                raise typer.Exit(1)

        profile = ProfileService.load_profile(name)
        Printer.header(Info.Profile.PROFILE_HEADER.format(name=name))

        # Build rows dynamically
        rows = []
        for field_name, value in profile.model_dump().items():
            if isinstance(value, list):
                value = ", ".join(value) if value else "-"
            elif value is None:
                value = "-"
            rows.append((field_name, str(value)))

        Printer.column_table(["Field", "Value"], rows)
        print()

    except ValueError as e:
        Printer.error(str(e))

@profile_app.command("create", help="Create a new profile")
def create_profile(
    name: str,
    scanledger_base_url: str,
    tasker_base_url: str,
    token: str
):
    profile = FalcoriaProfile(
        scanledger_base_url=scanledger_base_url,
        tasker_base_url=tasker_base_url,
        token=token
    )
    ProfileService.save_profile(name, profile)
    Printer.success(Info.Profile.CREATED.format(name=name))


@profile_app.command("delete", help="Delete a profile")
def delete_profile(name: str):
    try:
        ProfileService.load_profile(name)  # ensure profile exists
        ProfileService.delete_profile(name)
        Printer.success(Info.Profile.DELETED.format(name=name))
    except ValueError as e:
        Printer.error(str(e))


@profile_app.command("set-active-profile", help="Set a profile as active")
def set_active(name: str):
    try:
        ProfileService.load_profile(name)  # ensure profile exists
        ProfileService.set_active_profile(name)
        Printer.success(Info.Profile.ACTIVE_SET.format(name=name))
    except ValueError as e:
        Printer.error(str(e))


@profile_app.command("set-active-project", help="Set the default project for the active profile")
def set_default_project(project_id: str):
    active_profile_name = ProfileService.get_active_profile_name()
    if not active_profile_name:
        Printer.error(Errors.Profile.NO_ACTIVE_PROFILE)
        raise typer.Exit(1)

    if not ProfileService.project_exists(project_id):
        Printer.error(Errors.Project.NOT_FOUND.format(project_id=project_id))
        raise typer.Exit(1)

    try:
        profile = ProfileService.load_profile(active_profile_name)
        profile.current_project = project_id
        ProfileService.save_profile(active_profile_name, profile)
        Printer.success(Info.Profile.DEFAULT_PROJECT_SET.format(
            project_id=project_id,
            profile_name=active_profile_name
        ))
    except ValueError as e:
        Printer.error(str(e))


@profile_app.command("set", help="Set a field in the active profile")
def set_profile_field(
    name: str,
    field: str,
    value: str
):
    try:
        profile = ProfileService.load_profile(name)
    except ValueError as e:
        Printer.error(str(e))
        raise typer.Exit(1)

    # Validate field name
    if field not in profile.__class__.model_fields:
        Printer.error(Errors.Profile.INVALID_FIELD.format(
            field=field,
            allowed_fields=list(profile.__class__.model_fields.keys())
        ))
        raise typer.Exit(1)


    # Convert value to correct type
    field_type = profile.__class__.model_fields[field].annotation
    try:
        if field_type == str:
            typed_value = value
        elif field_type == list[str]:
            typed_value = [item.strip() for item in value.split(",")]
        elif field_type == int:
            typed_value = int(value)
        elif field_type == bool:
            typed_value = value.lower() in ("true", "1", "yes")
        elif field_type == type(None):
            typed_value = None
        else:
            typed_value = value
    except Exception as e:
        Printer.error(Errors.Profile.PARSE_FAILED.format(field=field, error=e))
        raise typer.Exit(1)

    setattr(profile, field, typed_value)
    ProfileService.save_profile(name, profile)
    Printer.success(Info.Profile.FIELD_UPDATED.format(field=field, name=name))


@profile_app.command("show-active", help="Show the currently active profile")
def show_active_profile():
    active_profile_name = ProfileService.get_active_profile_name()
    if active_profile_name:
        Printer.success(Info.Profile.ACTIVE_PROFILE.format(name=active_profile_name))
    else:
        Printer.error(Errors.Profile.NO_ACTIVE_PROFILE)


@profile_app.command("validate", help="Validate a profile file")
def validate_profile(profile_file: Path = typer.Argument(..., help="Path to profile YAML file to validate")):
    try:
        if not profile_file.exists():
            Printer.error(Errors.Profile.PROFILE_FILE_NOT_FOUND.format(file_path=profile_file))
            raise typer.Exit(1)

        data = load_yaml_file(profile_file)
        profile = FalcoriaProfile(**data)

        missing_fields = ProfileService.validate_profile_data(profile)

        if missing_fields:
            Printer.error(Errors.Profile.MISSING_REQUIRED_FIELDS.format(
                name=profile_file.name,
                missing_fields=", ".join(missing_fields)
            ))
            raise typer.Exit(1)
        else:
            Printer.success(Info.Profile.PROFILE_VALID.format(name=profile_file.name))

    except Exception as e:
        Printer.error(Errors.Profile.FAILED_TO_LOAD.format(name=profile_file, error=e))
        raise typer.Exit(1)