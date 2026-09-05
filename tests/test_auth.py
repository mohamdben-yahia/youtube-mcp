"""Unit tests for hosted authentication and security middleware."""

import os
import pytest
from unittest.mock import patch
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from youtube_mcp.auth import (
    get_or_generate_auth_key,
    AuthMiddleware,
    build_secured_starlette_app,
)
from youtube_mcp.server import mcp


def test_get_or_generate_auth_key_explicit():
    key = get_or_generate_auth_key(explicit_key="my_secret_token", allow_generation=False)
    assert key == "my_secret_token"


def test_get_or_generate_auth_key_from_env():
    with patch.dict(os.environ, {"MCP_AUTH_KEY": "env_token_abc"}, clear=False):
        key = get_or_generate_auth_key()
        assert key == "env_token_abc"

    with patch.dict(os.environ, {"YOUTUBE_MCP_AUTH_KEY": "fallback_token_xyz"}, clear=False):
        if "MCP_AUTH_KEY" in os.environ:
            del os.environ["MCP_AUTH_KEY"]
        key = get_or_generate_auth_key()
        assert key == "fallback_token_xyz"


def test_get_or_generate_auth_key_auto_generation():
    with patch.dict(os.environ, {"MCP_AUTH_KEY": "auto"}, clear=False):
        key = get_or_generate_auth_key()
        assert key is not None
        assert key.startswith("sec_")
        assert len(key) > 30


def test_auth_middleware_flow():
    secret = "test_auth_token_999"

    async def dummy_endpoint(request):
        return JSONResponse({"message": "authenticated successfully"})

    app = Starlette(
        routes=[
            Route("/protected", dummy_endpoint, methods=["GET", "POST"]),
            Route("/messages/", dummy_endpoint, methods=["POST"]),
        ]
    )
    app.add_middleware(AuthMiddleware, auth_key=secret)

    client = TestClient(app)

    # 1. Health check bypasses authentication
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_healthz = client.get("/healthz")
    assert res_healthz.status_code == 200

    # 2. Unauthenticated request to protected endpoint -> 401
    res_unauth = client.get("/protected")
    assert res_unauth.status_code == 401
    assert res_unauth.json()["error"] == "Unauthorized"

    # 3. Request with wrong key -> 401
    res_wrong = client.get("/protected", headers={"Authorization": "Bearer wrong_token"})
    assert res_wrong.status_code == 401

    # 4. Request with valid Bearer token -> 200
    res_bearer = client.get("/protected", headers={"Authorization": f"Bearer {secret}"})
    assert res_bearer.status_code == 200
    assert res_bearer.json()["message"] == "authenticated successfully"

    # 5. Request with valid X-API-Key header -> 200
    res_header = client.get("/protected", headers={"X-API-Key": secret})
    assert res_header.status_code == 200

    # 6. Request with valid ?api_key= query parameter -> 200
    res_query_api_key = client.get(f"/protected?api_key={secret}")
    assert res_query_api_key.status_code == 200

    # 7. Request with valid ?token= query parameter -> 200
    res_query_token = client.get(f"/protected?token={secret}")
    assert res_query_token.status_code == 200


def test_build_secured_starlette_app_adds_auth():
    app = build_secured_starlette_app(
        mcp_server=mcp,
        auth_key="secure_key_123",
        transport="sse",
        host="127.0.0.1",
    )
    assert isinstance(app, Starlette)
    client = TestClient(app)

    # Health check is accessible
    res = client.get("/health")
    assert res.status_code == 200
