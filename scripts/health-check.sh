#!/bin/bash
# InsightPulseAI Health Check Script
# Run every 5 minutes via cron

set -e

LOG_FILE="/var/log/insightpulse-health.log"
ALERT_EMAIL="admin@insightpulseai.net"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to send alert
send_alert() {
    local service=$1
    local message=$2
    echo "$message" | mail -s "InsightPulseAI Alert: $service DOWN" "$ALERT_EMAIL"
    log "ALERT SENT: $service - $message"
}

# Check Odoo
if curl -fsS https://insightpulseai.net/odoo >/dev/null; then
    log "✅ Odoo Health: OK"
else
    log "❌ Odoo Health: FAILED"
    send_alert "Odoo" "Odoo service is not responding at https://insightpulseai.net/odoo"
fi

# Check OCR Service
if curl -fsS https://insightpulseai.net/ocr/health >/dev/null; then
    log "✅ OCR Health: OK"
else
    log "❌ OCR Health: FAILED"
    send_alert "OCR" "OCR service is not responding at https://insightpulseai.net/ocr/health"
fi

# Check LangChain Service
if curl -fsS https://insightpulseai.net/agent/health >/dev/null; then
    log "✅ LangChain Health: OK"
else
    log "⚠️ LangChain Health: FAILED (502 expected during development)"
    # Don't send alert for LangChain as it's expected to return 502 during development
fi

# Check container status
if docker compose ps | grep -q "unhealthy"; then
    log "❌ Some containers are unhealthy"
    send_alert "Containers" "Some Docker containers are unhealthy. Check with: docker compose ps"
else
    log "✅ All containers healthy"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log "⚠️ Disk usage high: ${DISK_USAGE}%"
    send_alert "Disk" "Disk usage is at ${DISK_USAGE}%. Consider cleaning up."
fi

log "Health check completed"
