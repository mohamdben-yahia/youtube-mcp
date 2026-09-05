# Build stage using Python slim image with uv
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies into virtual environment
RUN uv venv /app/.venv && uv pip install -r pyproject.toml

# Final runtime image
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment and application code
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/
COPY pyproject.toml .

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose SSE HTTP port
EXPOSE 8000

# Default command: run remote MCP server over Server-Sent Events (SSE)
CMD ["python", "-m", "youtube_mcp", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
