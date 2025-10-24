#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Odoo Database Backup Script
# Creates timestamped database backups with compression
# ============================================================================

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/odoo_backup_${DATE}.sql.gz"

echo "═══════════════════════════════════════════════════════════════"
echo "  Odoo Database Backup"
echo "═══════════════════════════════════════════════════════════════"
echo "Backup file: $BACKUP_FILE"
echo "═══════════════════════════════════════════════════════════════"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform database backup
echo "▶ Starting database backup..."
docker compose exec -T postgres pg_dump -U odoo odoo | gzip > "$BACKUP_FILE"

# Verify backup was created
if [[ -f "$BACKUP_FILE" ]]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup completed successfully!"
    echo "   File: $BACKUP_FILE"
    echo "   Size: $BACKUP_SIZE"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Clean up old backups (keep last 30 days)
echo ""
echo "▶ Cleaning up old backups..."
find "$BACKUP_DIR" -name "odoo_backup_*.sql.gz" -mtime +30 -delete
echo "✅ Old backups cleaned up"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Backup Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "To restore this backup:"
echo "  gunzip -c $BACKUP_FILE | docker compose exec -T postgres psql -U odoo odoo"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "═══════════════════════════════════════════════════════════════"
