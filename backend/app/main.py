from fastapi import FastAPI
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.api import concept

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

_base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_base_dir / ".env")

app = FastAPI(
    title="ConceptTree API",
    description="概念依赖树生成API",
    version="1.0.0"
)

# CORS配置
origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(concept.router, prefix="/api", tags=["概念"])

@app.get("/")
async def root():
    return {
        "message": "ConceptTree API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
