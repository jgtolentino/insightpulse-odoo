#!/usr/bin/env bash
set -e
superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@local --password admin
superset db upgrade
superset init
# Import dashboards
for f in /dashboards/*.json; do
  [ -f "$f" ] && superset import-dashboards -p "$f" || true
done
