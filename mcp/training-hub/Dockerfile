# InsightPulse MCP Training Hub - Dockerfile
# FastMCP server with training orchestration tools

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastmcp \
    httpx \
    pyyaml \
    supabase \
    python-dotenv

# Copy MCP server
COPY server.py /app/server.py

# Expose SSE port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run MCP server
CMD ["python", "server.py"]
