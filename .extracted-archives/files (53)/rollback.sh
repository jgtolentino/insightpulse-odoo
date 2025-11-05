#!/bin/bash
#########################################################################
# Rollback Script for InsightPulse AI
# Rolls back to previous deployment version
# Usage: ./rollback.sh [service]
# Services: odoo, mcp, superset, ocr, all
#########################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVICE="${1:-all}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="/var/log/rollback-$TIMESTAMP.log"

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
log "InsightPulse AI Rollback - $SERVICE"
log "========================================"

#########################################################################
# Rollback Odoo
#########################################################################
rollback_odoo() {
    log "Rolling back Odoo..."
    
    # List available images
    IMAGES=$(docker images | grep "registry.digitalocean.com/insightpulse/odoo-erp" | awk '{print $2}' | grep -v "latest" | head -n 5)
    
    if [ -z "$IMAGES" ]; then
        error "No previous Odoo images found"
        return 1
    fi
    
    echo ""
    echo "Available Odoo versions:"
    echo "$IMAGES" | nl
    echo ""
    read -p "Select version number to rollback to: " VERSION_NUM
    
    SELECTED_TAG=$(echo "$IMAGES" | sed -n "${VERSION_NUM}p")
    
    if [ -z "$SELECTED_TAG" ]; then
        error "Invalid selection"
        return 1
    fi
    
    log "Selected tag: $SELECTED_TAG"
    
    # Backup current database before rollback
    log "Creating pre-rollback backup..."
    /opt/insightpulse-odoo/scripts/backup.sh pre-rollback
    
    # Stop current container
    log "Stopping current Odoo container..."
    docker stop odoo || true
    docker rm odoo || true
    
    # Start container with previous image
    log "Starting Odoo with tag: $SELECTED_TAG"
    docker run -d \
      --name odoo \
      --restart unless-stopped \
      -p 8069:8069 \
      -v odoo-web-data:/var/lib/odoo \
      -v /opt/insightpulse-odoo/services/odoo/addons:/mnt/extra-addons \
      -e POSTGRES_USER=odoo \
      -e POSTGRES_PASSWORD=${ODOO_DB_PASSWORD} \
      -e POSTGRES_DB=odoo \
      --link odoo-postgres:db \
      registry.digitalocean.com/insightpulse/odoo-erp:$SELECTED_TAG
    
    # Wait for Odoo to start
    log "Waiting for Odoo to be ready..."
    for i in {1..60}; do
        if curl -s -f http://localhost:8069/web/health > /dev/null 2>&1; then
            log "✅ Odoo rollback successful"
            return 0
        fi
        sleep 2
    done
    
    error "Odoo failed to start after rollback"
    return 1
}

#########################################################################
# Rollback MCP
#########################################################################
rollback_mcp() {
    log "Rolling back MCP Coordinator..."
    
    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        error "doctl is not installed"
        return 1
    fi
    
    # Get MCP app ID
    MCP_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "mcp-coordinator" | awk '{print $1}')
    
    if [ -z "$MCP_APP_ID" ]; then
        error "MCP app not found"
        return 1
    fi
    
    # List recent deployments
    log "Fetching recent deployments..."
    DEPLOYMENTS=$(doctl apps list-deployments $MCP_APP_ID --format ID,Created,Phase --no-header | head -n 10)
    
    echo ""
    echo "Recent MCP deployments:"
    echo "$DEPLOYMENTS" | nl
    echo ""
    read -p "Select deployment number to rollback to: " DEPLOY_NUM
    
    SELECTED_DEPLOY=$(echo "$DEPLOYMENTS" | sed -n "${DEPLOY_NUM}p" | awk '{print $1}')
    
    if [ -z "$SELECTED_DEPLOY" ]; then
        error "Invalid selection"
        return 1
    fi
    
    log "Rolling back to deployment: $SELECTED_DEPLOY"
    doctl apps create-deployment $MCP_APP_ID $SELECTED_DEPLOY
    
    log "✅ MCP rollback initiated"
    log "Monitor progress: doctl apps get-deployment $MCP_APP_ID $SELECTED_DEPLOY"
}

