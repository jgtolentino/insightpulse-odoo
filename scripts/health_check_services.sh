#!/usr/bin/env bash
# Health check script with retry logic
# Usage: ./health_check.sh <url> <max_retries> <wait_seconds>

set -euo pipefail

URL="${1:-http://localhost:8069/web/login}"
MAX_RETRIES="${2:-20}"
WAIT_SECONDS="${3:-15}"

echo "🏥 Health check: $URL"
echo "📊 Max retries: $MAX_RETRIES, Wait: ${WAIT_SECONDS}s"

for i in $(seq 1 "$MAX_RETRIES"); do
    echo "Attempt $i/$MAX_RETRIES..."
    
    if curl -fsSL --max-time 10 "$URL" >/dev/null 2>&1; then
        echo "✅ Health check passed!"
        exit 0
    fi
    
    if [ "$i" -lt "$MAX_RETRIES" ]; then
        echo "⏳ Waiting ${WAIT_SECONDS}s before retry..."
        sleep "$WAIT_SECONDS"
    fi
done

echo "❌ Health check failed after $MAX_RETRIES attempts"
exit 1
