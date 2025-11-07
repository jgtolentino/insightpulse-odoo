#!/bin/bash
# Superset health check with auto-restart

set -e

MAX_RETRIES=3
RETRY_DELAY=10
SUPERSET_URL="${SUPERSET_URL:-https://superset.insightpulseai.net}"
SUPERSET_APP_ID="${SUPERSET_APP_ID}"

check_superset_health() {
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout 10 \
            --max-time 30 \
            "$SUPERSET_URL/health" || echo "000")

        if [ "$HTTP_CODE" = "200" ]; then
            echo "✅ Superset healthy (HTTP $HTTP_CODE)"
            return 0
        fi

        echo "⚠️  Superset unhealthy (HTTP $HTTP_CODE) - retry $((retries+1))/$MAX_RETRIES"
        retries=$((retries+1))

        if [ $retries -lt $MAX_RETRIES ]; then
            sleep $RETRY_DELAY
        fi
    done

    echo "❌ Superset unresponsive after $MAX_RETRIES retries"
    return 1
}

check_database() {
    echo "🔍 Checking Superset database backend..."

    # Check if using PostgreSQL (not SQLite)
    if [ -n "$DATABASE_URL" ]; then
        if [[ "$DATABASE_URL" == sqlite* ]]; then
            echo "❌ ERROR: Superset using SQLite - not allowed in production"
            return 1
        elif [[ "$DATABASE_URL" == postgresql* ]] || [[ "$DATABASE_URL" == postgres* ]]; then
            echo "✅ Using PostgreSQL backend"

            # Test database connection
            if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
                echo "✅ Database connection successful"
                return 0
            else
                echo "❌ Database connection failed"
                return 1
            fi
        fi
    else
        echo "⚠️  DATABASE_URL not set"
        return 1
    fi
}

restart_superset() {
    echo "🔄 Restarting Superset..."

    if [ -n "$SUPERSET_APP_ID" ]; then
        # DigitalOcean App Platform
        echo "Triggering deployment on DigitalOcean App Platform..."
        doctl apps create-deployment "$SUPERSET_APP_ID" --force-rebuild

        echo "⏳ Waiting for deployment to complete..."
        sleep 60

        # Verify deployment
        STATUS=$(doctl apps get "$SUPERSET_APP_ID" --format Status --no-header)
        echo "Deployment status: $STATUS"

    else
        # Docker Compose
        echo "Restarting via Docker Compose..."
        docker-compose -f services/superset/docker-compose.superset.yml restart
        sleep 10
    fi

    echo "✅ Restart complete"
}

# Main execution
echo "🏥 Superset Health Check - $(date)"

# Check database first
if ! check_database; then
    echo "❌ Database check failed - manual intervention required"
    exit 1
fi

# Check Superset health
if ! check_superset_health; then
    echo "🔄 Attempting auto-heal..."

    # Restart Superset
    restart_superset

    # Re-check health
    sleep 30
    if check_superset_health; then
        echo "✅ Auto-heal successful"
        exit 0
    else
        echo "❌ Auto-heal failed - escalating to ops team"
        # Send alert
        if [ -n "$SLACK_WEBHOOK_URL" ]; then
            curl -X POST "$SLACK_WEBHOOK_URL" \
                -H "Content-Type: application/json" \
                -d "{\"text\":\"🚨 Superset auto-heal failed - manual intervention required\"}"
        fi
        exit 1
    fi
fi

echo "✅ All checks passed"
exit 0
