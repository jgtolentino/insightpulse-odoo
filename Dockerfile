# syntax=docker/dockerfile:1.7
ARG PYTHON_TAG=3.11-slim
FROM python:${PYTHON_TAG}

ARG ODOO_REF=19.0
ENV LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential curl ca-certificates \
    libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    libjpeg-dev zlib1g-dev libpng-dev libffi-dev tzdata \
 && rm -rf /var/lib/apt/lists/*

# Odoo
RUN useradd -ms /bin/bash odoo
RUN git clone --depth 1 --branch ${ODOO_REF} https://github.com/odoo/odoo.git /opt/odoo
WORKDIR /opt/odoo
RUN pip install --no-cache-dir -r requirements.txt

# Your addons
# Expect repo paths: addons/custom/* and addons/oca/*
COPY addons/ /mnt/addons/
RUN chown -R odoo:odoo /opt/odoo /mnt/addons

USER odoo
ENV DB_HOST=db DB_PORT=5432 DB_USER=odoo DB_PASSWORD=odoo \
    ADDONS_PATH=/opt/odoo/addons,/mnt/addons \
    SERVER_WIDE_MODULES=web

EXPOSE 8069
CMD python3 odoo-bin \
    --db_host=${DB_HOST} --db_port=${DB_PORT} \
    --db_user=${DB_USER} --db_password=${DB_PASSWORD} \
    --addons-path=${ADDONS_PATH} \
    --limit-time-cpu=120 --limit-time-real=240 \
    --workers=2
