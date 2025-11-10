from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import concept

app = FastAPI(
    title="ConceptTree API",
    description="概念依赖树生成API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
