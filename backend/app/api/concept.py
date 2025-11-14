from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional, Dict, List
from fastapi import Query
from app.models.concept import ConceptTree
from fastapi.encoders import jsonable_encoder
import traceback
from app.services.ai_service import generate_concept_tree, get_progress

router = APIRouter()

@router.get("/concept/{concept_name}")
async def get_concept_tree(
    concept_name: str,
    depth: Optional[int] = Query(None, ge=1, le=12),
    width: Optional[int] = Query(None, ge=1, le=20),
    focus: Optional[str] = Query(None, description="逗号分隔的分支ID列表"),
    minWidth: Optional[str] = Query(None, description="逗号分隔的id:num对，如 a:3,b:2"),
    priority: Optional[str] = Query(None, description="逗号分隔的id:num对，数值越大优先级越高"),
    refine: Optional[bool] = Query(True, description="是否进行二次深度细化"),
):
    try:
        focus_ids: List[str] = []
        if focus:
            focus_ids = [s.strip() for s in focus.split(",") if s.strip()]

        def parse_kv(s: Optional[str]) -> Dict[str, int]:
            out: Dict[str, int] = {}
            if not s:
                return out
            for pair in s.split(","):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    k = k.strip()
                    try:
                        out[k] = int(v.strip())
                    except Exception:
                        continue
            return out

        min_widths = parse_kv(minWidth)
        priorities = parse_kv(priority)

        tree: ConceptTree = await generate_concept_tree(
            concept_name,
            req_max_depth=depth,
            req_max_width=width,
            branch_focus_ids=focus_ids,
            branch_min_widths=min_widths,
            branch_priorities=priorities,
            refine_enabled=refine,
        )
        return {"concept": concept_name, "tree": jsonable_encoder(tree)}
    except Exception as e:
        traceback.print_exc()
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        raise HTTPException(status_code=500, detail=msg)

@router.get("/progress/{concept_name}")
async def get_progress_snapshot(concept_name: str):
    try:
        return get_progress(concept_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
