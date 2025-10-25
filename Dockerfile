FROM odoo:19.0

# Set working directory
WORKDIR /var/lib/odoo

# Copy custom addons
COPY insightpulse_odoo/addons /mnt/addons

# Copy Odoo configuration
COPY insightpulse_odoo/config/odoo.conf /etc/odoo/odoo.conf

# Install additional dependencies if needed
USER root
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Switch back to odoo user
USER odoo

# Expose Odoo port
EXPOSE 8069

# Default command
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
