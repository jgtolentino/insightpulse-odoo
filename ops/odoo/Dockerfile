# InsightPulse Odoo - Production Dockerfile
# Base: Odoo 19.0 Community Edition
# Platform: DigitalOcean App Platform + Self-hosted droplet

FROM odoo:19.0

LABEL org.opencontainers.image.source=https://github.com/jgtolentino/insightpulse-odoo
LABEL org.opencontainers.image.description="InsightPulse Odoo ERP with AI Agent, Slack Bridge, and PH Localization"
LABEL org.opencontainers.image.licenses="AGPL-3.0"

# Set environment variables
ENV ODOO_RC=/etc/odoo/odoo.conf
ENV PYTHONUNBUFFERED=1

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    python3-dev \
    # PostgreSQL client
    postgresql-client \
    # PDF generation
    wkhtmltopdf \
    # Git for OCA modules
    git \
    # Network tools
    curl \
    wget \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy custom addons
COPY addons/ipai_agent /mnt/extra-addons/ipai_agent
COPY addons/slack_bridge /mnt/extra-addons/slack_bridge

# Copy OCA Philippine localization (if available)
# RUN git clone --depth 1 --branch 19.0 https://github.com/OCA/l10n-philippines.git /tmp/l10n-ph && \
#     cp -r /tmp/l10n-ph/l10n_ph* /mnt/extra-addons/ && \
#     rm -rf /tmp/l10n-ph

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

# Create data directory
RUN mkdir -p /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo

# Configuration file
COPY ops/odoo/odoo.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Switch to odoo user
USER odoo

# Expose port
EXPOSE 8069 8072

# Entry point
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
