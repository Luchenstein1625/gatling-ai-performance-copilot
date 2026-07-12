from pydantic import BaseModel


class Quadrant(BaseModel):
    number: int
    criticality: str
    complexity: str
