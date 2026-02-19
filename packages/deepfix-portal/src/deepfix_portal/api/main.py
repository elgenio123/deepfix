"""
FastAPI main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from .routes import analysis, auth, api_keys, users, request_logs
from .database import engine, Base
from deepfix_core.models import DatabaseBase  # Base for RequestLog table
from deepfix_server.logging import setup_dspy_logging

# Create database tables
Base.metadata.create_all(bind=engine)
# Also create tables from deepfix_core (request_logs table)
DatabaseBase.metadata.create_all(bind=engine)

app = FastAPI(
    title="DeepFix Portal Backend",
    description="Backend for DeepFix Portal",
    version="1.0.0",
)

# CORS middleware - configure for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(
    request_logs.router, prefix="/api/request-logs", tags=["request-logs"]
)
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "DeepFix Portal Backend is running"}


if os.getenv("MLFLOW_EXP_NAME") and os.getenv("MLFLOW_TRACKING_URI"):
    setup_dspy_logging(
        experiment_name=os.getenv("MLFLOW_EXP_NAME"),
        tracking_uri=os.getenv("MLFLOW_TRACKING_URI"),
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5041)
