# Production-ready Apache Superset with Odoo integration
# Base image: Apache Superset 4.0.0
FROM apache/superset:4.0.0

# Metadata labels
LABEL org.opencontainers.image.title="InsightPulse AI - Apache Superset"
LABEL org.opencontainers.image.description="Custom Superset with Odoo integration and Finance SSC dashboards"
LABEL org.opencontainers.image.vendor="InsightPulse AI"
LABEL org.opencontainers.image.authors="InsightPulse Team"
LABEL org.opencontainers.image.source="https://github.com/jgtolentino/insightpulse-odoo"

# Build arguments
ARG SUPERSET_VERSION=4.0.0
ARG BUILD_DATE
ARG VCS_REF

# Add build metadata
LABEL org.opencontainers.image.version="${SUPERSET_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for production
RUN pip install --no-cache-dir \
    # PostgreSQL driver (required for Odoo connection)
    psycopg2-binary==2.9.9 \
    # Environment management
    python-dotenv==1.0.0 \
    # OAuth/Authentication
    authlib==1.3.0 \
    # Excel export support
    openpyxl==3.1.2 \
    xlsxwriter==3.1.9 \
    # Image processing for thumbnails
    pillow==10.2.0 \
    # Screenshot/Report generation
    playwright==1.40.0 \
    # Redis for caching
    redis==5.0.1 \
    # Celery for async tasks
    celery==5.3.4 \
    # Additional database drivers
    pymysql==1.1.0 \
    clickhouse-driver==0.2.6 \
    snowflake-sqlalchemy==1.5.1 \
    # Metrics and monitoring
    prometheus-client==0.19.0

# Install Playwright browsers for screenshots
RUN playwright install chromium && \
    playwright install-deps chromium

# Create necessary directories
RUN mkdir -p \
    /app/pythonpath \
    /app/config \
    /app/docker \
    /app/superset_home \
    /app/superset_home/dashboards \
    /app/superset_home/datasets

# Copy custom Superset configuration
COPY --chown=superset:superset ./superset_config.py /app/pythonpath/
COPY --chown=superset:superset ./init-superset.sh /app/docker/

# Make scripts executable
RUN chmod +x /app/docker/init-superset.sh

# Set permissions
RUN chown -R superset:superset \
    /app/pythonpath \
    /app/config \
    /app/docker \
    /app/superset_home

# Environment variables for production
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py \
    FLASK_APP="superset.app:create_app()" \
    PYTHONPATH="/app/pythonpath:${PYTHONPATH}" \
    SUPERSET_HOME=/app/superset_home

# Switch back to superset user
USER superset

# Expose Superset port
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl --fail http://localhost:8088/health || exit 1

# Default command (can be overridden for worker/beat)
CMD ["/app/docker/init-superset.sh"]
