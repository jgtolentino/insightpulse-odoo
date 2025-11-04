#!/bin/bash
#########################################################################
# Restore Script for InsightPulse AI
# Restores Odoo database and filestore from backup
# Usage: ./restore.sh <backup-filename>
# Example: ./restore.sh odoo-manual-20251104-020000
#########################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR:${NC} Please run as root"
    exit 1
fi

# Check if backup filename provided
if [ -z "$1" ]; then
    echo -e "${RED}ERROR:${NC} Please provide backup filename"
    echo "Usage: $0 <backup-filename>"
    echo "Example: $0 odoo-manual-20251104-020000"
    echo ""
    echo "Available backups:"
    ls -lh /backup/*.sql.gz | awk '{print $9}' | sed 's/.*\///' | sed 's/.sql.gz//'
    exit 1
fi

BACKUP_DIR="/backup"
FILENAME_BASE="$1"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$BACKUP_DIR/restore-$TIMESTAMP.log"

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "InsightPulse AI Restore"
log "========================================"

#########################################################################
# 1. Verify Backup Files Exist
#########################################################################
log "Step 1/7: Verifying backup files..."

if [ ! -f "$BACKUP_DIR/$FILENAME_BASE.sql.gz" ]; then
    error "Database backup file not found: $BACKUP_DIR/$FILENAME_BASE.sql.gz"
    exit 1
fi

if [ ! -f "$BACKUP_DIR/$FILENAME_BASE-filestore.tar.gz" ]; then
    error "Filestore backup file not found: $BACKUP_DIR/$FILENAME_BASE-filestore.tar.gz"
    exit 1
fi

log "✅ Backup files found"

#########################################################################
# 2. Verify Backup Integrity
#########################################################################
log "Step 2/7: Verifying backup integrity..."

if [ -f "$BACKUP_DIR/$FILENAME_BASE.sql.gz.sha256" ]; then
    cd "$BACKUP_DIR"
    sha256sum -c "$FILENAME_BASE.sql.gz.sha256" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log "✅ Database checksum verified"
    else
        error "Database checksum verification failed"
        exit 1
    fi
else
    warn "No checksum file found, skipping verification"
fi

# Test gunzip without extracting
gunzip -t "$BACKUP_DIR/$FILENAME_BASE.sql.gz" 2>/dev/null
if [ $? -eq 0 ]; then
    log "✅ Database archive integrity verified"
else
    error "Database archive is corrupted"
    exit 1
fi

#########################################################################
# 3. Confirmation Prompt
#########################################################################
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will replace the current database!${NC}"
echo ""
echo "Backup to restore: $FILENAME_BASE"
echo "Current database: odoo"
echo ""
echo "A backup of the current database will be created first."
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

#########################################################################
# 4. Backup Current Database (Safety)
#########################################################################
log "Step 3/7: Creating safety backup of current database..."

SAFETY_BACKUP="odoo-pre-restore-$TIMESTAMP"
docker exec odoo-postgres pg_dump -U odoo odoo | gzip > "$BACKUP_DIR/$SAFETY_BACKUP.sql.gz"

if [ $? -eq 0 ]; then
    log "✅ Safety backup created: $SAFETY_BACKUP.sql.gz"
else
    error "Safety backup failed. Aborting restore."
    exit 1
fi

#########################################################################
# 5. Stop Odoo Container
#########################################################################
log "Step 4/7: Stopping Odoo container..."

docker stop odoo
if [ $? -eq 0 ]; then
    log "✅ Odoo stopped"
else
    error "Failed to stop Odoo"
    exit 1
fi

#########################################################################
# 6. Restore Database
#########################################################################
log "Step 5/7: Restoring database..."

# Drop and recreate database
docker exec odoo-postgres psql -U postgres -c "DROP DATABASE IF EXISTS odoo;"
docker exec odoo-postgres psql -U postgres -c "CREATE DATABASE odoo OWNER odoo;"

# Restore from backup
gunzip -c "$BACKUP_DIR/$FILENAME_BASE.sql.gz" | docker exec -i odoo-postgres psql -U odoo odoo

if [ $? -eq 0 ]; then
    log "✅ Database restored successfully"
else
    error "Database restore failed"
    log "Attempting to restore safety backup..."
    gunzip -c "$BACKUP_DIR/$SAFETY_BACKUP.sql.gz" | docker exec -i odoo-postgres psql -U odoo odoo
    exit 1
fi

#########################################################################
# 7. Restore Filestore
#########################################################################
log "Step 6/7: Restoring filestore..."

# Extract filestore to temporary location
TEMP_DIR="/tmp/odoo-filestore-restore-$TIMESTAMP"
mkdir -p "$TEMP_DIR"
tar -xzf "$BACKUP_DIR/$FILENAME_BASE-filestore.tar.gz" -C "$TEMP_DIR"

# Stop Odoo container if still running
docker stop odoo 2>/dev/null || true

# Remove old filestore
docker exec odoo-postgres rm -rf /var/lib/odoo/filestore/* 2>/dev/null || true

# Copy new filestore
docker cp "$TEMP_DIR/var/lib/odoo/filestore/." odoo:/var/lib/odoo/filestore/

# Clean up temporary directory
rm -rf "$TEMP_DIR"

if [ $? -eq 0 ]; then
    log "✅ Filestore restored successfully"
else
    error "Filestore restore failed"
    exit 1
fi

#########################################################################
# 8. Start Odoo Container
#########################################################################
log "Step 7/7: Starting Odoo container..."

docker start odoo
if [ $? -eq 0 ]; then
    log "✅ Odoo started"
else
    error "Failed to start Odoo"
    exit 1
fi

# Wait for Odoo to be ready
log "Waiting for Odoo to be ready..."
for i in {1..60}; do
    if curl -s -f http://localhost:8069/web/health > /dev/null 2>&1; then
        log "✅ Odoo is healthy"
        break
    fi
    
    if [ $i -eq 60 ]; then
        error "Odoo failed to start properly"
        exit 1
    fi
    
    sleep 2
done

#########################################################################
# 9. Restore Summary
#########################################################################
log "========================================"
log "Restore Summary"
log "========================================"
log "Restored From: $FILENAME_BASE"
log "Safety Backup: $SAFETY_BACKUP.sql.gz"
log "Restore Time: $(date '+%Y-%m-%d %H:%M:%S')"
log "========================================"
log "✅ Restore completed successfully!"
log "========================================"
log ""
log "Next steps:"
log "1. Verify data integrity: curl https://erp.insightpulseai.net/web/health"
log "2. Test login: https://erp.insightpulseai.net"
log "3. Check Finance SSC module"
log "4. Run smoke tests: ./scripts/health-check.sh"
log ""
log "Safety backup location: $BACKUP_DIR/$SAFETY_BACKUP.sql.gz"
log ""

exit 0
