#!/usr/bin/env bash
set -euo pipefail

# n8n Opex Workflow Management Script
# For Mattermost ↔ n8n ↔ Odoo/Supabase integration

# Adjust if your container name is different
N8N_CONTAINER=${N8N_CONTAINER:-n8n}
BACKUP_DIR=/var/backups/n8n/$(date +%Y%m%d-%H%M)

echo "🔧 n8n Opex Workflow Management"
echo "=================================="

# Create backup directory
mkdir -p "${BACKUP_DIR}"

echo "[1/4] Export ALL workflows (including /opex)..."
docker exec -u node "${N8N_CONTAINER}" \
  n8n export:workflow --all --output="${BACKUP_DIR}/workflows.json"

echo "[2/4] Export ALL credentials..."
docker exec -u node "${N8N_CONTAINER}" \
  n8n export:credentials --all --output="${BACKUP_DIR}/creds.json"

echo "[3/4] Export full entities snapshot (for DB migration / disaster recovery)..."
docker exec -u node "${N8N_CONTAINER}" \
  n8n export:entities --outputDir "${BACKUP_DIR}/entities" \
  --includeExecutionHistoryDataTables true

echo "[4/4] Show /opex workflow id..."
docker exec -u node "${N8N_CONTAINER}" \
  n8n export:workflow --all --pretty | jq '.[] | select(.name | test("opex"; "i")) | {id, name}'

echo ""
echo "✅ Backup completed: ${BACKUP_DIR}"
echo ""
echo "To deploy to another instance:"
echo "  scp -r '${BACKUP_DIR}' user@target-host:/var/backups/n8n/"
echo ""
echo "On target host:"
echo "  docker exec -u node n8n n8n import:workflow --input=${BACKUP_DIR}/workflows.json"
echo "  docker exec -u node n8n n8n import:credentials --input=${BACKUP_DIR}/creds.json"
echo "  docker exec -u node n8n n8n import:entities --inputDir ${BACKUP_DIR}/entities --truncateTables true"
