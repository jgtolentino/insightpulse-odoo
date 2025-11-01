# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1
WORKDIR /app

# System deps (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl ca-certificates && \
  rm -rf /var/lib/apt/lists/*

# App deps
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# App code
COPY app /app/app

# Non-root
RUN useradd -m appuser
USER appuser

# MCP servers use stdio, no need to expose ports
CMD ["python", "-m", "app.pulser_hub_mcp.main"]
