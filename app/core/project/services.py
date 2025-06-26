from app.connectors.scanledger_connector import scanledger
from app.core.project.models import Project
from app.core.profile.services import ProfileService
from app.core.profile.models import FalcoriaProject


class ProjectService:
    @staticmethod
    def list_projects() -> list[Project]:
        response = scanledger.get_projects()
        raw_projects = response.json()
        return [Project.model_validate(p) for p in raw_projects]

    @staticmethod
    def create_project(name: str) -> Project | None:
        response = scanledger.create_project(name)
        if response.status_code == 201:
            return Project.model_validate(response.json())
        return None

    @staticmethod
    def get_project(project_id: str) -> Project | None:
        response = scanledger.get_project(project_id)
        if response.status_code == 200:
            return Project.model_validate(response.json())
        return None

    @staticmethod
    def delete_project(project_id: str) -> bool:
        response = scanledger.delete_project(project_id)
        if response.status_code == 204:
            active_profile_name = ProfileService.get_active_profile_name()
            if active_profile_name:
                profile = ProfileService.load_profile(active_profile_name)

                # Remove project from saved projects by project_id
                profile.projects = [
                    p for p in profile.projects if p.project_id != project_id
                ]

                # If current project matches, clear current_project
                if profile.current_project and profile.current_project.project_id == project_id:
                    profile.current_project = None

                ProfileService.save_profile(active_profile_name, profile)

            return True
        else:
            return False

    @staticmethod
    def get_saved_project_id() -> str | None:
        active_profile_name = ProfileService.get_active_profile_name()
        if not active_profile_name:
            return None
        profile = ProfileService.load_profile(active_profile_name)
        return profile.current_project.project_id if profile.current_project else None

    @staticmethod
    def save_project(project: FalcoriaProject) -> None:
        active_profile_name = ProfileService.get_active_profile_name()
        if not active_profile_name:
            return
        profile = ProfileService.load_profile(active_profile_name)
        if project not in profile.projects:
            profile.projects.append(project)
        profile.current_project = project
        ProfileService.save_profile(active_profile_name, profile)

    @staticmethod
    def set_default_project(project_id: str) -> bool:
        """Check if project exists in ScanLedger and set it as default."""
        project = ProjectService.get_project(project_id)
        if not project:
            return False

        falcoria_project = FalcoriaProject(
            name=project.project_name,
            project_id=project.id
        )
        ProjectService.save_project(falcoria_project)
        return True