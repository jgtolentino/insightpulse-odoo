# Production Dockerfile for InsightPulse Odoo 19.0
# Based on official Odoo image (already includes wkhtmltopdf, dependencies)

FROM odoo:19.0

# Switch to root for setup
USER root

# Install additional Python dependencies for custom modules
COPY requirements.txt requirements-auto.txt /tmp/
RUN pip3 install --no-cache-dir \
    -r /tmp/requirements.txt \
    -r /tmp/requirements-auto.txt \
    && rm -f /tmp/requirements*.txt

# Copy custom addons and scripts
COPY --chown=odoo:odoo addons/insightpulse /mnt/extra-addons/insightpulse
COPY --chown=odoo:odoo addons/custom /mnt/extra-addons/custom

# Copy OCA addons if they exist (optional)
RUN mkdir -p /mnt/extra-addons/oca
COPY --chown=odoo:odoo addons/oca /mnt/extra-addons/oca/ 2>/dev/null || true

# Copy utility scripts
COPY --chown=odoo:odoo scripts /opt/odoo/scripts

# Create necessary directories
RUN mkdir -p /var/lib/odoo/sessions \
    /var/lib/odoo/filestore \
    && chown -R odoo:odoo /var/lib/odoo

# Health check (Odoo 16+ supports /web/health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=5 \
    CMD curl -fsS http://localhost:${PORT:-8069}/web/health || exit 1

# Switch back to odoo user for security
USER odoo

# Expose ports
# 8069: HTTP
# 8072: Longpolling/Gevent (for real-time features)
EXPOSE 8069 8072

# Support DigitalOcean's $PORT environment variable
ENV PORT=8069

# Default command
# Can be overridden in docker-compose or app.yaml
CMD ["odoo"]
