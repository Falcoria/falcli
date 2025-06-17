from pydantic import BaseModel

class Project(BaseModel):
    project_name: str
    id: str
    users: list[str] = []