#!/bin/bash
# Auto-Merge Rollback Script
#
# Safely rollback auto-merge changes if needed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Auto-Merge Rollback Tool"
echo "=========================="
echo ""

# Find backup files
BACKUPS=$(find . -name "*.backup" -type f 2>/dev/null)

if [ -z "$BACKUPS" ]; then
    echo "ℹ️  No backup files found"
    echo ""
    echo "Backups are created in the same directory as resolved files"
    echo "with a .backup extension."
    exit 0
fi

echo "Found backup files:"
echo "$BACKUPS" | nl
echo ""

# Count backups
BACKUP_COUNT=$(echo "$BACKUPS" | wc -l)
echo "Total: $BACKUP_COUNT backup file(s)"
echo ""

# Ask for confirmation
read -p "Restore all backups? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Rollback cancelled"
    exit 0
fi

echo ""
echo "Restoring backups..."
echo ""

# Restore each backup
while IFS= read -r backup; do
    original="${backup%.backup}"

    if [ -f "$original" ]; then
        echo "  Restoring: $original"
        mv "$backup" "$original"
    else
        echo "  ⚠️  Original file not found: $original"
        echo "      Backup preserved at: $backup"
    fi
done <<< "$BACKUPS"

echo ""
echo "✅ Rollback complete!"
echo ""
echo "Next steps:"
echo "1. Review restored files"
echo "2. Manually resolve conflicts if needed"
echo "3. Run: git add -u && git commit -m 'Rollback auto-merge'"
