from pydantic import BaseModel
from typing import List

class ConceptNode(BaseModel):
    id: str
    name: str
    description: str
    dependencies: List[str] = []
    level: int = 0

class ConceptTree(BaseModel):
    target: str
    nodes: List[ConceptNode]
    total_nodes: int
