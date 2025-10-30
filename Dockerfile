# InsightPulse Odoo 19.0 Enterprise Production Dockerfile
# Budget-optimized for DigitalOcean App Platform (basic-xxs: 512MB RAM)

FROM odoo:19.0

# Install system dependencies
USER root

# Install Python dependencies and required packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Create addons directory structure
RUN mkdir -p /mnt/extra-addons/insightpulse \
    /mnt/extra-addons/custom \
    /mnt/extra-addons/oca

# Copy custom addons
COPY addons/insightpulse /mnt/extra-addons/insightpulse
COPY addons/custom /mnt/extra-addons/custom
COPY addons/oca /mnt/extra-addons/oca

# Copy additional addon directories (if needed)
COPY addons/bi_superset_agent /mnt/extra-addons/bi_superset_agent
COPY addons/knowledge_notion_clone /mnt/extra-addons/knowledge_notion_clone
COPY addons/web_environment_ribbon /mnt/extra-addons/web_environment_ribbon
COPY addons/web_favicon /mnt/extra-addons/web_favicon

# Set permissions for addons
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user for security
USER odoo

# Set working directory
WORKDIR /var/lib/odoo

# Expose Odoo HTTP port
EXPOSE 8069

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Odoo configuration via environment variables (set in App Platform spec)
# ODOO_DB_HOST, ODOO_DB_PORT, ODOO_DB_NAME, ODOO_DB_USER, ODOO_DB_PASSWORD
# ODOO_ADMIN_PASSWORD, ODOO_WORKERS, ODOO_MAX_CRON_THREADS

# Default command (can be overridden)
CMD ["odoo", \
     "--db_host=${ODOO_DB_HOST}", \
     "--db_port=${ODOO_DB_PORT}", \
     "--db_user=${ODOO_DB_USER}", \
     "--db_password=${ODOO_DB_PASSWORD}", \
     "--addons-path=/mnt/extra-addons/insightpulse,/mnt/extra-addons/custom,/mnt/extra-addons/oca,/mnt/extra-addons/bi_superset_agent,/mnt/extra-addons/knowledge_notion_clone,/mnt/extra-addons/web_environment_ribbon,/mnt/extra-addons/web_favicon,/usr/lib/python3/dist-packages/odoo/addons", \
     "--workers=${ODOO_WORKERS:-2}", \
     "--max-cron-threads=${ODOO_MAX_CRON_THREADS:-1}", \
     "--db-maxconn=${ODOO_DB_MAXCONN:-8}", \
     "--limit-memory-hard=${ODOO_LIMIT_MEMORY_HARD:-419430400}", \
     "--limit-memory-soft=${ODOO_LIMIT_MEMORY_SOFT:-335544320}", \
     "--limit-time-cpu=${ODOO_LIMIT_TIME_CPU:-300}", \
     "--limit-time-real=${ODOO_LIMIT_TIME_REAL:-600}", \
     "--proxy-mode", \
     "--without-demo=all"]
