#!/bin/bash
# InsightPulseAI Daily Backup Script
# Run daily at 2 AM via cron

set -e

BACKUP_DIR="/Users/tbwa/insightpulse-odoo/backups"
DATE=$(date +%Y%m%d)
RETENTION_DAYS=7

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$BACKUP_DIR/backup.log"
}

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

log "Starting daily backup for $DATE"

# Database backup
log "Creating database backup..."
docker exec -T postgres pg_dump -U odoo odoo | gzip > "$BACKUP_DIR/odoo_${DATE}.sql.gz"
if [ $? -eq 0 ]; then
    log "✅ Database backup created: odoo_${DATE}.sql.gz"
else
    log "❌ Database backup failed"
    exit 1
fi

# Verify database backup
if gzip -t "$BACKUP_DIR/odoo_${DATE}.sql.gz"; then
    log "✅ Database backup verified"
else
    log "❌ Database backup verification failed"
    exit 1
fi

# Clean up old backups (keep 7 days)
log "Cleaning up old backups..."
find "$BACKUP_DIR" -name "odoo_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "filestore_*.tgz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "oca_modules_*.tgz" -mtime +28 -delete  # Keep monthly OCA backups

log "Daily backup completed successfully"

# Report backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/odoo_${DATE}.sql.gz" | cut -f1)
log "Backup size: $BACKUP_SIZE"
