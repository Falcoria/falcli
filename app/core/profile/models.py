from pydantic import BaseModel


class FalcoriaProfile(BaseModel):
    scanledger_base_url: str
    tasker_base_url: str
    token: str
    projects: list[str] = []
    current_project: str | None = None  # optional field if needed