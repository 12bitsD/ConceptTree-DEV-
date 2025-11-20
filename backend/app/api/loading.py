from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time

router = APIRouter()

class StartRequest(BaseModel):
    concept: str
    details: Optional[Dict[str, Any]] = None
    user: Optional[str] = None

class StartResponse(BaseModel):
    sid: str
    concept: str
    details: Optional[Dict[str, Any]] = None
    received_at: int

@router.post('/loading/start', response_model=StartResponse)
async def start_loading(req: StartRequest):
    try:
        now = int(time.time())
        sid = f"ld-{now}"
        return StartResponse(sid=sid, concept=req.concept, details=req.details, received_at=now)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))