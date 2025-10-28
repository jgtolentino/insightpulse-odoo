#!/usr/bin/env bash
#
# audit-modules.sh - Comprehensive module audit (Filesystem vs Database)
# Prints: module name, version from __manifest__.py, install state from DB, source path
#
# Usage: ./scripts/audit-modules.sh [database_name] [--output csv|table|json]
#
# Examples:
#   ./scripts/audit-modules.sh odoo_prod
#   ./scripts/audit-modules.sh odoo_prod --output csv > module_audit.csv
#   ./scripts/audit-modules.sh odoo_prod --output table | less -S

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}✅${NC} $1" >&2
}

log_error() {
    echo -e "${RED}❌${NC} $1" >&2
}

# Configuration
DB="${1:-odoo_prod}"
OUTPUT_FORMAT="${2:-table}"
if [[ "$OUTPUT_FORMAT" == "--output" ]]; then
    OUTPUT_FORMAT="${3:-table}"
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}" >&2
echo -e "${BLUE}║  Module Audit Tool - Filesystem vs Database                   ║${NC}" >&2
echo -e "${BLUE}║  Database: $DB${NC}" >&2
echo -e "${BLUE}║  Output: $OUTPUT_FORMAT${NC}" >&2
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}" >&2
echo "" >&2

# Check Docker is running
if ! docker info &>/dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

# Check Odoo container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "odoo"; then
    log_error "No Odoo container found"
    exit 1
fi

ODOO_CONTAINER=$(docker ps -a --format '{{.Names}}' | grep "odoo" | head -1)
log_info "Using container: $ODOO_CONTAINER" >&2
echo "" >&2

# Part 1: Filesystem manifests
log_info "Scanning filesystem for __manifest__.py files..." >&2

case "$OUTPUT_FORMAT" in
    csv)
        echo "name,fs_version,db_version,state,path,category,author"
        ;;
    json)
        echo "{"
        echo "  \"scan_date\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
        echo "  \"database\": \"$DB\","
        echo "  \"modules\": ["
        ;;
    table)
        log_success "Filesystem Manifests" >&2
        echo "" >&2
        ;;
esac

# Extract manifest data
FS_DATA=$(docker exec "$ODOO_CONTAINER" bash -c '
shopt -s nullglob
declare -A seen_modules

for manifest_path in \
    /mnt/extra-addons/custom/*/__manifest__.py \
    /mnt/extra-addons/oca/*/*/__manifest__.py \
    /usr/lib/python3/dist-packages/odoo/addons/*/__manifest__.py \
    /mnt/extra-addons/*/*/__manifest__.py; do

    if [[ ! -f "$manifest_path" ]]; then
        continue
    fi

    # Extract module technical name from path
    module_dir=$(dirname "$manifest_path")
    tech_name=$(basename "$module_dir")

    # Skip duplicates
    if [[ -n "${seen_modules[$tech_name]:-}" ]]; then
        continue
    fi
    seen_modules[$tech_name]=1

    # Parse manifest with Python
    manifest_data=$(python3 - "$manifest_path" <<PYPYTHON
import ast
import sys
import json

try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        manifest = ast.literal_eval(f.read())

    print(json.dumps({
        "name": manifest.get("name", ""),
        "version": manifest.get("version", ""),
        "category": manifest.get("category", ""),
        "author": manifest.get("author", ""),
        "installable": manifest.get("installable", True)
    }))
except Exception as e:
    print(json.dumps({"error": str(e)}))
PYPYTHON
)

    echo "$tech_name|$manifest_path|$manifest_data"
done
' 2>/dev/null)

# Part 2: Database states
log_info "Querying database for module states..." >&2

DB_DATA=$(docker exec "$ODOO_CONTAINER" bash -c "
psql -U \$PGUSER -d $DB -A -F'|' -t -c \"
SELECT name, latest_version, state
FROM ir_module_module
ORDER BY name;
\" 2>/dev/null
" || echo "")

# Combine and output
declare -A db_versions
declare -A db_states

while IFS='|' read -r name version state; do
    if [[ -n "$name" ]]; then
        db_versions["$name"]="$version"
        db_states["$name"]="$state"
    fi
done <<< "$DB_DATA"

FIRST_ENTRY=true
while IFS='|' read -r tech_name path manifest_json; do
    if [[ -z "$tech_name" ]]; then
        continue
    fi

    # Parse manifest JSON
    display_name=$(echo "$manifest_json" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('name',''))" 2>/dev/null || echo "")
    fs_version=$(echo "$manifest_json" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('version',''))" 2>/dev/null || echo "")
    category=$(echo "$manifest_json" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('category',''))" 2>/dev/null || echo "")
    author=$(echo "$manifest_json" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('author',''))" 2>/dev/null || echo "")

    db_version="${db_versions[$tech_name]:-}"
    state="${db_states[$tech_name]:-not_in_db}"

    case "$OUTPUT_FORMAT" in
        csv)
            echo "$tech_name,$fs_version,$db_version,$state,$path,$category,$author"
            ;;
        json)
            if [[ "$FIRST_ENTRY" == "false" ]]; then
                echo ","
            fi
            FIRST_ENTRY=false
            cat <<JSON
    {
      "technical_name": "$tech_name",
      "display_name": "$display_name",
      "fs_version": "$fs_version",
      "db_version": "$db_version",
      "state": "$state",
      "path": "$path",
      "category": "$category",
      "author": "$author"
    }
