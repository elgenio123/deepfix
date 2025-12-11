"""
LitServe callbacks for request/response logging.
"""

import json
import time
from typing import Any, Dict, Optional

from litserve.callbacks import Callback

from .config import DatabaseConfig
from .database import init_database, get_session
from .db_models import RequestLog
from .logging import get_logger
from .portal_client import PortalKeyValidationResult

LOGGER = get_logger(__name__)


class RequestLoggingCallback(Callback):
    """Callback to log successful requests and responses to the database.

    This callback captures request timing, user identity (from authorization),
    and stores the request/response payloads as JSON in the shared database.

    Only successful requests (status 2xx) are logged.
    """

    def __init__(self, database_config: DatabaseConfig) -> None:
        """Initialize the logging callback.

        Args:
            database_config: Configuration for the database connection.
        """
        super().__init__()
        self._database_config = database_config
        self._request_data: Dict[str, Dict[str, Any]] = {}
        self._db_initialized = False

    def _ensure_db_initialized(self) -> None:
        """Initialize database connection if not already done."""
        if not self._db_initialized:
            init_database(self._database_config)
            self._db_initialized = True

    def on_request(self, *args, **kwargs) -> None:
        """Called when request enters the endpoint function.

        Captures the start time and request data for later logging.
        """
        # Extract request_id from kwargs if available
        # LitServe passes various parameters depending on the hook
        lit_api = kwargs.get("lit_api")
        request = kwargs.get("request")

        # Generate a unique request ID based on the request object id
        request_id = str(id(request)) if request else str(time.time_ns())

        # Store request timing and data
        self._request_data[request_id] = {
            "start_time": time.time(),
            "request": request,
            "lit_api": lit_api,
        }

        LOGGER.debug(f"Request started: {request_id}")

    def on_response(self, *args, **kwargs) -> None:
        """Called when response is generated and ready to return.

        Logs the request/response to the database if the request was successful.
        """
        lit_api = kwargs.get("lit_api")
        response = kwargs.get("response")

        # Find matching request data by checking lit_api reference
        request_id = None
        request_data = None

        for rid, data in list(self._request_data.items()):
            if data.get("lit_api") is lit_api:
                request_id = rid
                request_data = data
                break

        if request_data is None:
            LOGGER.warning("No matching request data found for response")
            return

        try:
            # Calculate duration
            duration_ms = (time.time() - request_data["start_time"]) * 1000

            # Get user info from lit_api (set during authorize)
            current_user: Optional[PortalKeyValidationResult] = getattr(
                lit_api, "_current_user", None
            )

            if current_user is None:
                LOGGER.warning("No user info available for logging")
                return

            # Determine status code - assume success if we reached on_response
            # LitServe doesn't pass status code directly, so we infer success
            status_code = 200

            # Serialize request and response to JSON
            request_json = self._serialize_to_json(request_data.get("request"))
            response_json = self._serialize_to_json(response)

            # Get endpoint from lit_api
            endpoint = getattr(lit_api, "api_path", "/v1/analyse")

            # Log to database
            self._log_to_database(
                user_id=current_user.user_id,
                user_email=current_user.user_email,
                endpoint=endpoint,
                request_json=request_json,
                response_json=response_json,
                status_code=status_code,
                duration_ms=duration_ms,
            )

            LOGGER.info(
                f"Logged request for user {current_user.user_email} "
                f"to {endpoint} ({duration_ms:.2f}ms)"
            )

        except Exception as exc:
            LOGGER.exception(f"Failed to log request/response: {exc}")

        finally:
            # Clean up request data
            if request_id:
                self._request_data.pop(request_id, None)

    def _serialize_to_json(self, obj: Any) -> Optional[str]:
        """Serialize an object to JSON string.

        Args:
            obj: Object to serialize. Can be a Pydantic model, dict, or other.

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

    def _log_to_database(
        self,
        user_id: str,
        user_email: str,
        endpoint: str,
        request_json: Optional[str],
        response_json: Optional[str],
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Insert a request log entry into the database.

        Args:
            user_id: ID of the user who made the request.
            user_email: Email of the user.
            endpoint: API endpoint that was called.
            request_json: JSON-serialized request payload.
            response_json: JSON-serialized response payload.
            status_code: HTTP status code of the response.
            duration_ms: Request duration in milliseconds.
        """
        self._ensure_db_initialized()

        session = get_session()
        try:
            log_entry = RequestLog(
                user_id=user_id,
                user_email=user_email,
                endpoint=endpoint,
                request_json=request_json,
                response_json=response_json,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            session.add(log_entry)
            session.commit()
        except Exception as exc:
            session.rollback()
            LOGGER.exception(f"Failed to insert request log: {exc}")
            raise
        finally:
            session.close()
