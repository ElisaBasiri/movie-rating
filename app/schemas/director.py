from pydantic import BaseModel


class DirectorOut(BaseModel):
    id: int
    name: str
