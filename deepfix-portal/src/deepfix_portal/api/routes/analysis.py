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
from langfuse import get_client, observe
from deepfix_core.models import APIRequest, APIResponse, DatasetArtifacts
from deepfix_server.config import LLMConfig
from deepfix_server.coordinators import ArtifactAnalysisCoordinator
from deepfix_server.models import AgentContext
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_api_key_user
from ..models import RequestLog
from ..schemas import APIKeyValidationResponse

router = APIRouter()

LOGGER = logging.getLogger(__name__)


# Singleton coordinator instance
_coordinator: Optional[ArtifactAnalysisCoordinator] = None
_llm_config: Optional[LLMConfig] = None

if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    from openinference.instrumentation.dspy import DSPyInstrumentor

    DSPyInstrumentor().instrument()
    langfuse = get_client()

    # Verify connection
    if langfuse.auth_check():
        LOGGER.info("Langfuse client is authenticated and ready!")
    else:
        LOGGER.warning("Authentication failed. Please check your credentials and host.")


def _get_llm_config() -> LLMConfig:
    """Get or create the LLM configuration from environment variables."""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig.load_from_env()
    return _llm_config


def _get_coordinator() -> ArtifactAnalysisCoordinator:
    """Get or create the singleton coordinator instance."""
    global _coordinator
    if _coordinator is None:
        llm_config = _get_llm_config()
        _coordinator = ArtifactAnalysisCoordinator(config=llm_config)
    return _coordinator


def _serialize_to_json(obj: Any) -> Optional[str]:
    """Serialize an object to JSON string.

    Args:
        obj: Object to serialize.

    Returns:
        JSON string representation, or None if serialization fails.
    """
    if obj is None:
        return None

    try:
        # Handle Pydantic models
        if hasattr(obj, "model_dump"):
            return json.dumps(obj.model_dump(), default=str)
        elif hasattr(obj, "dict"):
            return json.dumps(obj.dict(), default=str)
        # Handle dicts and other JSON-serializable objects
        return json.dumps(obj, default=str)
    except Exception as exc:
        LOGGER.warning(f"Failed to serialize object to JSON: {exc}")
        return None


def _decode_request(request: APIRequest) -> AgentContext:
    """Decode API request into AgentContext.

    Args:
        request: APIRequest containing artifacts and configuration.

    Returns:
        AgentContext with artifacts and settings.

    Raises:
        HTTPException: If request decoding fails (status 400).
    """
    try:
        dataset_artifacts = request.dataset_artifacts
        if isinstance(request.dataset_artifacts, dict):
            dataset_artifacts = DatasetArtifacts.from_dict(request.dataset_artifacts)
        elif request.dataset_artifacts is not None and not isinstance(
            request.dataset_artifacts, DatasetArtifacts
        ):
            raise ValueError("Dataset artifacts must be a DatasetArtifacts object")

        return AgentContext(
            dataset_artifacts=dataset_artifacts,
            training_artifacts=request.training_artifacts,
            deepchecks_artifacts=request.deepchecks_artifacts,
            model_checkpoint_artifacts=request.model_checkpoint_artifacts,
            dataset_name=request.dataset_name,
            language=request.language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Error decoding request: {exc}",
        ) from exc


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
        request_json = _serialize_to_json(request)
        response_json = _serialize_to_json(response)

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
    endpoint = "/api/v1/analyse"

    try:
        # 1. Decode request into AgentContext
        agent_context = _decode_request(request)

        # 2. Get coordinator and run analysis
        coordinator = _get_coordinator()
        results = await coordinator.run(agent_context)

        # 3. Build response
        response = APIResponse(
            agent_results=results.get_agent_results(),
            summary=results.summary,
            additional_outputs=results.additional_outputs,
            error_messages=results.get_error_messages(),
        )

        # 4. Log successful request
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
    return {
        "status": "ok",
        "service": "analysis",
        "coordinator_initialized": _coordinator is not None,
    }
