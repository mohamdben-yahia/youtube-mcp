"""CLI Entrypoint for the YouTube MCP server."""

import argparse
import os
import sys
import uvicorn
from dotenv import load_dotenv
from youtube_mcp.server import mcp
from youtube_mcp.auth import get_or_generate_auth_key, build_secured_starlette_app


def main():
    """Parse CLI arguments and start the MCP server."""
    # Load environment variables from .env file if available
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="YouTube Model Context Protocol (MCP) Server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to run the server on (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind for SSE or HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind for SSE or HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--auth-key",
        default=None,
        help="Authentication key for hosted SSE/HTTP endpoints (or set MCP_AUTH_KEY env var)",
    )
    parser.add_argument(
        "--generate-key",
        action="store_true",
        help="Force generation of a new cryptographically secure authentication key",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable authentication on hosted SSE/HTTP endpoints (insecure; for local testing only)",
    )

    args = parser.parse_args()

    api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_API_KEYS")
    if not api_key:
        sys.stderr.write(
            "[WARNING] Neither YOUTUBE_API_KEY nor YOUTUBE_API_KEYS is set.\n"
            "Public RSS feeds (get_channel_rss_videos) and video transcripts (get_video_transcript)\n"
            "will function with zero quota, but official Data API operations will require an API key.\n\n"
        )
        sys.stderr.flush()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport in ("sse", "streamable-http"):
        # Resolve authentication key
        auth_key = None
        if not args.no_auth:
            allow_gen = args.generate_key or (args.auth_key is None and not os.getenv("MCP_AUTH_KEY") and not os.getenv("YOUTUBE_MCP_AUTH_KEY"))
            auth_key = get_or_generate_auth_key(
                explicit_key=args.auth_key,
                allow_generation=allow_gen,
            )

        app = build_secured_starlette_app(
            mcp_server=mcp,
            auth_key=auth_key,
            transport=args.transport,
            host=args.host,
        )

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info",
        )


if __name__ == "__main__":
    main()
