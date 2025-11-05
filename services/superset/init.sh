#!/usr/bin/env bash
set -euo pipefail

# Create admin
superset fab create-admin \
  --username "${ADMIN_USERNAME}" \
  --firstname "${ADMIN_FIRSTNAME}" \
  --lastname  "${ADMIN_LASTNAME}" \
  --email     "${ADMIN_EMAIL}" \
  --password  "${ADMIN_PASSWORD}"

# Load official example datasets & dashboards
superset load_examples

# Init roles, perms, and defaults
superset init

# Publish & retitle one of the example dashboards so you have a clean demo entry point
python /app/publish_examples.py || true
