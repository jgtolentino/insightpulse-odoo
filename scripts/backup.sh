#!/bin/bash
#########################################################################
# Backup Script for InsightPulse AI
# Backs up Odoo database, filestore, and configuration
# Usage: ./backup.sh [manual|scheduled|pre-deployment]
#########################################################################

set -e  # Exit on error

# Configuration
BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_TYPE="${1:-manual}"
LOG_FILE="$BACKUP_DIR/backup-$TIMESTAMP.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "========================================"
log "InsightPulse AI Backup - $BACKUP_TYPE"
log "========================================"

# Check if Odoo container is running
if ! docker ps | grep -q odoo; then
    error "Odoo container is not running"
    exit 1
fi

# Check if PostgreSQL container is running
if ! docker ps | grep -q odoo-postgres; then
    error "PostgreSQL container is not running"
    exit 1
fi

FILENAME_BASE="odoo-${BACKUP_TYPE}-${TIMESTAMP}"

#########################################################################
# 1. Backup Odoo Database
#########################################################################
log "Step 1/5: Backing up Odoo database..."

docker exec odoo-postgres pg_dump -U odoo odoo | gzip > "$BACKUP_DIR/$FILENAME_BASE.sql.gz"

if [ $? -eq 0 ]; then
    DB_SIZE=$(du -h "$BACKUP_DIR/$FILENAME_BASE.sql.gz" | cut -f1)
    log "✅ Database backup completed: $DB_SIZE"
else
    error "Database backup failed"
    exit 1
fi

#########################################################################
# 2. Backup Odoo Filestore
#########################################################################
log "Step 2/5: Backing up Odoo filestore..."

# Create temporary filestore backup inside container
docker exec odoo tar czf /tmp/filestore-backup.tar.gz /var/lib/odoo/filestore 2>/dev/null

# Copy to backup directory
docker cp odoo:/tmp/filestore-backup.tar.gz "$BACKUP_DIR/$FILENAME_BASE-filestore.tar.gz"

# Clean up temporary file
docker exec odoo rm /tmp/filestore-backup.tar.gz

if [ $? -eq 0 ]; then
    FS_SIZE=$(du -h "$BACKUP_DIR/$FILENAME_BASE-filestore.tar.gz" | cut -f1)
    log "✅ Filestore backup completed: $FS_SIZE"
else
    error "Filestore backup failed"
    exit 1
fi

#########################################################################
# 3. Backup Odoo Configuration
#########################################################################
log "Step 3/5: Backing up Odoo configuration..."

if [ -f /opt/insightpulse-odoo/services/odoo/odoo.conf ]; then
    cp /opt/insightpulse-odoo/services/odoo/odoo.conf "$BACKUP_DIR/$FILENAME_BASE-odoo.conf"
    log "✅ Configuration backup completed"
else
    warn "odoo.conf not found, skipping"
fi

#########################################################################
# 4. Generate Checksums
#########################################################################
log "Step 4/5: Generating checksums..."

cd "$BACKUP_DIR"
sha256sum "$FILENAME_BASE.sql.gz" > "$FILENAME_BASE.sql.gz.sha256"
sha256sum "$FILENAME_BASE-filestore.tar.gz" > "$FILENAME_BASE-filestore.tar.gz.sha256"

log "✅ Checksums generated"

#########################################################################
# 5. Verify Backup Integrity
#########################################################################
log "Step 5/5: Verifying backup integrity..."

# Verify checksums
sha256sum -c "$FILENAME_BASE.sql.gz.sha256" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    log "✅ Database checksum verified"
else
    error "Database checksum verification failed"
    exit 1
fi

sha256sum -c "$FILENAME_BASE-filestore.tar.gz.sha256" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    log "✅ Filestore checksum verified"
else
    error "Filestore checksum verification failed"
    exit 1
fi

# Test gunzip without extracting
gunzip -t "$FILENAME_BASE.sql.gz" 2>/dev/null
if [ $? -eq 0 ]; then
    log "✅ Database archive integrity verified"
else
    error "Database archive is corrupted"
    exit 1
fi

#########################################################################
# 6. Upload to DigitalOcean Spaces (Optional)
#########################################################################
if command -v s3cmd &> /dev/null; then
    log "Uploading to DigitalOcean Spaces..."
    
    s3cmd put "$FILENAME_BASE.sql.gz" s3://insightpulse-backups/odoo/ 2>&1 | tee -a "$LOG_FILE"
    s3cmd put "$FILENAME_BASE-filestore.tar.gz" s3://insightpulse-backups/odoo/ 2>&1 | tee -a "$LOG_FILE"
    s3cmd put "$FILENAME_BASE.sql.gz.sha256" s3://insightpulse-backups/odoo/ 2>&1 | tee -a "$LOG_FILE"
    s3cmd put "$FILENAME_BASE-filestore.tar.gz.sha256" s3://insightpulse-backups/odoo/ 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "✅ Uploaded to DigitalOcean Spaces"
    else
        warn "Upload to DigitalOcean Spaces failed (continuing anyway)"
    fi
else
    warn "s3cmd not installed, skipping cloud upload"
fi

#########################################################################
# 7. Cleanup Old Backups
#########################################################################
log "Cleaning up old backups..."

# Keep last 7 days of manual/scheduled backups
find "$BACKUP_DIR" -name "odoo-manual-*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "odoo-scheduled-*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "odoo-*-filestore.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.sha256" -mtime +7 -delete

# Keep last 30 days of pre-deployment backups
find "$BACKUP_DIR" -name "odoo-pre-deployment-*.sql.gz" -mtime +30 -delete

# Keep last 90 days of log files
find "$BACKUP_DIR" -name "backup-*.log" -mtime +90 -delete

log "✅ Old backups cleaned up"

#########################################################################
# 8. Backup Summary
#########################################################################
log "========================================"
log "Backup Summary"
log "========================================"
log "Backup Type: $BACKUP_TYPE"
log "Timestamp: $TIMESTAMP"
log "Database Size: $DB_SIZE"
log "Filestore Size: $FS_SIZE"
log "Backup Location: $BACKUP_DIR"
log "Files:"
log "  - $FILENAME_BASE.sql.gz"
log "  - $FILENAME_BASE-filestore.tar.gz"
log "  - $FILENAME_BASE.sql.gz.sha256"
log "  - $FILENAME_BASE-filestore.tar.gz.sha256"
log "========================================"
log "✅ Backup completed successfully!"
log "========================================"

# Return backup filename for use in scripts
echo "$FILENAME_BASE"

exit 0
