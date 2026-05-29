from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.workflow_routes import router as workflow_router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="SDLCOS",
    description="AI-native multi-agent SDLC orchestration platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_router)


@app.get("/health")
def health():
    return {"status": "online", "platform": "SDLCOS", "version": "0.1.0"}
