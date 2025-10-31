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

# wkhtmltopdf for PDF reports (Debian trixie compatibility)
# Install fonts and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl xz-utils fontconfig \
    libxrender1 libxext6 libx11-6 libxcb1 libx11-xcb1 libxcb-render0 libxcb-shm0 \
    libjpeg62-turbo libpng16-16 libfreetype6 \
    xfonts-base xfonts-75dpi fonts-dejavu fonts-liberation fonts-noto-cjk \
  && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf (Qt-patched) via .deb (preferred / stable)
# Option A: Ubuntu 22.04 (Jammy) package 0.12.6.1-2
# Option B: Debian 11 (Bullseye) package 0.12.6.1-3 (often used on Debian 12 too)
ARG WKHTML_DEB_URL_JAMMY="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb"
ARG WKHTML_DEB_URL_BULLSEYE="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb"

RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    ca-certificates curl fontconfig \
    libxrender1 libxext6 libx11-6 libxcb1 libx11-xcb1 libxcb-render0 libxcb-shm0 \
    libjpeg62-turbo libpng16-16 libfreetype6 \
    xfonts-base xfonts-75dpi fonts-dejavu fonts-liberation fonts-noto-cjk; \
  curl -fL -o /tmp/wkhtml.deb "$WKHTML_DEB_URL_JAMMY" \
  || curl -fL -o /tmp/wkhtml.deb "$WKHTML_DEB_URL_BULLSEYE"; \
  apt-get install -y --no-install-recommends /tmp/wkhtml.deb \
  || (apt-get -f install -y && dpkg -i /tmp/wkhtml.deb); \
  rm -f /tmp/wkhtml.deb; \
  rm -rf /var/lib/apt/lists/*; \
  wkhtmltopdf --version

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

# Minimal runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libxml2 libxslt1.1 libldap-2.5-0 libsasl2-2 \
    libjpeg62-turbo zlib1g tzdata gosu curl ca-certificates xz-utils \
    fontconfig libxrender1 libxext6 libx11-6 libxcb1 libx11-xcb1 libxcb-render0 libxcb-shm0 \
    libpng16-16 libfreetype6 xfonts-base xfonts-75dpi fonts-dejavu fonts-liberation fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf (Qt-patched) via .deb (preferred / stable) in runtime stage
ARG WKHTML_DEB_URL_JAMMY="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb"
ARG WKHTML_DEB_URL_BULLSEYE="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb"

RUN set -eux; \
  apt-get update; \
  curl -fL -o /tmp/wkhtml.deb "$WKHTML_DEB_URL_JAMMY" \
  || curl -fL -o /tmp/wkhtml.deb "$WKHTML_DEB_URL_BULLSEYE"; \
  apt-get install -y --no-install-recommends /tmp/wkhtml.deb \
  || (apt-get -f install -y && dpkg -i /tmp/wkhtml.deb); \
  rm -f /tmp/wkhtml.deb; \
  rm -rf /var/lib/apt/lists/*; \
  wkhtmltopdf --version

# Create user and dirs
RUN useradd -m -d /var/lib/odoo -U -r -s /usr/sbin/nologin odoo && \
    mkdir -p /var/lib/odoo/.local /var/log/odoo /mnt/extra-addons /var/lib/odoo/.cache/pip && \
    chown -R odoo:odoo /var/lib/odoo /var/log/odoo /mnt/extra-addons

# Install Odoo from official apt repository for better maintainability
RUN curl -o odoo.deb https://nightly.odoo.com/19.0/nightly/deb/odoo_19.0.latest_all.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends ./odoo.deb && \
    rm odoo.deb && \
    rm -rf /var/lib/apt/lists/*

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
