import json

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from deepfix_server.api import AnalyseArtifactsAPI
from deepfix_server.config import PortalConfig
from deepfix_server.portal_client import PortalClient, PortalKeyValidationResult


@pytest.mark.asyncio
async def test_portal_client_success():
    config = PortalConfig(
        base_url="http://portal",
        validate_path="/api/api-keys/validate",
        service_token="svc-token",
        timeout_seconds=1.0,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-Service-Token") == "svc-token"
        assert request.url.path == "/api/api-keys/validate"
        payload = json.loads(request.content.decode())
        assert payload["key"] == "abc123"
        return httpx.Response(
            200,
            json={
                "key_id": "k1",
                "key_name": "default",
                "key_is_active": True,
                "user_id": "u1",
                "user_email": "user@example.com",
                "user_name": "User Example",
                "user_is_active": True,
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url=config.base_url
    ) as http_client:
        client = PortalClient(config=config, client=http_client)
        result = await client.validate_api_key("abc123")

    assert isinstance(result, PortalKeyValidationResult)
    assert result.user_email == "user@example.com"
    assert result.key_is_active is True


@pytest.mark.asyncio
async def test_portal_client_unauthorized():
    config = PortalConfig(
        base_url="http://portal",
        validate_path="/api/api-keys/validate",
        service_token="svc-token",
        timeout_seconds=1.0,
    )

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid API key"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url=config.base_url
    ) as http_client:
        client = PortalClient(config=config, client=http_client)
        with pytest.raises(HTTPException) as exc_info:
            await client.validate_api_key("bad-key")

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authorize_delegates_to_portal_client():
    class DummyPortalClient:
        def __init__(self) -> None:
            self.called_with = None

        async def validate_api_key(self, api_key: str) -> PortalKeyValidationResult:
            self.called_with = api_key
            return PortalKeyValidationResult(
                key_id="k1",
                key_name=None,
                key_is_active=True,
                user_id="user-1",
                user_email="user@example.com",
                user_name=None,
                user_is_active=True,
            )

    api = AnalyseArtifactsAPI()
    api.portal_client = DummyPortalClient()

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid-token"
    )
    result = await api.authorize(auth=credentials)

    assert api.portal_client.called_with == "valid-token"
    assert result.user_id == "user-1"
    assert result.key_is_active is True
