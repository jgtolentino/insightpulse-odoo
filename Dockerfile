# ---------- Build stage ----------
FROM python:3.11-slim AS build

# Build arguments for versioning and metadata
ARG ODOO_VERSION=19.0
ARG INCLUDE_OCA_MODULES=true
ARG BUILD_DATE
ARG VCS_REF

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl git ca-certificates \
    libxml2-dev libxslt1-dev libpq-dev libldap2-dev libsasl2-dev \
    libffi-dev libjpeg-dev zlib1g-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Note: wkhtmltopdf removed - Odoo 19.0 uses Python-based PDF rendering by default

WORKDIR /opt/odoo

# Copy only requirement manifests first for better layer caching
COPY requirements.txt requirements-auto.txt ./
RUN python -m pip install --upgrade pip wheel && \
    pip wheel --wheel-dir /wheels -r requirements.txt && \
    pip wheel --wheel-dir /wheels -r requirements-auto.txt && \
    # Additional AI/OCR dependencies
    pip wheel --wheel-dir /wheels \
        paddlepaddle==2.6.0 \
        paddleocr==2.7.3 \
        anthropic==0.7.8 \
        openai==1.6.1 \
        supabase==2.0.3 \
        fastapi==0.109.0 \
        uvicorn[standard]==0.27.0 \
        pydantic==2.5.3 \
        pillow==10.2.0 \
        opencv-python-headless==4.9.0.80 \
        pandas==2.1.4 \
        numpy==1.24.3 \
        openpyxl==3.1.2 \
        prometheus-client==0.19.0 \
        sentry-sdk==1.39.2

# Install additional production dependencies
RUN pip wheel --wheel-dir /wheels \
    paddleocr==2.7.0 \
    anthropic==0.7.8 \
    supabase==2.0.3 \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    pydantic==2.5.3 \
    python-dotenv==1.0.0

# Clone OCA modules if enabled
RUN if [ "$INCLUDE_OCA_MODULES" = "true" ]; then \
        mkdir -p /oca-modules && \
        cd /oca-modules && \
        git clone -b ${ODOO_VERSION} --depth 1 https://github.com/OCA/server-auth.git oca-server-auth && \
        git clone -b ${ODOO_VERSION} --depth 1 https://github.com/OCA/server-tools.git oca-server-tools && \
        git clone -b ${ODOO_VERSION} --depth 1 https://github.com/OCA/account-financial-reporting.git oca-account-financial && \
        git clone -b ${ODOO_VERSION} --depth 1 https://github.com/OCA/account-financial-tools.git oca-account-tools && \
        git clone -b 16.0 --depth 1 https://github.com/OCA/rest-framework.git oca-rest-framework; \
    fi

# Copy source
COPY . /src

# ---------- Runtime stage ----------
FROM python:3.11-slim AS runtime

# Metadata labels
LABEL org.opencontainers.image.title="InsightPulse AI - Odoo 19 CE + OCA"
LABEL org.opencontainers.image.description="Production Odoo 19 with OCA modules, PaddleOCR, and Finance SSC automation"
LABEL org.opencontainers.image.vendor="InsightPulse AI"
LABEL org.opencontainers.image.authors="InsightPulse Team"
LABEL org.opencontainers.image.source="https://github.com/jgtolentino/insightpulse-odoo"
LABEL org.opencontainers.image.version="${ODOO_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"

ARG ODOO_VERSION=19.0
ARG INCLUDE_OCA_MODULES=true

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    ODOO_RC=/etc/odoo/odoo.conf \
    ODOO_VERSION=${ODOO_VERSION}

# Minimal runtime libs (Debian trixie compatibility)
# Note: libpq-dev needed for pg_config during Odoo source installation
# postgresql-client and redis-tools for entrypoint health checks
# libgomp1 needed for PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libpq-dev libxml2 libxslt1.1 libldap2 libsasl2-2 \
    libjpeg62-turbo zlib1g tzdata gosu curl ca-certificates \
    fonts-dejavu fonts-liberation fonts-noto-cjk \
    postgresql-client redis-tools libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create user and dirs
RUN useradd -m -d /var/lib/odoo -U -r -s /usr/sbin/nologin odoo && \
    mkdir -p /var/lib/odoo/.local /var/log/odoo /mnt/extra-addons /var/lib/odoo/.cache/pip && \
    chown -R odoo:odoo /var/lib/odoo /var/log/odoo /mnt/extra-addons

# Install python wheels built in stage 1 FIRST (includes psycopg2-binary)
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Install Odoo from source (19.0 branch - not yet on PyPI)
# Installing after our wheels ensures psycopg2-binary is already present
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git /opt/odoo-src && \
    cd /opt/odoo-src && \
    pip install --no-cache-dir -e . && \
    rm -rf /var/lib/apt/lists/*

# Clone OCA modules (production-ready versions)
RUN mkdir -p /mnt/extra-addons/oca && \
    cd /mnt/extra-addons/oca && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/server-auth.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/server-tools.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/server-backend.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/account-financial-reporting.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/account-financial-tools.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/account-invoicing.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/account-payment.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/account-reconcile.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/bank-payment.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/purchase-workflow.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/partner-contact.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/hr.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/queue.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/reporting-engine.git && \
    git clone -b 19.0 --depth 1 https://github.com/OCA/web.git && \
    git clone -b 16.0 --depth 1 https://github.com/OCA/rest-framework.git && \
    chown -R odoo:odoo /mnt/extra-addons/oca

# Copy application code (custom addons and scripts)
WORKDIR /opt/odoo
COPY --chown=odoo:odoo --from=build /src/addons /mnt/extra-addons
COPY --chown=odoo:odoo --from=build /src/scripts /opt/odoo/scripts

# Copy OCA modules if they were built
COPY --chown=odoo:odoo --from=build /oca-modules/ /mnt/oca-addons/ || true

# Copy and setup entrypoint (must be before USER odoo)
COPY --from=build /src/scripts/entrypoint-oca.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir -p /etc/odoo /var/lib/odoo /var/log/odoo /mnt/oca-addons && \
    chown -R odoo:odoo /etc/odoo /var/lib/odoo /var/log/odoo /mnt/oca-addons

# Healthcheck endpoint (Odoo supports /web/health from 16+)
HEALTHCHECK --interval=30s --timeout=5s --retries=10 \
  CMD curl -fsS http://localhost:8069/web/health || exit 1

# Default config path (mounted via compose)
VOLUME ["/var/lib/odoo", "/var/log/odoo", "/mnt/extra-addons", "/mnt/oca-addons"]

# Run as non-root
USER odoo

EXPOSE 8069 8071 8072
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
