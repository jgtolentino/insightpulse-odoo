#!/usr/bin/env bash
###############################################################################
# Pull-Based Deployment Script for Odoo Production
#
# This script performs fast pull-based upgrades by pulling the latest
# container images and restarting services, instead of rebuilding on droplet.
#
# Usage:
#   bash deploy-all.sh [--skip-git-pull]
#
# Run from: /opt/odoo (or repo root directory on droplet)
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - Repository cloned to /opt/odoo
#   - Services defined in docker-compose.yml (or override file)
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Parse arguments
SKIP_GIT_PULL=false
for arg in "$@"; do
    case $arg in
        --skip-git-pull)
        SKIP_GIT_PULL=true
        shift
        ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "============================================"
log_info "  Pull-Based Production Deployment"
log_info "  InsightPulse AI"
log_info "============================================"
echo ""

log_info "Repository: $REPO_ROOT"
echo ""

# Step 1: Git pull (unless skipped)
if [ "$SKIP_GIT_PULL" = false ]; then
    log_step "Step 1/3: Pulling latest code from Git"
    cd "$REPO_ROOT"

    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warn "Uncommitted changes detected. Stashing them..."
        git stash
    fi

    # Pull latest changes
    log_info "Pulling from $(git remote get-url origin)..."
    git pull || {
        log_error "Git pull failed"
        exit 1
    }

    log_info "✅ Git pull complete"
    echo ""
else
    log_warn "Skipping git pull (--skip-git-pull flag set)"
    echo ""
fi

# Step 2: Docker Compose pull
log_step "Step 2/3: Pulling latest container images"
cd "$REPO_ROOT"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found in $REPO_ROOT"
    exit 1
fi

log_info "Pulling images defined in docker-compose.yml..."
docker compose pull || {
    log_error "docker compose pull failed"
    exit 1
}

log_info "✅ Image pull complete"
echo ""

# Step 3: Docker Compose up
log_step "Step 3/3: Restarting services with latest images"

log_info "Starting services with docker compose up -d --remove-orphans..."
docker compose up -d --remove-orphans || {
    log_error "docker compose up failed"
    exit 1
}

log_info "✅ Services restarted"
echo ""

# Wait for services to stabilize
log_info "Waiting 10 seconds for services to stabilize..."
sleep 10

# Show running containers
log_info "Running containers:"
docker compose ps
echo ""

log_info "============================================"
log_info "  Deployment Complete!"
log_info "============================================"
echo ""

log_info "Service Management:"
log_info "  View logs:    docker compose logs -f"
log_info "  Check status: docker compose ps"
log_info "  Restart:      docker compose restart [service]"
echo ""

log_info "Next Step: Run smoke test to verify deployment"
log_info "  curl -s -o /dev/null -w \"%{http_code}\" https://erp.insightpulseai.net/web/login"
echo ""

exit 0
