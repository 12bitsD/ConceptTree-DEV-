from fastapi import APIRouter, HTTPException
from app.models.concept import ConceptTree, ConceptNode

router = APIRouter()

@router.get("/concept/{concept_name}")
async def get_concept_tree(concept_name: str):
    """
    获取指定概念的依赖树
    """
    try:
        # TODO: 调用AI服务生成依赖树
        # 临时返回mock数据
        tree = ConceptTree(
            target=concept_name,
            nodes=[
                ConceptNode(
                    id="1",
                    name=concept_name,
                    description=f"核心概念: {concept_name}",
                    dependencies=["2", "3"],
                    level=2
                ),
                ConceptNode(
                    id="2",
                    name=f"{concept_name}的前置知识A",
                    description="前置概念A的描述",
                    dependencies=["4"],
                    level=1
                ),
                ConceptNode(
                    id="3",
                    name=f"{concept_name}的前置知识B",
                    description="前置概念B的描述",
                    dependencies=["4"],
                    level=1
                ),
                ConceptNode(
                    id="4",
                    name="基础概念",
                    description="最基础的前置概念",
                    dependencies=[],
                    level=0
                ),
            ],
            total_nodes=4
        )
        
        return {
            "concept": concept_name,
            "tree": tree.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
