from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import domain 
from app.api import routes

# 建立資料庫資料表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Grid Allocator API",
    description="Backend API for Smart Grid Allocator System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend system is running."}

app.include_router(routes.router, prefix="/api/v1", tags=["Grid Allocator"])