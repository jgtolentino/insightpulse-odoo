#!/bin/bash
# deduplicate-archives.sh
# Deduplicate extracted archive contents by finding and removing duplicate files

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

EXTRACTED_DIR="/Users/tbwa/insightpulse-odoo/.extracted-archives"
DEDUP_LOG="${EXTRACTED_DIR}/deduplication-log.txt"

echo "=== Archive Deduplication ===" > "$DEDUP_LOG"
echo "Date: $(date)" >> "$DEDUP_LOG"
echo "" >> "$DEDUP_LOG"

log_info "Starting deduplication in: ${EXTRACTED_DIR}"

# Find all files and compute MD5 hashes
log_info "Computing file hashes..."
find "$EXTRACTED_DIR" -type f -not -path "*/\.*" -exec md5 -r {} \; | \
  sort | \
  awk '{
    hash=$1
    file=$2
    if (seen[hash]) {
      duplicates[hash] = duplicates[hash] " " file
      dup_count++
    } else {
      originals[hash] = file
      seen[hash] = 1
    }
  }
  END {
    print "Total files scanned:", NR
    print "Unique files:", length(originals)
    print "Duplicate files:", dup_count
    print ""
    print "=== Duplicates ==="
    for (hash in duplicates) {
      print "Original:", originals[hash]
      print "Duplicates:", duplicates[hash]
      print ""
    }
  }' | tee -a "$DEDUP_LOG"

# Count duplicates
DUPLICATE_COUNT=$(grep -c "Duplicates:" "$DEDUP_LOG" 2>/dev/null || echo "0")

if [ "$DUPLICATE_COUNT" -eq 0 ]; then
  log_success "No duplicates found"
  exit 0
fi

log_warning "Found ${DUPLICATE_COUNT} sets of duplicate files"

# Prompt for deletion
read -p "Delete duplicate files? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  log_info "Skipping deletion. Review log: ${DEDUP_LOG}"
  exit 0
fi

# Delete duplicates (keep first occurrence)
log_info "Deleting duplicate files..."
DELETED_COUNT=0

while IFS= read -r line; do
  if [[ $line == Duplicates:* ]]; then
    # Extract duplicate file paths
    duplicates=$(echo "$line" | sed 's/Duplicates: //')
    for dup_file in $duplicates; do
      if [ -f "$dup_file" ]; then
        rm "$dup_file"
        echo "Deleted: $dup_file" >> "$DEDUP_LOG"
        DELETED_COUNT=$((DELETED_COUNT + 1))
      fi
    done
  fi
done < "$DEDUP_LOG"

log_success "Deleted ${DELETED_COUNT} duplicate files"
log_info "Full log: ${DEDUP_LOG}"

# Summary
echo "" >> "$DEDUP_LOG"
echo "=== Summary ===" >> "$DEDUP_LOG"
echo "Duplicate sets found: ${DUPLICATE_COUNT}" >> "$DEDUP_LOG"
echo "Files deleted: ${DELETED_COUNT}" >> "$DEDUP_LOG"
echo "Space saved: $(du -sh ${EXTRACTED_DIR} | awk '{print $1}')" >> "$DEDUP_LOG"

log_success "Deduplication complete!"
