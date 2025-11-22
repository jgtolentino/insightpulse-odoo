#!/usr/bin/env bash
################################################################################
# Odoo CE Automated Backup Script
# Purpose: Daily backup of PostgreSQL database and filestore
# Usage: Runs automatically via cron (2 AM daily)
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="/opt/odoo-backups"
INSTALL_DIR="/opt/odoo-ce"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

log "Starting Odoo backup..."

# Load environment variables
if [ -f "$INSTALL_DIR/deploy/.env" ]; then
    # shellcheck disable=SC1091
    source "$INSTALL_DIR/deploy/.env"
else
    log "ERROR: .env file not found at $INSTALL_DIR/deploy/.env"
    exit 1
fi

# Backup database
log "Backing up PostgreSQL database..."
docker exec odoo-db pg_dumpall -U odoo | gzip > "$BACKUP_DIR/odoo-db-$TIMESTAMP.sql.gz"

# Backup filestore
log "Backing up filestore..."
docker exec odoo-ce tar czf - /var/lib/odoo > "$BACKUP_DIR/odoo-filestore-$TIMESTAMP.tar.gz"

# Backup configuration
log "Backing up configuration files..."
tar czf "$BACKUP_DIR/odoo-config-$TIMESTAMP.tar.gz" \
    -C "$INSTALL_DIR" \
    deploy/odoo.conf \
    deploy/docker-compose.yml \
    deploy/nginx/ \
    addons/ \
    2>/dev/null || true

# Calculate backup sizes
DB_SIZE=$(du -h "$BACKUP_DIR/odoo-db-$TIMESTAMP.sql.gz" | cut -f1)
FILESTORE_SIZE=$(du -h "$BACKUP_DIR/odoo-filestore-$TIMESTAMP.tar.gz" | cut -f1)
CONFIG_SIZE=$(du -h "$BACKUP_DIR/odoo-config-$TIMESTAMP.tar.gz" | cut -f1)

log "✅ Backup complete:"
log "  - Database: $DB_SIZE"
log "  - Filestore: $FILESTORE_SIZE"
log "  - Config: $CONFIG_SIZE"

# Cleanup old backups (keep last 7 days)
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "odoo-*.gz" -mtime +"$RETENTION_DAYS" -delete

# Count remaining backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "odoo-db-*.sql.gz" | wc -l)
log "Retained $BACKUP_COUNT database backups"

# Verify latest backup integrity
log "Verifying backup integrity..."
if gzip -t "$BACKUP_DIR/odoo-db-$TIMESTAMP.sql.gz"; then
    log "✅ Database backup integrity verified"
else
    log "❌ ERROR: Database backup integrity check failed!"
    exit 1
fi

log "Backup completed successfully"
