"""CLI Entrypoint for the YouTube MCP server."""

import argparse
import os
import sys
from dotenv import load_dotenv
from youtube_mcp.server import mcp


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

    args = parser.parse_args()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        sys.stderr.write(
            "[WARNING] YOUTUBE_API_KEY environment variable is not set.\n"
            "Video transcripts (get_video_transcript) will work without an API key,\n"
            "but search, video details, channels, playlists, and comments will require\n"
            "a valid YouTube Data API v3 key.\n\n"
        )
        sys.stderr.flush()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
