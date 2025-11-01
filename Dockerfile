# ---------- Build stage ----------
FROM python:3.11-slim AS build

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl git ca-certificates \
    libxml2-dev libxslt1-dev libpq-dev libldap2-dev libsasl2-dev \
    libffi-dev libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Note: wkhtmltopdf removed - Odoo 19.0 uses Python-based PDF rendering by default

WORKDIR /opt/odoo

# Copy only requirement manifests first for better layer caching
COPY requirements.txt requirements-auto.txt ./
RUN python -m pip install --upgrade pip wheel && \
    pip wheel --wheel-dir /wheels -r requirements.txt && \
    pip wheel --wheel-dir /wheels -r requirements-auto.txt

# Copy source
COPY . /src

# ---------- Runtime stage ----------
FROM python:3.11-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    ODOO_RC=/etc/odoo/odoo.conf

# Minimal runtime libs (Debian trixie compatibility)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libxml2 libxslt1.1 libldap2 libsasl2-2 \
    libjpeg62-turbo zlib1g tzdata gosu curl ca-certificates \
    fonts-dejavu fonts-liberation fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Create user and dirs
RUN useradd -m -d /var/lib/odoo -U -r -s /usr/sbin/nologin odoo && \
    mkdir -p /var/lib/odoo/.local /var/log/odoo /mnt/extra-addons /var/lib/odoo/.cache/pip && \
    chown -R odoo:odoo /var/lib/odoo /var/log/odoo /mnt/extra-addons

# Install Odoo from pip (Debian trixie compatibility - .deb has unmet dependencies)
RUN pip install --no-cache-dir odoo==19.0

# Install python wheels built in stage 1
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code (custom addons and scripts)
WORKDIR /opt/odoo
COPY --chown=odoo:odoo --from=build /src/addons /mnt/extra-addons
COPY --chown=odoo:odoo --from=build /src/scripts /opt/odoo/scripts

# Healthcheck endpoint (Odoo supports /web/health from 16+)
HEALTHCHECK --interval=30s --timeout=5s --retries=10 \
  CMD curl -fsS http://localhost:8069/web/health || exit 1

# Default config path (mounted via compose)
VOLUME ["/var/lib/odoo", "/var/log/odoo", "/mnt/extra-addons"]

# Run as non-root
USER odoo

EXPOSE 8069 8071
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
