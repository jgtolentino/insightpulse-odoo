#!/usr/bin/env bash
set -euo pipefail

# Guardrail: Block known Odoo 19.x-only API patterns
# Usage: ./check_api_mismatches.sh

echo "=== Checking for Odoo 19.x API patterns ==="

ERROR_COUNT=0

# Check for 19.x-only groups API
if grep -R -n -E "res\.groups\.user_ids|group_id\.user_ids" /mnt/addons /mnt/oca 2>/dev/null; then
  echo "✗ Detected 19.x-only groups API usage (res.groups.user_ids)"
  ERROR_COUNT=$((ERROR_COUNT + 1))
fi

# Check for other potential 19.x patterns
# Add more patterns as needed

if [ $ERROR_COUNT -gt 0 ]; then
  echo ""
  echo "✗ API check failed with $ERROR_COUNT error(s)"
  echo "  Please fix 19.x-only API usage before proceeding"
  exit 1
fi

echo "✓ API check passed - no 19.x-only patterns detected"
exit 0