#########################################################################
# Rollback Superset
#########################################################################
rollback_superset() {
    log "Rolling back Superset..."
    
    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        error "doctl is not installed"
        return 1
    fi
    
    # Get Superset app ID
    SUPERSET_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "superset" | awk '{print $1}')
    
    if [ -z "$SUPERSET_APP_ID" ]; then
        error "Superset app not found"
        return 1
    fi
    
    # List recent deployments
    log "Fetching recent deployments..."
    DEPLOYMENTS=$(doctl apps list-deployments $SUPERSET_APP_ID --format ID,Created,Phase --no-header | head -n 10)
    
    echo ""
    echo "Recent Superset deployments:"
    echo "$DEPLOYMENTS" | nl
    echo ""
    read -p "Select deployment number to rollback to: " DEPLOY_NUM
    
    SELECTED_DEPLOY=$(echo "$DEPLOYMENTS" | sed -n "${DEPLOY_NUM}p" | awk '{print $1}')
    
    if [ -z "$SELECTED_DEPLOY" ]; then
        error "Invalid selection"
        return 1
    fi
    
    log "Rolling back to deployment: $SELECTED_DEPLOY"
    doctl apps create-deployment $SUPERSET_APP_ID $SELECTED_DEPLOY
    
    log "✅ Superset rollback initiated"
    log "Monitor progress: doctl apps get-deployment $SUPERSET_APP_ID $SELECTED_DEPLOY"
}

#########################################################################
# Rollback OCR
#########################################################################
rollback_ocr() {
    log "Rolling back OCR Service..."
    
    # List available images
    IMAGES=$(docker images | grep "registry.digitalocean.com/insightpulse/ocr-service" | awk '{print $2}' | grep -v "latest" | head -n 5)
    
    if [ -z "$IMAGES" ]; then
        error "No previous OCR images found"
        return 1
    fi
    
    echo ""
    echo "Available OCR versions:"
    echo "$IMAGES" | nl
    echo ""
    read -p "Select version number to rollback to: " VERSION_NUM
    
    SELECTED_TAG=$(echo "$IMAGES" | sed -n "${VERSION_NUM}p")
    
    if [ -z "$SELECTED_TAG" ]; then
        error "Invalid selection"
        return 1
    fi
    
    log "Selected tag: $SELECTED_TAG"
    
    # Stop current container
    log "Stopping current OCR container..."
    docker stop ocr || true
    docker rm ocr || true
    
    # Start container with previous image
    log "Starting OCR with tag: $SELECTED_TAG"
    docker run -d \
      --name ocr \
      --restart unless-stopped \
      -p 8080:8080 \
      -v /opt/paddleocr/models:/root/.paddleocr \
      -e LOG_LEVEL=INFO \
      registry.digitalocean.com/insightpulse/ocr-service:$SELECTED_TAG
    
    # Wait for OCR to start
    log "Waiting for OCR to be ready..."
    for i in {1..30}; do
        if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
            log "✅ OCR rollback successful"
            return 0
        fi
        sleep 2
    done
    
    error "OCR failed to start after rollback"
    return 1
}

#########################################################################
# Main Execution
#########################################################################
case "$SERVICE" in
    odoo)
        rollback_odoo
        ;;
    mcp)
        rollback_mcp
        ;;
    superset)
        rollback_superset
        ;;
    ocr)
        rollback_ocr
        ;;
    all)
        echo ""
        echo "Rollback all services? This will:"
        echo "  1. Rollback Odoo (with database backup)"
        echo "  2. Rollback MCP Coordinator"
        echo "  3. Rollback Superset"
        echo "  4. Rollback OCR Service"
        echo ""
        read -p "Are you sure? (yes/no): " CONFIRM
        
        if [ "$CONFIRM" = "yes" ]; then
            rollback_odoo
            rollback_mcp
            rollback_superset
            rollback_ocr
        else
            log "Rollback cancelled"
            exit 0
        fi
        ;;
    *)
        error "Invalid service: $SERVICE"
        echo "Usage: $0 [service]"
        echo "Services: odoo, mcp, superset, ocr, all"
        exit 1
        ;;
esac

log "========================================"
log "Rollback Summary"
log "========================================"
log "Service: $SERVICE"
log "Timestamp: $TIMESTAMP"
log "Log File: $LOG_FILE"
log "========================================"
log "✅ Rollback completed"
log "========================================"
log ""
log "Next steps:"
log "1. Run health checks: ./scripts/health-check.sh"
log "2. Verify service functionality"
log "3. Monitor logs for errors"
log ""

exit 0
