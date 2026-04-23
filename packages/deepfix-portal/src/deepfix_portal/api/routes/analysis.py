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
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from deepfix_core.models import APIRequest, APIResponse, APIJobResponse, AnalysisJobStatus
from fastapi import APIRouter, Depends, HTTPException
from langfuse import get_client, observe
from sqlalchemy.orm import Session
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from ..config import settings
from ..database import get_db
from ..dependencies import get_api_key_user
from ..models import RequestLog
from ..schemas import APIKeyValidationResponse

router = APIRouter()

LOGGER = logging.getLogger(__name__)

if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
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


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.TimeoutError))
)
async def proxy_to_deepfix_server(
    request_body: Optional[dict], endpoint: str, timeout: float = 0.5
) -> APIJobResponse:
    """Proxy a request to the DeepFix server and return a job response.

    Args:
        request_body: Optional JSON body for POST requests.
        endpoint: The target endpoint on the DeepFix server.
        timeout: Request timeout in seconds.

    Returns:
        APIJobResponse from the server.

    Raises:
        HTTPException: If the server is unavailable or returns an error.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            if request_body is not None:
                response = await client.post(endpoint, json=request_body)
            else:
                response = await client.get(endpoint)

            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_detail = response.json().get("detail", error_detail)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"DeepFix Server error: {error_detail}",
                )

            return APIJobResponse.model_validate(response.json())

        except httpx.RequestError as exc:
            LOGGER.error(f"Failed to connect to DeepFix Server: {exc}")
            raise HTTPException(
                status_code=503, detail=f"DeepFix Server is unavailable: {exc}"
            )


@router.post("/analyse", response_model=APIJobResponse)
@observe()
async def analyse_artifacts(
    request: APIRequest,
    current_user: APIKeyValidationResponse = Depends(get_api_key_user),
    db: Session = Depends(get_db),
) -> APIJobResponse:
    """Analyze ML artifacts and return diagnostic results.

    This endpoint accepts dataset, training, deepchecks, and model checkpoint
    artifacts, runs analysis through specialized agents, and returns findings
    and recommendations.

    Args:
        request: APIRequest containing artifacts to analyze.
        current_user: Authenticated user from API key validation.
        db: Database session for logging.

    Returns:
        APIJobResponse with analysis results from all agents.

    Raises:
        HTTPException: If authentication fails (401/403) or analysis fails (500).
    """
    start_time = time.perf_counter()
    endpoint = "/v1/analyse"

    try:
        # 1. Forward request to deepfix-server v2
        job_data = await proxy_to_deepfix_server(
            request.model_dump(mode="json"), urljoin(settings.DEEPFIX_SERVER_URL, endpoint)
        )
        
        # 3. Log successful request
        duration_ms = (time.perf_counter() - start_time) * 1000
        await _log_request(
            db=db,
            current_user=current_user,
            endpoint=endpoint,
            request=request,
            response=job_data.result,
            status_code=200,
            duration_ms=duration_ms,
        )

        return job_data

    except HTTPException as exc:
        # Re-raise HTTP exceptions (auth failures, bad requests)
        raise exc
    except Exception as exc:
        LOGGER.exception(f"Analysis failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc(),
        ) from exc



@router.post("/v2/analyse", response_model=APIJobResponse)
@observe()
async def analyse_artifacts_v2(
    request: APIRequest,
    current_user: APIKeyValidationResponse = Depends(get_api_key_user),
    db: Session = Depends(get_db),
) -> APIJobResponse:
    """Proxy to deepfix-server for artifact analysis (Async v2)."""
    start_time = time.perf_counter()
    endpoint = "/v2/analyse"

    try:
        # 1. Forward request to deepfix-server v2
        job_data = await proxy_to_deepfix_server(
            request.model_dump(mode="json"), urljoin(settings.DEEPFIX_SERVER_URL, endpoint)
        )

        # 2. Log submission
        duration_ms = (time.perf_counter() - start_time) * 1000
        # We use a placeholder for response_json since it's just the job handle
        await _log_request(
            db=db,
            current_user=current_user,
            endpoint=endpoint,
            request=request,
            response=APIResponse(summary=f"Job submitted: {job_data.job_id}"),
            status_code=202,
            duration_ms=duration_ms,
        )

        return job_data
    
    except HTTPException as exc:
        # Re-raise HTTP exceptions (auth failures, bad requests)
        raise exc
    except Exception as exc:
        LOGGER.exception(f"Analysis submission failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail=traceback.format_exc(),
        ) from exc


@router.get("/v2/jobs/{job_id}", response_model=APIJobResponse)
@observe()
async def get_job_status(
    job_id: str,
    current_user: APIKeyValidationResponse = Depends(get_api_key_user),
    db: Session = Depends(get_db),
) -> APIJobResponse:
    """Proxy job status from deepfix-server."""
    endpoint = f"/v2/jobs/{job_id}"

    try:
        job_data = await proxy_to_deepfix_server(
            None, urljoin(settings.DEEPFIX_SERVER_URL, endpoint)
        )

        # Optionally log the completion if status is finished
        if job_data.is_finished:
            LOGGER.info(f"Job {job_id} finished with status {job_data.status}")

        return job_data
    except HTTPException as exc:
        # Re-raise HTTP exceptions (auth failures, bad requests)
        raise exc
    except Exception as exc:
        LOGGER.exception(f"Failed to fetch job status: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching job status",
        ) from exc

@router.get("/health")
async def analysis_health():
    """Health check endpoint for the analysis service."""
    server_url = settings.DEEPFIX_SERVER_URL
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
