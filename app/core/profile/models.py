from pydantic import BaseModel


class FalcoriaProject(BaseModel):
    name: str
    project_id: str | None = None


class FalcoriaProfile(BaseModel):
    scanledger_base_url: str
    tasker_base_url: str
    token: str
    projects: list[FalcoriaProject] = []
    current_project: FalcoriaProject | None = None  # optional field if needed