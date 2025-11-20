from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.models.concept import ConceptTree, ConceptNode
from app.services.ai_service import generate_concept_tree

router = APIRouter()

@router.get("/concept/{concept_name}")
async def get_concept_tree(concept_name: str):
    """
    获取指定概念的依赖树
    """
    try:
        tree = ConceptTree(
            target=concept_name,
            nodes=[
                ConceptNode(
                    id="1",
                    label=concept_name,
                    description=f"核心概念: {concept_name}",
                    prerequisites=["2", "3"],
                    level=2
                ),
                ConceptNode(
                    id="2",
                    label=f"{concept_name}的前置知识A",
                    description="前置概念A的描述",
                    prerequisites=["4"],
                    level=1
                ),
                ConceptNode(
                    id="3",
                    label=f"{concept_name}的前置知识B",
                    description="前置概念B的描述",
                    prerequisites=["4"],
                    level=1
                ),
                ConceptNode(
                    id="4",
                    label="基础概念",
                    description="最基础的前置概念",
                    prerequisites=[],
                    level=0
                ),
            ],
            total_nodes=4,
            root="1"
        )

        return {
            "concept": concept_name,
            "tree": tree.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    concept: str
    details: Optional[Dict[str, Any]] = None

@router.post("/concept")
async def post_concept(req: GenerateRequest):
    try:
        tree = await generate_concept_tree(req.concept)
        return {"concept": req.concept, "tree": tree.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
