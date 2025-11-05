FROM odoo:16.0

USER root
RUN apt-get update && apt-get install -y --no-install-recommends wget xz-utils fonts-dejavu && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER odoo
