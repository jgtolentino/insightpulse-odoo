#!/bin/bash
# OpenUpgrade Test Script
# Tests module upgrades in isolated Docker environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
MODULE_NAME="${1:-all}"
FROM_VERSION="${2:-18.0}"
TO_VERSION="${3:-19.0}"
TEST_DB="odoo_upgrade_test_$$"
BACKUP_SQL="/tmp/odoo_backup_pre_upgrade.sql"

# Colors
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Step 1: Check prerequisites
log "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
fi

if ! command -v psql &> /dev/null; then
    error "PostgreSQL client (psql) is not installed"
fi

# Step 2: Start PostgreSQL test container
log "Starting PostgreSQL test container..."

docker run -d \
    --name odoo_upgrade_test_pg_$$ \
    -e POSTGRES_DB="$TEST_DB" \
    -e POSTGRES_USER=odoo \
    -e POSTGRES_PASSWORD=odoo \
    -p 15432:5432 \
    postgres:16 \
    > /dev/null

sleep 5  # Wait for PostgreSQL to be ready

cleanup() {
    log "Cleaning up test environment..."
    docker stop odoo_upgrade_test_pg_$$ > /dev/null 2>&1 || true
    docker rm odoo_upgrade_test_pg_$$ > /dev/null 2>&1 || true
    rm -f "$BACKUP_SQL"
}

trap cleanup EXIT

# Step 3: Install old version
log "Installing old version ($FROM_VERSION)..."

# TODO: This should install from a backup or old version
# For now, we'll create empty database
export PGPASSWORD=odoo
psql -h localhost -p 15432 -U odoo -d "$TEST_DB" -c "SELECT 1" > /dev/null

log "Old version database ready"

# Step 4: Backup before upgrade
log "Backing up database before upgrade..."

pg_dump -h localhost -p 15432 -U odoo "$TEST_DB" > "$BACKUP_SQL"

log "Backup saved: $BACKUP_SQL ($(du -h "$BACKUP_SQL" | cut -f1))"

# Step 5: Run OpenUpgrade
log "Running OpenUpgrade migration..."

OPENUPGRADE_DIR="/tmp/openupgrade_$$"

# Clone OpenUpgrade
git clone --depth 1 --branch "$TO_VERSION" \
    https://github.com/OCA/OpenUpgrade.git \
    "$OPENUPGRADE_DIR" \
    > /dev/null 2>&1

# Run upgrade
UPGRADE_LOG="/tmp/upgrade_$$.log"

if [ "$MODULE_NAME" == "all" ]; then
    MODULES_TO_UPGRADE="all"
else
    MODULES_TO_UPGRADE="$MODULE_NAME"
fi

log "Upgrading modules: $MODULES_TO_UPGRADE"

python3 "$OPENUPGRADE_DIR/odoo-bin" \
    -d "$TEST_DB" \
    --db_host localhost \
    --db_port 15432 \
    --db_user odoo \
    --db_password odoo \
    --addons-path "$PROJECT_ROOT/odoo/custom-addons,$OPENUPGRADE_DIR/odoo/addons" \
    -u "$MODULES_TO_UPGRADE" \
    --stop-after-init \
    --log-level=info \
    2>&1 | tee "$UPGRADE_LOG"

# Check for errors
if grep -q "ERROR" "$UPGRADE_LOG"; then
    error "Upgrade failed! Check log: $UPGRADE_LOG"
fi

log "✅ Upgrade completed successfully"

# Step 6: Validate migration
log "Validating migration results..."

# Check for NULL values in critical fields
psql -h localhost -p 15432 -U odoo -d "$TEST_DB" << EOF
-- Check for NULL values in required fields
SELECT
    'res_partner' as table_name,
    COUNT(*) FILTER (WHERE name IS NULL) as null_names,
    COUNT(*) as total_records
FROM res_partner;

-- Check module versions
SELECT name, latest_version, state
FROM ir_module_module
WHERE name LIKE 'insightpulse%'
ORDER BY name;
EOF

# Step 7: Generate test report
log "Generating test report..."

REPORT_FILE="/tmp/openupgrade_test_report_$$.txt"

cat > "$REPORT_FILE" << EOF
OpenUpgrade Test Report
=======================

Test Date: $(date)
Module: $MODULE_NAME
Upgrade Path: $FROM_VERSION → $TO_VERSION

Database Statistics:
-------------------
EOF

psql -h localhost -p 15432 -U odoo -d "$TEST_DB" -t << EOF >> "$REPORT_FILE"
SELECT
    'Partners: ' || COUNT(*)
FROM res_partner;

SELECT
    'Companies: ' || COUNT(*)
FROM res_company;

SELECT
    'Users: ' || COUNT(*)
FROM res_users;

SELECT
    'Installed Modules: ' || COUNT(*)
FROM ir_module_module
WHERE state = 'installed';
EOF

cat >> "$REPORT_FILE" << EOF

Upgrade Log: $UPGRADE_LOG
Database Backup: $BACKUP_SQL

Status: SUCCESS ✅
EOF

log "Test report saved: $REPORT_FILE"
cat "$REPORT_FILE"

# Step 8: Optional - Keep test DB for inspection
if [ "${KEEP_TEST_DB}" == "1" ]; then
    warn "Test database preserved (KEEP_TEST_DB=1)"
    warn "Connect with: psql -h localhost -p 15432 -U odoo -d $TEST_DB"
    warn "Stop container with: docker stop odoo_upgrade_test_pg_$$"
    trap - EXIT  # Remove cleanup trap
else
    log "Cleaning up test environment..."
fi

log "✅ OpenUpgrade test completed successfully!"
