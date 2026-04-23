"""
FastAPI main application entry point
"""

import os

from deepfix_core.models import DatabaseBase  # Base for RequestLog table
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .database import Base, engine
from .routes import analysis, api_keys, auth, request_logs, users

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


# Serve frontend static files
static_dir = settings.STATIC_DIR
if static_dir and os.path.exists(static_dir):
    # Mount the static files directory
    # Note: We don't mount at "/" directly to avoid conflicting with the routers
    # Instead, we serve files from the static_dir and use a catch-all for SPA routing

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Skip API routes
        if full_path.startswith("api"):
            return None  # Should be handled by routers

        # Check if requested path is a file in static_dir
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Otherwise serve index.html for SPA routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return {"detail": "Not Found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5041)
