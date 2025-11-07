FROM odoo:18.0

# (Optional) Install extra OS deps needed by custom addons
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libxml2-dev libxslt1-dev libpq-dev && rm -rf /var/lib/apt/lists/*

# Mount points are provided by compose; keep image lean
# COPY addons /mnt/addons
# COPY custom /mnt/custom

ENV ODOO_RC=/etc/odoo/odoo.conf
EXPOSE 8069

# Default CMD provided by base image (odoo)
# Override via compose if needed
