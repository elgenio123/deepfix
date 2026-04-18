"""
Artifact analysis routes.

This module provides the API endpoint for analyzing ML artifacts,
replicating the functionality of LitServe-based deepfix-server.
"""

import json
import logging
import os
import time
import traceback
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from deepfix_core.models import APIRequest, APIResponse
from fastapi import APIRouter, Depends, HTTPException
from langfuse import get_client, observe
from sqlalchemy.orm import Session
from functools import lru_cache

from ..database import get_db
from ..dependencies import get_api_key_user
from ..models import RequestLog
from ..schemas import APIKeyValidationResponse

router = APIRouter()

LOGGER = logging.getLogger(__name__)

if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    from openinference.instrumentation.dspy import DSPyInstrumentor

    DSPyInstrumentor().instrument()
    langfuse = get_client()

    # Verify connection
    if langfuse.auth_check():
        LOGGER.info("Langfuse client is authenticated and ready!")
    else:
        LOGGER.warning("Authentication failed. Please check your credentials and host.")


async def _log_request(
    db: Session,
    current_user: APIKeyValidationResponse,
    endpoint: str,
    request: APIRequest,
    response: APIResponse,
    status_code: int,
    duration_ms: float,
) -> None:
    """Log the request to the database.

    Args:
        db: Database session.
        current_user: Current user information.
        endpoint: API endpoint that was called.
        request: The API request.
        response: The API response.
        status_code: HTTP status code.
        duration_ms: Request duration in milliseconds.
    """
    try:
        request_json = request.model_dump_json()
        response_json = response.model_dump_json()

        log_entry = RequestLog(
            user_id=current_user.user_id,
            user_email=current_user.user_email,
            endpoint=endpoint,
            request_json=request_json,
            response_json=response_json,
            status_code=status_code,
            duration_ms=duration_ms,
        )
        db.add(log_entry)
        db.commit()

        LOGGER.info(
            f"Logged request for user {current_user.user_email} "
            f"to {endpoint} ({duration_ms:.2f}ms)"
        )
    except Exception as exc:
        db.rollback()
        LOGGER.exception(f"Failed to log request/response: {exc}")


@lru_cache(maxsize=1)
def get_deepfix_server_url() -> str:
    """Get the DeepFix server URL from environment variables."""
    server_url = os.getenv("DEEPFIX_SERVER_URL")
    if server_url is None or server_url == "":
        raise HTTPException(
            status_code=500,
            detail="DEEPFIX_SERVER_URL not set",
        )
    return server_url


@router.post("/analyse", response_model=APIResponse)
@observe()
async def analyse_artifacts(
    request: APIRequest,
    current_user: APIKeyValidationResponse = Depends(get_api_key_user),
    db: Session = Depends(get_db),
) -> APIResponse:
    """Analyze ML artifacts and return diagnostic results.

    This endpoint accepts dataset, training, deepchecks, and model checkpoint
    artifacts, runs analysis through specialized agents, and returns findings
    and recommendations.

    Args:
        request: APIRequest containing artifacts to analyze.
        current_user: Authenticated user from API key validation.
        db: Database session for logging.

    Returns:
        APIResponse with analysis results from all agents.

    Raises:
        HTTPException: If authentication fails (401/403) or analysis fails (500).
    """
    start_time = time.perf_counter()
    endpoint = "/analyse"

    try:
        # 1. Forward request to deepfix-server
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                # Use model_dump(mode="json") to ensure JSON compatibility
                request_data = request.model_dump(mode="json")

                response_api = await client.post(
                    urljoin(get_deepfix_server_url(), endpoint), json=request_data
                )

                if response_api.status_code != 200:
                    error_detail = response_api.text
                    try:
                        error_detail = response_api.json().get("detail", error_detail)
                    except Exception:
                        pass

                    raise HTTPException(
                        status_code=response_api.status_code,
                        detail=f"DeepFix Server error: {error_detail}",
                    )

                # 2. Build response
                response_json = response_api.json()
                response = APIResponse(**response_json)

            except httpx.RequestError as exc:
                LOGGER.error(f"Failed to connect to DeepFix Server: {exc}")
                raise HTTPException(
                    status_code=503, detail=f"DeepFix Server is unavailable: {exc}"
                )

        # 3. Log successful request
        duration_ms = (time.perf_counter() - start_time) * 1000
        await _log_request(
            db=db,
            current_user=current_user,
            endpoint=endpoint,
            request=request,
            response=response,
            status_code=200,
            duration_ms=duration_ms,
        )

        return response

    except HTTPException as exc:
        # Re-raise HTTP exceptions (auth failures, bad requests)
        raise exc
    except Exception as exc:
        LOGGER.exception(f"Analysis failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc(),
        ) from exc


@router.get("/health")
async def analysis_health():
    """Health check endpoint for the analysis service."""
    server_url = os.getenv("DEEPFIX_SERVER_URL", "http://localhost:8844")
    server_status = "unknown"

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(urljoin(server_url, "health"))
            if resp.status_code == 200:
                server_status = "ok"
            else:
                server_status = f"error_{resp.status_code}"
    except Exception:
        server_status = "unavailable"

    return {
        "status": "ok",
        "service": "portal-analysis-proxy",
        "deepfix_server_url": server_url,
        "deepfix_server_status": server_status,
    }
