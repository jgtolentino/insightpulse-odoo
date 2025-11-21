#!/usr/bin/env bash
#
# n8n-sync.sh - Manage finance automations (Odoo, Supabase, Superset, Notion)
#
# Usage:
#   ./scripts/n8n-sync.sh backup
#   ./scripts/n8n-sync.sh restore
#   ./scripts/n8n-sync.sh activate
#   ./scripts/n8n-sync.sh execute W001_OD_MNTH_CLOSE_SYNC
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INDEX_FILE="$REPO_ROOT/workflows/index.yaml"

# Override via env if needed
N8N_CONTAINER="${N8N_CONTAINER:-odoo-ipa-1}"
N8N_HOST="${N8N_HOST:-root@erp.insightpulseai.net}"
BACKUP_DIR="${BACKUP_DIR:-$REPO_ROOT/workflows/backups}"

mkdir -p "$BACKUP_DIR"

# Cheap YAML parser: line-based grep/awk (good enough for our structure)
get_workflow_ids() {
  awk '/^  - code: / {code=$3}
       /    id:/ {id=$2; print code":"id}' "$INDEX_FILE"
}

get_id_by_code() {
  local code="$1"
  awk -v target="$code" '
    /^  - code:/ {
      sub("  - code: ","",$0); gsub("\"","",$0);
      current=$0
    }
    /    id:/ && current==target {
      print $2; exit 0
    }' "$INDEX_FILE"
}

get_file_by_code() {
  local code="$1"
  awk -v target="$code" '
    /^  - code:/ {
      sub("  - code: ","",$0); gsub("\"","",$0);
      current=$0
    }
    /    file:/ && current==target {
      sub("    file: ","",$0); gsub("\"","",$0);
      print $0; exit 0
    }' "$INDEX_FILE"
}

backup() {
  echo "==> Backing up workflows listed in $INDEX_FILE"
  echo "→ Exporting from n8n container on $N8N_HOST"

  # Export all workflows from production n8n instance
  ssh "$N8N_HOST" "docker exec -u node $N8N_CONTAINER n8n export:workflow \
    --all \
    --output=/files/tmp-finance-workflows.json"

  echo "→ Copying backup from container..."
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  scp "$N8N_HOST:/files/tmp-finance-workflows.json" \
    "$BACKUP_DIR/finance-workflows-$TIMESTAMP.json"

  echo "→ Cleaning up container temp file..."
  ssh "$N8N_HOST" "docker exec -u node $N8N_CONTAINER rm -f /files/tmp-finance-workflows.json"

  echo "✅ Backup complete: $BACKUP_DIR/finance-workflows-$TIMESTAMP.json"
}

restore() {
  echo "==> Restoring workflows from repo JSON files (per index.yaml)"

  while IFS=: read -r code id; do
    file=$(get_file_by_code "$code")

    # strip possible quotes
    file="${file//\"/}"

    if [[ -z "$file" ]]; then
      echo "⚠️  No file found for $code in index.yaml, skipping"
      continue
    fi

    if [[ ! -f "$REPO_ROOT/$file" ]]; then
      echo "⚠️  File not found: $REPO_ROOT/$file, skipping"
      continue
    fi

    echo "→ Importing $code ($id) from $file"
    ssh "$N8N_HOST" "docker exec -u node -i $N8N_CONTAINER n8n import:workflow --input=-" < "$REPO_ROOT/$file"
  done < <(get_workflow_ids)

  echo "✅ Restore/import complete."
}

activate() {
  echo "==> Activating all workflows from index.yaml"

  while IFS=: read -r code id; do
    echo "→ Activating $code (id=$id)"
    ssh "$N8N_HOST" "docker exec -u node $N8N_CONTAINER n8n update:workflow \
      --id=$id --active=true" || {
        echo "⚠️  Failed to activate $code (id=$id), continuing"
      }
  done < <(get_workflow_ids)

  echo "🔁 Remember: restart n8n for active flags to fully apply."
  echo "✅ Activation pass complete."
}

execute_code() {
  local code="$1"
  local id
  id="$(get_id_by_code "$code" || true)"

  if [[ -z "$id" ]]; then
    echo "❌ Unknown workflow code: $code (check $INDEX_FILE)"
    exit 1
  fi

  echo "==> Executing $code (id=$id) on $N8N_HOST"
  ssh "$N8N_HOST" "docker exec -u node $N8N_CONTAINER n8n execute --id $id"
}

list_workflows() {
  echo "==> Finance Ops Workflows (from $INDEX_FILE)"
  echo ""
  printf "%-25s %-4s %-40s %-10s\n" "CODE" "ID" "NAME" "CRITICAL"
  printf "%-25s %-4s %-40s %-10s\n" "----" "--" "----" "--------"

  awk '
    /^  - code:/ {
      sub("  - code: ","",$0); gsub("\"","",$0);
      code=$0
    }
    /    id:/ {id=$2}
    /    name:/ {
      sub("    name: ","",$0); gsub("\"","",$0);
      name=$0
    }
    /    critical:/ {
      critical=$2
      printf "%-25s %-4s %-40s %-10s\n", code, id, name, critical
    }
  ' "$INDEX_FILE"

  echo ""
}

status() {
  echo "==> n8n Workflow Status"
  echo "→ Fetching from $N8N_HOST"

  # Check which workflows are active
  while IFS=: read -r code id; do
    local active
    active=$(ssh "$N8N_HOST" "docker exec -u node $N8N_CONTAINER n8n workflow:list 2>/dev/null | grep -E '^$id\s' | awk '{print \$3}'" || echo "unknown")

    if [[ "$active" == "true" ]]; then
      echo "✅ $code (id=$id) - ACTIVE"
    elif [[ "$active" == "false" ]]; then
      echo "❌ $code (id=$id) - INACTIVE"
    else
      echo "⚠️  $code (id=$id) - STATUS UNKNOWN"
    fi
  done < <(get_workflow_ids)
}

case "${1:-}" in
  backup)
    backup
    ;;
  restore)
    restore
    ;;
  activate)
    activate
    ;;
  execute)
    if [[ -z "${2:-}" ]]; then
      echo "Usage: $0 execute <WORKFLOW_CODE>"
      exit 1
    fi
    execute_code "$2"
    ;;
  list)
    list_workflows
    ;;
  status)
    status
    ;;
  *)
    cat <<EOF
Usage: $0 <command>

Commands:
  backup          Export all current workflows to workflows/backups/*.json
  restore         Import workflows based on workflows/index.yaml
  activate        Activate all workflows in workflows/index.yaml
  execute CODE    Execute a single workflow by code (e.g. W001_OD_MNTH_CLOSE_SYNC)
  list            List all workflows from index.yaml
  status          Check active/inactive status of all workflows

Environment:
  N8N_CONTAINER   (default: odoo-ipa-1)
  N8N_HOST        (default: root@erp.insightpulseai.net)
  BACKUP_DIR      (default: \$REPO_ROOT/workflows/backups)

Examples:
  # Backup all workflows from production
  ./scripts/n8n-sync.sh backup

  # Restore workflows to production (after fresh install)
  ./scripts/n8n-sync.sh restore

  # Activate all workflows
  ./scripts/n8n-sync.sh activate

  # Execute monthly closing sync manually
  ./scripts/n8n-sync.sh execute W001_OD_MNTH_CLOSE_SYNC

  # List all registered workflows
  ./scripts/n8n-sync.sh list

  # Check workflow status
  ./scripts/n8n-sync.sh status
EOF
    exit 1
    ;;
esac
