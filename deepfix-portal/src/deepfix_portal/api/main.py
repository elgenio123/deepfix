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
        "http://localhost:8844",
        "http://localhost:5173",
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


# Serve static files in production
# In development, Vite handles this
if os.getenv("NODE_ENV") == "production":
    # Check multiple possible locations for the built frontend
    # 1. Docker: copied to src/deepfix_portal/dist/public
    # 2. Local: Vite outputs to project_root/dist/public
    possible_paths = [
        Path(__file__).parent.parent / "dist" / "public",  # Docker path
        Path(__file__).parent.parent.parent.parent / "dist" / "public",  # Local path
    ]

    dist_path = None
    for path in possible_paths:
        if path.exists() and (path / "index.html").exists():
            dist_path = path
            break

    if dist_path:
        # Mount assets at /assets to match Vite's output references
        assets_path = dist_path / "assets"
        if assets_path.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

        @app.get("/")
        async def serve_index():
            """Serve index.html for root path"""
            return FileResponse(str(dist_path / "index.html"))

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve SPA for all non-API routes"""
            if full_path.startswith("api"):
                return {"error": "Not found"}
            # Try to serve static file first
            file_path = dist_path / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            # Otherwise serve index.html for SPA routing
            return FileResponse(str(dist_path / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5041)
