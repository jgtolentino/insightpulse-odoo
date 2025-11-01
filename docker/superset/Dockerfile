# Apache Superset Production Dockerfile
# Base: Official Apache Superset image
# Deployment: DigitalOcean App Platform
# Date: 2025-10-30

# Use official Superset image as base
ARG SUPERSET_VERSION=latest
FROM apache/superset:${SUPERSET_VERSION}

# Metadata
LABEL maintainer="InsightPulse AI <admin@insightpulseai.net>"
LABEL description="Apache Superset Production Image with PostgreSQL and additional drivers"
LABEL version="1.0.0"

# Switch to root for package installation
USER root

# ========================================
# System Dependencies
# ========================================

# Install system dependencies for database drivers and production tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL development libraries
    libpq-dev \
    # Build tools for Python packages
    build-essential \
    gcc \
    g++ \
    python3-dev \
    # Security and monitoring tools
    curl \
    wget \
    ca-certificates \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ========================================
# Python Dependencies
# ========================================

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

# Install production database drivers
RUN pip install --no-cache-dir \
    # PostgreSQL driver (required for Supabase)
    psycopg2-binary==2.9.9 \
    # Async support for Gunicorn
    gevent==24.2.1 \
    greenlet==3.0.3 \
    # Additional database drivers (optional, for connecting to data sources)
    pymysql==1.1.0 \
    # MongoDB support
    pymongo==4.6.1 \
    # Redis support for caching
    redis==5.0.1 \
    hiredis==2.3.2 \
    # Security enhancements
    flask-talisman==1.1.0 \
    # Rate limiting
    flask-limiter==3.5.0 \
    # Monitoring and logging
    sentry-sdk==1.40.0

# ========================================
# Production Configuration
# ========================================

# Copy production configuration
COPY config/superset/superset_config_production.py /app/pythonpath/superset_config.py

# Create required directories
RUN mkdir -p \
    /app/superset_home/uploads \
    /app/superset_home/sqllab \
    /tmp/celerybeat-schedule \
    && chown -R superset:superset /app/superset_home \
    && chown -R superset:superset /tmp/celerybeat-schedule

# ========================================
# Security Hardening
# ========================================

# Set proper permissions
RUN chmod 755 /app/superset_home \
    && chmod 755 /app/superset_home/uploads \
    && chmod 755 /app/superset_home/sqllab

# Remove unnecessary setuid/setgid binaries
RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} \; || true

# ========================================
# Health Check
# ========================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8088/health || exit 1

# ========================================
# Runtime Configuration
# ========================================

# Switch back to superset user for security
USER superset

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8088

# Set environment variables
ENV PYTHONPATH="/app/pythonpath:/app/config" \
    SUPERSET_ENV="production" \
    FLASK_APP="superset.app:create_app()"

# ========================================
# Entrypoint Script
# ========================================

# Create custom entrypoint for initialization
COPY docker/superset/entrypoint.sh /app/entrypoint.sh
USER root
RUN chmod +x /app/entrypoint.sh
USER superset

# Default command: Run Gunicorn with gevent workers
CMD ["/app/entrypoint.sh"]