JSON
            ;;
        table)
            printf "%-40s %-15s %-15s %-15s\n" "$tech_name" "$fs_version" "$db_version" "$state"
            ;;
    esac
done <<< "$FS_DATA"

case "$OUTPUT_FORMAT" in
    json)
        echo ""
        echo "  ]"
        echo "}"
        ;;
    table)
        echo "" >&2
        log_info "Database-only modules (not on filesystem):" >&2
        echo "" >&2
        docker exec "$ODOO_CONTAINER" bash -c "
psql -U \$PGUSER -d $DB -A -F'|' -t -c \"
SELECT name, latest_version, state
FROM ir_module_module
WHERE name NOT IN (
    SELECT DISTINCT SUBSTRING(model FROM '^([^.]+)') AS tech_name
    FROM ir_model_data
    WHERE module IS NOT NULL
)
AND state != 'uninstalled'
ORDER BY name
LIMIT 20;
\" 2>/dev/null
" | while IFS='|' read -r name version state; do
            if [[ -n "$name" ]]; then
                printf "  ⚠️  %-40s %-15s %s\n" "$name" "$version" "$state" >&2
            fi
        done
        ;;
esac

# Summary statistics
if [[ "$OUTPUT_FORMAT" == "table" ]]; then
    echo "" >&2
    log_success "Audit Summary" >&2
    echo "" >&2

    TOTAL_FS=$(echo "$FS_DATA" | grep -c "|" || echo 0)
    TOTAL_DB=$(echo "$DB_DATA" | grep -c "|" || echo 0)
    INSTALLED=$(echo "$DB_DATA" | grep -c "installed" || echo 0)
    TO_UPGRADE=$(echo "$DB_DATA" | grep -c "to upgrade" || echo 0)
    UNINSTALLED=$(echo "$DB_DATA" | grep -c "uninstalled" || echo 0)

    echo "  📦 Modules on filesystem: $TOTAL_FS" >&2
    echo "  💾 Modules in database: $TOTAL_DB" >&2
    echo "  ✅ Installed: $INSTALLED" >&2
    if [[ $TO_UPGRADE -gt 0 ]]; then
        echo "  🔄 To upgrade: $TO_UPGRADE" >&2
    fi
    echo "  ❌ Uninstalled: $UNINSTALLED" >&2
    echo "" >&2

    log_info "Export options:" >&2
    echo "  CSV: ./scripts/audit-modules.sh $DB --output csv > audit.csv" >&2
    echo "  JSON: ./scripts/audit-modules.sh $DB --output json > audit.json" >&2
    echo "" >&2
fi

exit 0
