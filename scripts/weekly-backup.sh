#!/bin/bash
# InsightPulseAI Weekly Backup Script
# Run weekly at 3 AM Sunday via cron

set -e

BACKUP_DIR="/Users/tbwa/insightpulse-odoo/backups"
DATE=$(date +%Y%m%d)
RETENTION_WEEKS=4

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$BACKUP_DIR/backup.log"
}

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

log "Starting weekly backup for $DATE"

# Database backup (same as daily)
log "Creating database backup..."
docker exec -T postgres pg_dump -U odoo odoo | gzip > "$BACKUP_DIR/odoo_${DATE}.sql.gz"
if [ $? -eq 0 ]; then
    log "✅ Database backup created: odoo_${DATE}.sql.gz"
else
    log "❌ Database backup failed"
    exit 1
fi

# Filestore backup
log "Creating filestore backup..."
if [ -d "/var/lib/docker/volumes/insightpulse-odoo-odoo_data/_data" ]; then
    tar czf "$BACKUP_DIR/filestore_${DATE}.tgz" -C /var/lib/docker/volumes/insightpulse-odoo-odoo_data/_data .
    log "✅ Filestore backup created: filestore_${DATE}.tgz"
else
    log "⚠️ Filestore directory not found, skipping"
fi

# OCA modules backup
log "Creating OCA modules backup..."
if [ -d "addons/oca" ]; then
    tar czf "$BACKUP_DIR/oca_modules_${DATE}.tgz" addons/oca/
    log "✅ OCA modules backup created: oca_modules_${DATE}.tgz"
else
    log "⚠️ OCA modules directory not found, skipping"
fi

# Verify all backups
log "Verifying backups..."
if gzip -t "$BACKUP_DIR/odoo_${DATE}.sql.gz"; then
    log "✅ Database backup verified"
else
    log "❌ Database backup verification failed"
    exit 1
fi

if [ -f "$BACKUP_DIR/filestore_${DATE}.tgz" ]; then
    if tar -tzf "$BACKUP_DIR/filestore_${DATE}.tgz" >/dev/null 2>&1; then
        log "✅ Filestore backup verified"
    else
        log "❌ Filestore backup verification failed"
    fi
fi

if [ -f "$BACKUP_DIR/oca_modules_${DATE}.tgz" ]; then
    if tar -tzf "$BACKUP_DIR/oca_modules_${DATE}.tgz" >/dev/null 2>&1; then
        log "✅ OCA modules backup verified"
    else
        log "❌ OCA modules backup verification failed"
    fi
fi

# Clean up old weekly backups (keep 4 weeks)
log "Cleaning up old weekly backups..."
find "$BACKUP_DIR" -name "filestore_*.tgz" -mtime +$((RETENTION_WEEKS * 7)) -delete
find "$BACKUP_DIR" -name "oca_modules_*.tgz" -mtime +$((RETENTION_WEEKS * 7)) -delete

log "Weekly backup completed successfully"

# Report backup sizes
log "Backup sizes:"
if [ -f "$BACKUP_DIR/odoo_${DATE}.sql.gz" ]; then
    DB_SIZE=$(du -h "$BACKUP_DIR/odoo_${DATE}.sql.gz" | cut -f1)
    log "  Database: $DB_SIZE"
fi
if [ -f "$BACKUP_DIR/filestore_${DATE}.tgz" ]; then
    FS_SIZE=$(du -h "$BACKUP_DIR/filestore_${DATE}.tgz" | cut -f1)
    log "  Filestore: $FS_SIZE"
fi
if [ -f "$BACKUP_DIR/oca_modules_${DATE}.tgz" ]; then
    OCA_SIZE=$(du -h "$BACKUP_DIR/oca_modules_${DATE}.tgz" | cut -f1)
    log "  OCA Modules: $OCA_SIZE"
fi
