from pathlib import Path
from pydantic import ValidationError

from app.core.profile.models import FalcoriaProfile
from app.messages.errors import Errors
from app.utils.io_utils import save_dict_to_yaml, load_yaml_file
from app.config import PROFILE_DIR
from app.connectors.scanledger_connector import scanledger
from app.core.profile.models import FalcoriaProject


class ProfileService:
    @staticmethod
    def _get_profile_path(profile_name: str) -> Path:
        return PROFILE_DIR / f"{profile_name}.yaml"

    @staticmethod
    def _get_active_profile_file() -> Path:
        return PROFILE_DIR / "active_profile.txt"

    @staticmethod
    def list_profiles() -> list[str]:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        return [p.stem for p in PROFILE_DIR.glob("*.yaml")]

    @staticmethod
    def load_profile(profile_name: str) -> FalcoriaProfile:
        profile_path = ProfileService._get_profile_path(profile_name)
        if not profile_path.exists():
            raise ValueError(Errors.Profile.NOT_FOUND.format(name=profile_name))
        try:
            data = load_yaml_file(profile_path)
            return FalcoriaProfile(**data)
        except (ValidationError, Exception) as e:
            raise ValueError(f"Failed to load profile '{profile_name}': {e}")

    @staticmethod
    def save_profile(profile_name: str, profile: FalcoriaProfile):
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        profile_path = ProfileService._get_profile_path(profile_name)
        save_dict_to_yaml(profile.model_dump(), profile_path)

    @staticmethod
    def delete_profile(profile_name: str):
        profile_path = ProfileService._get_profile_path(profile_name)
        if profile_path.exists():
            profile_path.unlink()

    @staticmethod
    def set_active_profile(profile_name: str):
        active_file = ProfileService._get_active_profile_file()
        active_file.parent.mkdir(parents=True, exist_ok=True)
        active_file.write_text(profile_name)

    @staticmethod
    def get_active_profile_name() -> str:
        active_file = ProfileService._get_active_profile_file()
        active_file.parent.mkdir(parents=True, exist_ok=True)
        if not active_file.exists():
            active_file.write_text("default")
            return "default"
        return active_file.read_text().strip()
    
    @staticmethod
    def validate_profile_data(profile: FalcoriaProfile) -> list[str]:
        required_fields = [
            "scanledger_base_url",
            "tasker_base_url",
            "token"
        ]

        missing_fields = []
        for field in required_fields:
            value = getattr(profile, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)

        return missing_fields
    
    @staticmethod
    def get_saved_project() -> FalcoriaProject | None:
        active_profile_name = ProfileService.get_active_profile_name()
        profile = ProfileService.load_profile(active_profile_name)
        return profile.current_project if profile.current_project else None

    @staticmethod
    def get_saved_project_id() -> str | None:
        falcoria_project = ProfileService.get_saved_project()
        if falcoria_project:
            return falcoria_project.project_id
    
    @staticmethod
    def project_exists(project_id: str) -> bool:
        try:
            response = scanledger.get_project(project_id)
            if response.status_code != 200:
                return False
            return True
        except RuntimeError:
            return False
        
    @staticmethod
    def format_profile_data(profile: FalcoriaProfile) -> list[tuple[str, str]]:
        """Prepare profile data as (field, value) tuples for display."""
        rows = [
            ("scanledger_base_url", profile.scanledger_base_url),
            ("tasker_base_url", profile.tasker_base_url),
            ("token", profile.token)
        ]

        if profile.projects:
            projects = ", ".join([f"{p.name} ({p.project_id})" for p in profile.projects])
        else:
            projects = "-"
        rows.append(("projects", projects))

        if profile.current_project:
            current = f"{profile.current_project.name} ({profile.current_project.project_id})"
        else:
            current = "-"
        rows.append(("current_project", current))

        return rows
    
    @staticmethod
    def get_project_by_id(project_id: str) -> FalcoriaProject | None:
        """Return project by ID from the active profile, or None if not found."""
        active_profile_name = ProfileService.get_active_profile_name()
        if not active_profile_name:
            return None

        profile = ProfileService.load_profile(active_profile_name)
        for project in profile.projects:
            if project.project_id == project_id:
                return project

        return None