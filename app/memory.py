import uuid
import json
from app.config import config

"""
Memory usage policy:

1. Creating projects:
   - If no project is currently saved in memory → auto-save the new project.
   - If a project is already saved → ask the user whether to replace it.

2. Using project IDs:
   - If a command accepts a project ID and none is provided → use the last saved project ID.
   - If no saved project ID exists → exit with an error message.

3. Deleting projects:
   - On successful deletion → automatically remove the project from memory.
"""

class Memory:
    def __init__(self, path: str = config.memory_file):
        self.path = path
        self.data = {"projects": {}, "last_project": None}

        if self.path.exists():
            try:
                with self.path.open("r") as f:
                    self.data = json.load(f) or {"projects": {}, "last_project": None}
            except json.JSONDecodeError:
                self.data = {"projects": {}, "last_project": None}
                self._save()


    def project_id_exists(self, project_id: str) -> bool:
        return project_id in self.data.get("projects", {}).values()

    # ──────────────── Project Save / Get ────────────────

    def save_project(self, project_name: str, project_id: str):
        self.data.setdefault("projects", {})
        self.data["projects"][project_name] = project_id
        self.data["last_project"] = project_id
        self._save()

    def get_project_id(self, project_name: str) -> str | None:
        return self.data.get("projects", {}).get(project_name)

    def get_last_project_id(self) -> str | None:
        return self.data.get("last_project")

    def set_last_project(self, project_id: str):
        """Manually set the last used project."""
        self.data["last_project"] = project_id
        self._save()

    def get_saved_project_summary(self) -> tuple[str, str] | None:
        """
        Return the (project_name, project_id) pair for the currently saved project.
        Assumes last_project ID must be found in projects.
        """
        project_id = self.get_last_project_id()
        if not project_id:
            return None

        for name, pid in self.data.get("projects", {}).items():
            if pid == project_id:
                return name, pid

        # This is a workaround assumption: ID must exist in projects
        raise ValueError(f"Inconsistent memory state: project ID {project_id} not found in named projects.")

    # ──────────────── Delete ────────────────

    def delete_project_by_id(self, project_id: str):
        projects = self.data.get("projects", {})
        name_to_delete = None

        for name, pid in projects.items():
            if pid == project_id:
                name_to_delete = name
                break

        if name_to_delete:
            del self.data["projects"][name_to_delete]

            if self.data.get("last_project") == project_id:
                self.data["last_project"] = None

            self._save()

    def clear(self):
        """Completely clear all saved data."""
        self.data = {"projects": {}, "last_project": None}
        self._save()

    # ──────────────── Raw Access ────────────────

    def load(self):
        """Return raw memory data."""
        return self.data

    def _save(self):
        def convert(obj):
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(i) for i in obj]
            elif isinstance(obj, uuid.UUID):
                return str(obj)
            else:
                return obj

        with self.path.open("w") as f:
            json.dump(convert(self.data), f, indent=2)


# ──────────────── Singleton ────────────────

memory = Memory()
