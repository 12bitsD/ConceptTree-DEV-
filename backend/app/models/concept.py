from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ConceptNode(BaseModel):
    id: str
    name: str
    description: str
    level: int = 0
    children: List["ConceptNode"] = Field(default_factory=list)
    parent: Optional[str] = None
    mastered: Optional[bool] = False
    estimatedTime: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TreeStats(BaseModel):
    masteredNodes: int = 0
    totalLearningTime: int = 0
    completionRate: float = 0.0


class ConceptTree(BaseModel):
    target: str
    root: ConceptNode
    total_nodes: int
    max_depth: Optional[int] = None
    stats: Optional[TreeStats] = None
    generated_at: Optional[str] = None
    version: str = "1.0.0"


# pydantic v2 forward refs rebuild
ConceptNode.model_rebuild()
