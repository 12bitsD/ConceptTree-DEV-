from pydantic import BaseModel
from typing import List, Optional

class ConceptNode(BaseModel):
    id: str
    label: str
    description: str
    prerequisites: List[str] = []
    level: int = 0

class ConceptTree(BaseModel):
    target: str
    nodes: List[ConceptNode]
    total_nodes: int
    root: Optional[str] = None
