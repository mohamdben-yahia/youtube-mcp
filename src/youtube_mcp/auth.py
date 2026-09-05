"""Authentication and security module for hosted/remote YouTube MCP deployments."""

import os
import sys
import hmac
import secrets
from typing import Optional, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.applications import Starlette

try:
    from mcp.server.transport_security import TransportSecuritySettings
except ImportError:
    TransportSecuritySettings = None


def get_or_generate_auth_key(
    explicit_key: Optional[str] = None,
    allow_generation: bool = True,
) -> Optional[str]:
    """Retrieve the authentication key from arguments or environment, or generate one.

    Looks up:
      1. explicit_key passed as CLI argument
      2. MCP_AUTH_KEY environment variable
      3. YOUTUBE_MCP_AUTH_KEY environment variable

    If the value is 'auto' or empty (and allow_generation=True), a cryptographically
    secure 256-bit token is automatically generated and displayed in the logs.
    """
    key = explicit_key or os.getenv("MCP_AUTH_KEY") or os.getenv("YOUTUBE_MCP_AUTH_KEY")

    if key and key.strip().lower() not in ("auto", "generate", "create"):
        return key.strip()

    if not allow_generation:
        return None

    # Auto-generate a secure token
    generated_key = f"sec_{secrets.token_urlsafe(32)}"

    banner = (
        "\n"
        "================================================================================\n"
        "🔒 [SECURITY] Server Authentication Key Generated (Host Protected)\n"
        f"   MCP_AUTH_KEY: {generated_key}\n\n"
        "   To connect an MCP client (Claude Desktop, Cursor, remote agent), supply this key:\n"
        "   - Header: 'Authorization: Bearer <KEY>' or 'X-API-Key: <KEY>'\n"
        "   - SSE URL: 'http://<host>:<port>/sse?api_key=<KEY>'\n"
        "================================================================================\n"
    )
    sys.stderr.write(banner)
    sys.stderr.flush()

    return generated_key


class AuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware to enforce token authentication on hosted MCP endpoints."""

    def __init__(self, app, auth_key: str):
        super().__init__(app)
        self.auth_key = auth_key

    async def dispatch(self, request: Request, call_next):
        # Allow Docker and load balancer health checks to pass without credentials
        if request.url.path in ("/health", "/healthz", "/ping", "/"):
            return JSONResponse({
                "status": "ok",
                "service": "youtube-mcp",
                "auth_enabled": True,
            })

        # 1. Check Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                if hmac.compare_digest(token, self.auth_key):
                    return await call_next(request)

        # 2. Check X-API-Key: <key>
        api_key_header = request.headers.get("X-API-Key")
        if api_key_header and hmac.compare_digest(api_key_header, self.auth_key):
            return await call_next(request)

        # 3. Check query parameters: ?api_key=<key> or ?token=<key>
        query_key = request.query_params.get("api_key") or request.query_params.get("token")
        if query_key and hmac.compare_digest(query_key, self.auth_key):
            return await call_next(request)

        return JSONResponse(
            {
                "error": "Unauthorized",
                "message": (
                    "Valid authentication key required. Provide via 'Authorization: Bearer <KEY>' header, "
                    "'X-API-Key: <KEY>' header, or '?api_key=<KEY>' query parameter."
                ),
            },
            status_code=401,
        )


def build_secured_starlette_app(
    mcp_server,
    auth_key: Optional[str] = None,
    transport: str = "sse",
    host: str = "127.0.0.1",
    allowed_hosts: Optional[List[str]] = None,
) -> Starlette:
    """Build and secure a Starlette ASGI application for SSE or streamable-http."""
    security_settings = None
    if TransportSecuritySettings is not None:
        hosts = allowed_hosts or []
        env_hosts = os.getenv("MCP_ALLOWED_HOSTS")
        if env_hosts:
            hosts.extend([h.strip() for h in env_hosts.split(",") if h.strip()])
        
        # If binding to all interfaces (0.0.0.0) or custom hosts, disable strict DNS rebinding or allow all
        disable_dns_protection = (
            os.getenv("MCP_DISABLE_DNS_PROTECTION", "false").lower() in ("true", "1", "yes")
            or host == "0.0.0.0"
        )
        if disable_dns_protection:
            security_settings = TransportSecuritySettings(enable_dns_rebinding_protection=False)
        elif hosts:
            security_settings = TransportSecuritySettings(
                enable_dns_rebinding_protection=True,
                allowed_hosts=hosts,
            )

    if transport == "sse":
        kwargs = {"host": host}
        if security_settings is not None:
            kwargs["transport_security"] = security_settings
        app = mcp_server.sse_app(**kwargs)
    elif transport == "streamable-http":
        kwargs = {}
        if security_settings is not None:
            kwargs["transport_security"] = security_settings
        app = mcp_server.streamable_http_app(**kwargs)
    else:
        raise ValueError(f"Unsupported transport for Starlette app: {transport}")

    if auth_key:
        app.add_middleware(AuthMiddleware, auth_key=auth_key)

    return app
