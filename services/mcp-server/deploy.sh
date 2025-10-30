#!/bin/bash
set -e

# MCP GitHub Server Deployment Script for DigitalOcean App Platform
# Usage: ./deploy.sh [create|update|status|logs]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_SPEC="${SCRIPT_DIR}/../../infra/do/mcp-github-server.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    log_error "doctl CLI not found. Install with: brew install doctl"
    exit 1
fi

# Check if authenticated
if ! doctl auth list &> /dev/null; then
    log_error "Not authenticated with DigitalOcean. Run: doctl auth init"
    exit 1
fi

# Function: Create new app
create_app() {
    log_info "Creating new MCP GitHub server app..."

    # Validate app spec
    if [ ! -f "$APP_SPEC" ]; then
        log_error "App spec not found: $APP_SPEC"
        exit 1
    fi

    log_info "Validating app spec..."
    if ! python -c "import yaml; yaml.safe_load(open('$APP_SPEC'))" 2>/dev/null; then
        log_error "Invalid YAML in app spec"
        exit 1
    fi

    # Create app
    log_info "Creating app from spec..."
    APP_ID=$(doctl apps create --spec "$APP_SPEC" --format ID --no-header)

    if [ -z "$APP_ID" ]; then
        log_error "Failed to create app"
        exit 1
    fi

    log_success "App created with ID: $APP_ID"
    echo "$APP_ID" > "${SCRIPT_DIR}/.app_id"

    # Wait for deployment
    log_info "Waiting for initial deployment..."
    wait_for_deployment "$APP_ID"

    # Get app URL
    APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
    log_success "App deployed: https://$APP_URL"

    # Test health endpoint
    log_info "Testing health endpoint..."
    sleep 10  # Wait for app to be ready
    if curl -sf "https://$APP_URL/health" > /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed - app may still be starting"
    fi

    log_success "Deployment complete!"
    echo ""
    log_info "App ID: $APP_ID"
    log_info "App URL: https://$APP_URL"
    log_info "MCP Endpoint: https://$APP_URL/mcp/github"
}

# Function: Update existing app
update_app() {
    # Get app ID
    if [ -f "${SCRIPT_DIR}/.app_id" ]; then
        APP_ID=$(cat "${SCRIPT_DIR}/.app_id")
    else
        log_error "App ID not found. Run 'create' first or set APP_ID environment variable"
        exit 1
    fi

    log_info "Updating app $APP_ID..."

    # Update app spec
    doctl apps update "$APP_ID" --spec "$APP_SPEC"
    log_success "App spec updated"

    # Create new deployment
    log_info "Creating new deployment..."
    DEPLOYMENT_ID=$(doctl apps create-deployment "$APP_ID" --force-rebuild --format ID --no-header)

    if [ -z "$DEPLOYMENT_ID" ]; then
        log_error "Failed to create deployment"
        exit 1
    fi

    log_success "Deployment created: $DEPLOYMENT_ID"

    # Wait for deployment
    wait_for_deployment "$APP_ID"

    # Get app URL
    APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)

    # Test health endpoint
    log_info "Testing health endpoint..."
    sleep 10
    if curl -sf "https://$APP_URL/health" | jq .; then
        log_success "Health check passed"
    else
        log_warning "Health check failed"
    fi

    log_success "Update complete!"
}

# Function: Wait for deployment
wait_for_deployment() {
    local APP_ID=$1
    local MAX_WAIT=1200  # 20 minutes
    local ELAPSED=0

    log_info "Waiting for deployment to complete..."

    while [ $ELAPSED -lt $MAX_WAIT ]; do
        # Get latest deployment status
        STATUS=$(doctl apps list-deployments "$APP_ID" --format Phase --no-header | head -1)

        if [ "$STATUS" == "ACTIVE" ]; then
            log_success "Deployment successful!"
            return 0
        elif [ "$STATUS" == "ERROR" ] || [ "$STATUS" == "CANCELED" ]; then
            log_error "Deployment failed with status: $STATUS"
            log_info "Fetching deployment logs..."
            doctl apps logs "$APP_ID" --type build || true
            return 1
        fi

        echo -n "."
        sleep 30
        ELAPSED=$((ELAPSED + 30))
    done

    log_error "Deployment timeout after ${MAX_WAIT}s"
    return 1
}

# Function: Show app status
show_status() {
    # Get app ID
    if [ -f "${SCRIPT_DIR}/.app_id" ]; then
        APP_ID=$(cat "${SCRIPT_DIR}/.app_id")
    else
        log_error "App ID not found. Run 'create' first"
        exit 1
    fi

    log_info "App Status for $APP_ID:"
    echo ""

    # Get app details
    doctl apps get "$APP_ID"

    echo ""
    log_info "Recent Deployments:"
    doctl apps list-deployments "$APP_ID" --format ID,Phase,Created | head -5

    # Get app URL
    APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
    echo ""
    log_info "Endpoints:"
    echo "  Health: https://$APP_URL/health"
    echo "  MCP: https://$APP_URL/mcp/github"

    # Test health
    echo ""
    log_info "Health Check:"
    if curl -sf "https://$APP_URL/health" | jq .; then
        log_success "Service is healthy"
    else
        log_error "Service health check failed"
    fi
}

# Function: Show logs
show_logs() {
    # Get app ID
    if [ -f "${SCRIPT_DIR}/.app_id" ]; then
        APP_ID=$(cat "${SCRIPT_DIR}/.app_id")
    else
        log_error "App ID not found. Run 'create' first"
        exit 1
    fi

    log_info "Fetching logs for $APP_ID..."
    echo ""

    # Show build logs
    log_info "Build Logs:"
    doctl apps logs "$APP_ID" --type build --follow=false || true

    echo ""
    # Show runtime logs
    log_info "Runtime Logs:"
    doctl apps logs "$APP_ID" --type run --follow
}

# Main script
case "${1:-}" in
    create)
        create_app
        ;;
    update)
        update_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {create|update|status|logs}"
        echo ""
        echo "Commands:"
        echo "  create  - Create new MCP server app"
        echo "  update  - Update existing app and redeploy"
        echo "  status  - Show app status and health"
        echo "  logs    - Show app logs"
        exit 1
        ;;
esac
