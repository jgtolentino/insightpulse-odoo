#!/usr/bin/env bash
###############################################################################
# Odoo Backup Script
#
# This script creates a backup of an Odoo database and uploads it to S3
# or saves it locally.
#
# Usage:
#   bash backup-odoo.sh <database_name> [s3_bucket]
#
# Run as: root or user with postgres access
# Environment variables:
#   AWS_ACCESS_KEY_ID     - AWS access key (if using S3)
#   AWS_SECRET_ACCESS_KEY - AWS secret key (if using S3)
#   AWS_DEFAULT_REGION    - AWS region (default: us-west-2)
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if database name provided
if [[ $# -eq 0 ]]; then
    log_error "Database name not provided"
    log_info "Usage: bash backup-odoo.sh <database_name> [s3_bucket]"
    exit 1
fi

DATABASE="$1"
S3_BUCKET="${2:-}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/var/backups/odoo}"
BACKUP_FILE="$BACKUP_DIR/${DATABASE}-${TIMESTAMP}.dump"
FILESTORE_BACKUP="$BACKUP_DIR/${DATABASE}-filestore-${TIMESTAMP}.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log_info "Starting backup of database: $DATABASE"

# Verify database exists
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DATABASE"; then
    log_error "Database '$DATABASE' does not exist"
    exit 1
fi

# Backup database
log_info "Backing up database..."
sudo -u postgres pg_dump -Fc "$DATABASE" > "$BACKUP_FILE"

if [[ -f "$BACKUP_FILE" ]]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_info "✓ Database backup created: $BACKUP_FILE ($BACKUP_SIZE)"
else
    log_error "Failed to create database backup"
    exit 1
fi

# Backup filestore
FILESTORE_PATH="/home/odoo/data/filestore/$DATABASE"
if [[ -d "$FILESTORE_PATH" ]]; then
    log_info "Backing up filestore..."
    tar -czf "$FILESTORE_BACKUP" -C "$(dirname "$FILESTORE_PATH")" "$(basename "$FILESTORE_PATH")"

    if [[ -f "$FILESTORE_BACKUP" ]]; then
        FILESTORE_SIZE=$(du -h "$FILESTORE_BACKUP" | cut -f1)
        log_info "✓ Filestore backup created: $FILESTORE_BACKUP ($FILESTORE_SIZE)"
    else
        log_warn "Failed to create filestore backup"
    fi
else
    log_warn "Filestore not found at $FILESTORE_PATH, skipping"
fi

# Upload to S3 if bucket specified
if [[ -n "$S3_BUCKET" ]]; then
    if command -v aws &> /dev/null; then
        log_info "Uploading backups to S3: $S3_BUCKET"

        # Upload database backup
        aws s3 cp "$BACKUP_FILE" "$S3_BUCKET/$(basename "$BACKUP_FILE")"
        log_info "✓ Database backup uploaded to S3"

        # Upload filestore backup if exists
        if [[ -f "$FILESTORE_BACKUP" ]]; then
            aws s3 cp "$FILESTORE_BACKUP" "$S3_BUCKET/$(basename "$FILESTORE_BACKUP")"
            log_info "✓ Filestore backup uploaded to S3"
        fi

        # Clean up old S3 backups (keep last 30 days)
        log_info "Cleaning up old S3 backups..."
        aws s3 ls "$S3_BUCKET/" | while read -r line; do
            createDate=$(echo "$line" | awk '{print $1" "$2}')
            createDate=$(date -d "$createDate" +%s 2>/dev/null || echo 0)
            olderThan=$(date -d "30 days ago" +%s)

            if [[ $createDate -lt $olderThan ]] && [[ $createDate -ne 0 ]]; then
                fileName=$(echo "$line" | awk '{print $4}')
                if [[ -n "$fileName" ]]; then
                    aws s3 rm "$S3_BUCKET/$fileName"
                    log_info "Deleted old backup: $fileName"
                fi
            fi
        done
    else
        log_warn "AWS CLI not found, skipping S3 upload"
    fi
fi

# Clean up old local backups (keep last 7 days)
log_info "Cleaning up old local backups..."
find "$BACKUP_DIR" -name "${DATABASE}-*.dump" -mtime +7 -delete
find "$BACKUP_DIR" -name "${DATABASE}-filestore-*.tar.gz" -mtime +7 -delete

log_info ""
log_info "✓ Backup complete!"
log_info "Database: $BACKUP_FILE ($BACKUP_SIZE)"
if [[ -f "$FILESTORE_BACKUP" ]]; then
    log_info "Filestore: $FILESTORE_BACKUP ($FILESTORE_SIZE)"
fi

if [[ -n "$S3_BUCKET" ]]; then
    log_info "S3 Location: $S3_BUCKET/"
fi

exit 0
