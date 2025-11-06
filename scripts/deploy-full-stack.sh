#!/bin/bash

# InsightPulse Odoo ERP SaaS + Mobile App - Full Stack Deployment Script
# Usage: ./scripts/deploy-full-stack.sh [--backend-only|--mobile-only|--all]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check for required tools
    local missing_tools=()

    if ! command_exists "gh"; then
        missing_tools+=("gh (GitHub CLI)")
    fi

    if ! command_exists "doctl"; then
        missing_tools+=("doctl (DigitalOcean CLI)")
    fi

    if ! command_exists "docker"; then
        missing_tools+=("docker")
    fi

    if ! command_exists "jq"; then
        missing_tools+=("jq")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools:"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo ""
        echo "Install missing tools:"
        echo "  macOS: brew install gh doctl docker jq"
        echo "  Linux: sudo snap install gh doctl && sudo apt install docker.io jq"
        exit 1
    fi

    log_success "All prerequisites installed"
}

# Check GitHub Secrets
check_github_secrets() {
    log_info "Checking GitHub Secrets..."

    local required_secrets=(
        "DO_APP_ID"
        "DO_ACCESS_TOKEN"
        "DIGITALOCEAN_ACCESS_TOKEN"
        "SUPABASE_PROJECT_REF"
        "SUPABASE_ACCESS_TOKEN"
        "CR_PAT"
        "SUPERSET_PASSWORD"
    )

    local missing_secrets=()

    for secret in "${required_secrets[@]}"; do
        if ! gh secret list | grep -q "$secret"; then
            missing_secrets+=("$secret")
        fi
    done

    if [ ${#missing_secrets[@]} -gt 0 ]; then
        log_error "Missing GitHub Secrets:"
        for secret in "${missing_secrets[@]}"; do
            echo "  - $secret"
        done
        echo ""
        echo "Set secrets with:"
        echo "  gh secret set SECRET_NAME"
        echo ""
        echo "See DEPLOYMENT_PLAN.md for details on how to obtain these values"
        exit 1
    fi

    log_success "All GitHub Secrets configured"
}

# Deploy backend infrastructure
deploy_backend() {
    log_info "Starting backend deployment..."

    # Step 1: Build and push Docker image
    log_info "Building Odoo Docker image..."

    local IMAGE_NAME="ghcr.io/jgtolentino/insightpulse-odoo"
    local IMAGE_TAG="prod-$(git rev-parse --short HEAD)"
    local IMAGE_FULL="${IMAGE_NAME}:${IMAGE_TAG}"
    local IMAGE_LATEST="${IMAGE_NAME}:latest-prod"

    docker build -t "$IMAGE_FULL" -t "$IMAGE_LATEST" .

    log_success "Docker image built: $IMAGE_FULL"

    log_info "Pushing to GitHub Container Registry..."
    docker push "$IMAGE_FULL"
    docker push "$IMAGE_LATEST"

    log_success "Docker image pushed"

    # Step 2: Deploy to DigitalOcean
    log_info "Deploying to DigitalOcean App Platform..."

    local DO_APP_ID=$(gh secret get DO_APP_ID --repo jgtolentino/insightpulse-odoo 2>/dev/null || echo "")

    if [ -z "$DO_APP_ID" ]; then
        log_error "DO_APP_ID secret not found. Please set it first."
        exit 1
    fi

    # Check if app exists
    if doctl apps get "$DO_APP_ID" >/dev/null 2>&1; then
        log_info "Updating existing app: $DO_APP_ID"
        doctl apps update "$DO_APP_ID" --spec infra/do/odoo-saas-platform.yaml
    else
        log_info "Creating new app..."
        doctl apps create --spec infra/do/odoo-saas-platform.yaml
    fi

    # Step 3: Create deployment
    log_info "Creating deployment..."
    local DEPLOYMENT_ID=$(doctl apps create-deployment "$DO_APP_ID" --format ID --no-header)

    log_success "Deployment created: $DEPLOYMENT_ID"

    # Step 4: Wait for deployment
    log_info "Waiting for deployment to complete (max 10 minutes)..."

    local MAX_WAIT=600
    local ELAPSED=0

    while [ $ELAPSED -lt $MAX_WAIT ]; do
        local PHASE=$(doctl apps deployments get "$DO_APP_ID" "$DEPLOYMENT_ID" --format Phase --no-header)

        echo -ne "  Status: $PHASE (${ELAPSED}s elapsed)\r"

        if [ "$PHASE" = "ACTIVE" ]; then
            echo ""
            log_success "Deployment successful!"
            break
        elif [ "$PHASE" = "ERROR" ] || [ "$PHASE" = "CANCELED" ]; then
            echo ""
            log_error "Deployment failed: $PHASE"
            log_info "Check logs with: doctl apps logs $DO_APP_ID --type=DEPLOY --follow"
            exit 1
        fi

        sleep 15
        ELAPSED=$((ELAPSED + 15))
    done

    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo ""
        log_warning "Deployment timeout after ${MAX_WAIT}s"
        log_info "Check status with: doctl apps get $DO_APP_ID"
        exit 1
    fi

    # Step 5: Deploy Superset (optional)
    read -p "Deploy Superset analytics? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_superset
    fi

    # Step 6: Deploy MCP Coordinator (optional)
    read -p "Deploy MCP Coordinator? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_mcp
    fi
}

# Deploy Superset
deploy_superset() {
    log_info "Deploying Superset Analytics..."

    if [ ! -f "infra/do/superset-app.yaml" ]; then
        log_warning "Superset spec not found: infra/do/superset-app.yaml"
        return
    fi

    doctl apps create --spec infra/do/superset-app.yaml

    log_success "Superset deployed"
}

# Deploy MCP Coordinator
deploy_mcp() {
    log_info "Deploying MCP Coordinator..."

    if [ ! -f "infra/do/mcp-coordinator.yaml" ]; then
        log_warning "MCP spec not found: infra/do/mcp-coordinator.yaml"
        return
    fi

    doctl apps create --spec infra/do/mcp-coordinator.yaml

    log_success "MCP Coordinator deployed"
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."

    local SERVICES=(
        "https://erp.insightpulseai.net/web/health"
        "https://superset.insightpulseai.net/health"
        "https://mcp.insightpulseai.net/health"
        "https://ade-ocr-backend-d9dru.ondigitalocean.app/health"
    )

    for service in "${SERVICES[@]}"; do
        echo -n "  Checking $service ... "
        if curl -s -o /dev/null -w "%{http_code}" "$service" | grep -q "200"; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    done
}

# Deploy mobile app
deploy_mobile() {
    log_info "Starting mobile app deployment..."

    cd mobile-companion

    # Check if EAS CLI is installed
    if ! command_exists "eas"; then
        log_info "Installing EAS CLI..."
        npm install -g eas-cli
    fi

    # Check if logged in
    if ! eas whoami >/dev/null 2>&1; then
        log_info "Logging in to Expo..."
        eas login
    fi

    # Install dependencies
    log_info "Installing dependencies..."
    npm install

    # Build for preview
    read -p "Build for which platform? (ios/android/all): " PLATFORM

    log_info "Building for $PLATFORM..."
    eas build --profile preview --platform "$PLATFORM"

    log_success "Mobile app build complete"

    cd ..
}

# Print deployment summary
print_summary() {
    echo ""
    echo "================================================"
    echo "  InsightPulse Deployment Summary"
    echo "================================================"
    echo ""
    echo "🌐 Service URLs:"
    echo "  Odoo ERP:     https://erp.insightpulseai.net"
    echo "  Superset:     https://superset.insightpulseai.net"
    echo "  MCP:          https://mcp.insightpulseai.net"
    echo "  OCR Service:  https://ade-ocr-backend-d9dru.ondigitalocean.app"
    echo ""
    echo "🔑 Credentials:"
    echo "  Odoo Admin:   admin / (ODOO_ADMIN_PASSWORD)"
    echo "  Superset:     admin / (SUPERSET_PASSWORD)"
    echo ""
    echo "📱 Mobile App:"
    echo "  Build:        Check Expo dashboard"
    echo "  Download:     https://expo.dev/accounts/your-account/projects/insightpulse-expense-companion"
    echo ""
    echo "📊 Next Steps:"
    echo "  1. Configure DNS (see infra/DNS_CONFIGURATION.md)"
    echo "  2. Import Superset dashboards (superset/dashboards/*.json)"
    echo "  3. Test mobile app flows"
    echo "  4. Submit to App Stores (eas submit)"
    echo ""
    echo "📚 Documentation:"
    echo "  DEPLOYMENT_PLAN.md"
    echo "  infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md"
    echo ""
}

# Main function
main() {
    echo ""
    echo "================================================"
    echo "  InsightPulse Odoo ERP SaaS Deployment"
    echo "================================================"
    echo ""

    local DEPLOYMENT_TYPE="${1:-all}"

    case $DEPLOYMENT_TYPE in
        --backend-only)
            check_prerequisites
            check_github_secrets
            deploy_backend
            run_health_checks
            print_summary
            ;;
        --mobile-only)
            check_prerequisites
            deploy_mobile
            print_summary
            ;;
        --all|*)
            check_prerequisites
            check_github_secrets
            deploy_backend
            run_health_checks

            read -p "Deploy mobile app? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                deploy_mobile
            fi

            print_summary
            ;;
    esac

    log_success "Deployment complete! 🎉"
}

# Run main function
main "$@"
