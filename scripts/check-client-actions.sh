#!/usr/bin/env bash
#
# check-client-actions.sh - Guardrail to prevent KeyNotFoundError in JS action registry
# Lists client action tags from DB and ensures each has a JS registry handler
#
# Usage: ./scripts/check-client-actions.sh [database_name]
#
# CI Integration: Fail CI if there are missing JS handlers
# Exit code: 0 = all good, 1 = missing handlers found

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Configuration
DB="${1:-odoo_prod}"
ODOO_CONTAINER=$(docker ps --format '{{.Names}}' | grep "odoo" | head -1 || echo "")

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Client Action Guardrail - Prevent KeyNotFoundError           ║${NC}"
echo -e "${BLUE}║  Database: $DB${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker
if ! docker info &>/dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

if [[ -z "$ODOO_CONTAINER" ]]; then
    log_error "No Odoo container found"
    exit 1
fi

log_info "Using container: $ODOO_CONTAINER"
echo ""

# Step 1: Extract client action tags from database
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/3] Extracting client action tags from database${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

DB_ACTIONS=$(docker exec "$ODOO_CONTAINER" bash -c "
psql -U \$PGUSER -d $DB -t -c \"
SELECT DISTINCT tag
FROM ir_act_client
WHERE tag IS NOT NULL AND tag != ''
ORDER BY tag;
\" 2>/dev/null
" | tr -d ' \r' | grep -v '^$' || echo "")

if [[ -z "$DB_ACTIONS" ]]; then
    log_warning "No client actions found in database"
    echo ""
    log_success "Nothing to check - no client actions registered"
    exit 0
fi

ACTION_COUNT=$(echo "$DB_ACTIONS" | wc -l | tr -d ' ')
log_info "Found $ACTION_COUNT client action(s) in database:"
echo "$DB_ACTIONS" | while read -r tag; do
    echo "  📋 $tag"
done
echo ""

# Step 2: Extract JS action registry handlers from codebase
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/3] Scanning JavaScript for action registry handlers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

JS_ACTIONS=$(docker exec "$ODOO_CONTAINER" bash -c "
# Search for registry.category('actions').add('action_name', ...)
# Common patterns:
#   registry.category('actions').add('my_action', MyAction)
#   registry.category(\"actions\").add(\"my_action\", MyAction)
#   registry.category(\\\`actions\\\`).add(\\\`my_action\\\`, MyAction)

grep -rhoP \"registry\\.category\\(['\\\"\\\\\\\`]actions['\\\"\\\\\\\`]\\)\\.add\\(['\\\"\\\\\\\`]\\K[^'\\\"\\\\\\\\\\`]+\" \
    /mnt/extra-addons \
    /mnt/oca-addons \
    /usr/lib/python3/dist-packages/odoo/addons \
    2>/dev/null | sort -u || true
" || echo "")

if [[ -z "$JS_ACTIONS" ]]; then
    log_warning "No JS action registry handlers found in codebase"
    log_info "This may indicate missing static/src files or incorrect pattern matching"
else
    HANDLER_COUNT=$(echo "$JS_ACTIONS" | wc -l | tr -d ' ')
    log_info "Found $HANDLER_COUNT action handler(s) in JavaScript:"
    echo "$JS_ACTIONS" | head -20 | while read -r handler; do
        echo "  🔧 $handler"
    done
    if [[ $HANDLER_COUNT -gt 20 ]]; then
        echo "  ... and $((HANDLER_COUNT - 20)) more"
    fi
fi
echo ""

# Step 3: Compare and report missing handlers
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/3] Identifying missing JS handlers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

MISSING_ACTIONS=""
MISSING_COUNT=0

while read -r db_action; do
    if [[ -z "$db_action" ]]; then
        continue
    fi

    # Check if action exists in JS handlers
    if ! echo "$JS_ACTIONS" | grep -qF "$db_action"; then
        MISSING_ACTIONS="$MISSING_ACTIONS$db_action"$'\n'
        ((MISSING_COUNT++))
    fi
done <<< "$DB_ACTIONS"

if [[ $MISSING_COUNT -eq 0 ]]; then
    log_success "All client actions have corresponding JS handlers!"
    echo ""
    log_info "Validation passed:"
    echo "  ✅ $ACTION_COUNT action(s) in database"
    echo "  ✅ All have JS registry handlers"
    echo ""
    exit 0
else
    log_error "Found $MISSING_COUNT missing JS handler(s)"
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}Missing JS Handlers (will cause KeyNotFoundError)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    echo "$MISSING_ACTIONS" | grep -v '^$' | while read -r missing; do
        echo "  ❌ $missing"
    done
    echo ""

    log_warning "Recommended fixes:"
    echo ""
    echo "1. Add JS handler for each missing action:"
    echo ""
    cat <<'JSEXAMPLE'
   // static/src/registry.js
   /** @odoo-module */
   import { registry } from "@web/core/registry";

   function MyAction(env, action) {
       // Your action implementation
       env.services.notification.add("Action executed", { type: "info" });
       return { clean: () => {} };
   }

   registry.category("actions").add("my_action_tag", MyAction);
JSEXAMPLE
    echo ""
    echo "2. Add to module's __manifest__.py:"
    echo ""
    cat <<'MANIFESTEXAMPLE'
   "assets": {
       "web.assets_backend": [
           "module_name/static/src/registry.js"
       ]
   }
MANIFESTEXAMPLE
    echo ""
    echo "3. Or uninstall modules that register these actions if not needed"
    echo ""

    log_error "CI/CD should fail - missing JS handlers detected"
    exit 1
fi
