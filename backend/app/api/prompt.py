from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.kimi_adapter import generate_refine_options, check_kimi_status

router = APIRouter()

class RefineOption(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    defaultChecked: bool = False
    type: str
    suggested: Optional[List[str]] = None

class RefineRequest(BaseModel):
    concept: str
    context: Optional[Dict[str, Any]] = None

class RefineResponse(BaseModel):
    concept: str
    options: List[RefineOption]

class EnvStatusResponse(BaseModel):
    env_present: bool
    can_call: bool
    model: str
    api_url: str

@router.post("/prompt/refine", response_model=RefineResponse)
async def refine(concept_req: RefineRequest):
    try:
        options = await generate_refine_options(concept_req.concept)
        normalized: List[RefineOption] = []
        for o in options:
            normalized.append(
                RefineOption(
                    id=str(o.get("id")),
                    title=str(o.get("title")),
                    description=o.get("description"),
                    defaultChecked=bool(o.get("defaultChecked", False)),
                    type=str(o.get("type", "single-line")),
                    suggested=o.get("suggested") or None,
                )
            )
        if not normalized:
            raise HTTPException(status_code=502, detail="refine_generation_failed")
        return RefineResponse(concept=concept_req.concept, options=normalized)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompt/env", response_model=EnvStatusResponse)
async def env_status():
    info = await check_kimi_status()
    return EnvStatusResponse(
        env_present=bool(info.get("env_present")),
        can_call=bool(info.get("can_call")),
        model=str(info.get("model")),
        api_url=str(info.get("api_url")),
    )