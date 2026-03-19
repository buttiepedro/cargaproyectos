
from pydantic import BaseModel

class TaskCreate(BaseModel):
    tipo: str
    project_id: int
    title: str
    description: str
