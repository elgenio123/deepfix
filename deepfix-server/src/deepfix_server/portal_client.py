"""
Client for delegating authorization to deepfix-portal.
"""
from functools import lru_cache
from typing import Optional

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

from .config import PortalConfig
from .logging import get_logger

LOGGER = get_logger(__name__)


class PortalKeyValidationResult(BaseModel):
    """Parsed response from portal API key validation."""

    key_id: str
    key_name: Optional[str]
    key_is_active: bool
    user_id: str
    user_email: str
    user_name: Optional[str]
    user_is_active: bool


class PortalClient:
    """Async client to validate API keys against deepfix-portal."""

    def __init__(
        self, config: PortalConfig, client: Optional[httpx.AsyncClient] = None
    ) -> None:
        self.config = config
        self._client = client or httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
        )

    @lru_cache(maxsize=128)
    async def validate_api_key(self, api_key: str) -> PortalKeyValidationResult:
        """Validate an API key via deepfix-portal."""
        if not api_key:
            raise HTTPException(
                status_code=401, detail="Missing authorization credentials"
            )

        try:
            response = await self._client.post(
                self.config.validate_path,
                json={"key": api_key},
                headers={"X-Service-Token": self.config.service_token},
            )
        except httpx.RequestError as exc:
            LOGGER.exception(f"Portal validation request failed: {exc}")
            raise HTTPException(
                status_code=503, detail="Portal authorization service unavailable"
            ) from exc

        # Map portal responses to API-facing errors.
        if response.status_code in (401, 403):
            detail = self._extract_detail(response)
            raise HTTPException(status_code=response.status_code, detail=detail)
        if response.status_code >= 500:
            raise HTTPException(
                status_code=503, detail="Portal authorization service unavailable"
            )
        if response.is_error:
            detail = self._extract_detail(response)
            raise HTTPException(status_code=response.status_code, detail=detail)

        try:
            payload = response.json()
            return PortalKeyValidationResult(**payload)
        except Exception as exc:  # JSON decode or validation error
            LOGGER.exception(f"Invalid portal validation response: {exc}")
            raise HTTPException(
                status_code=502, detail="Invalid response from portal"
            ) from exc

    @staticmethod
    def _extract_detail(response: httpx.Response) -> str:
        """Best-effort extraction of error detail from the portal response."""
        try:
            data = response.json()
            if isinstance(data, dict) and "detail" in data:
                return str(data["detail"])
        except Exception:
            # Fall back to text if JSON parsing fails
            pass
        return response.text or "Authorization failed"

