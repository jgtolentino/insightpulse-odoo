#!/usr/bin/env bash
# Export all Superset assets from runtime using Docker exec
set -euo pipefail

CONTAINER="${SUPERSET_CONTAINER:-superset}"
OUT="${1:-exports/runtime_dev}"

echo "=== Exporting assets from Superset container ==="
rm -rf "$OUT"
mkdir -p "$OUT"

# Export all dashboards (use /app path which has write permissions)
echo "  → Exporting dashboards..."
docker exec "$CONTAINER" superset export-dashboards -f /app/all_dashboards.zip

# Copy export from container
echo "  → Copying export from container..."
docker cp "$CONTAINER":/app/all_dashboards.zip "$OUT/"

# Extract the ZIP
echo "  → Extracting assets..."
cd "$OUT" && unzip -q all_dashboards.zip && cd - >/dev/null

echo ""
echo "✅ EXPORTED -> $OUT"
echo ""
echo "📊 Asset Summary:"
find "$OUT" -name "*.yaml" -type f | wc -l | xargs echo "  YAML files:"
du -sh "$OUT" | awk '{print "  Total size: " $1}'
