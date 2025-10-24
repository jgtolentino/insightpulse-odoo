FROM odoo:19.0

# optional extra Python deps
COPY requirements.txt /tmp/requirements.txt
RUN if [ -s /tmp/requirements.txt ]; then pip3 install --no-cache-dir -r /tmp/requirements.txt; fi

# addons (order for cache)
COPY addons/bi_superset_agent /mnt/extra-addons/bi_superset_agent
COPY addons/custom /mnt/extra-addons/custom

ENV ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/bi_superset_agent,/mnt/extra-addons/custom"
ENV ODOO_RC=/etc/odoo/odoo.conf
