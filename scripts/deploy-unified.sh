# Unified Deployment Master Script
# Consolidates all deployment paths for InsightPulse platform

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Configuration
DEPLOYMENT_TYPE="${1:-full}"  # full, odoo, superset, paddleocr, traefik
ENVIRONMENT="${2:-production}"  # production, staging

# Banner
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     InsightPulse Unified Deployment System v2.0          ║
║     Complete Platform Deployment Automation              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

log_info "Deployment Type: $DEPLOYMENT_TYPE"
log_info "Environment: $ENVIRONMENT"
echo ""

# Functions
check_prerequisites() {
    log_step "Checking prerequisites..."

    local missing=()

    if ! command -v doctl &> /dev/null; then
        missing+=("doctl")
    fi

    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi

    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        exit 1
    fi

    # Check doctl authentication
    if ! doctl auth list | grep -q "current"; then
        log_error "doctl not authenticated. Run: doctl auth init"
        exit 1
    fi

    log_info "All prerequisites satisfied"
}

deploy_odoo() {
    log_step "Deploying Odoo ERP to DigitalOcean App Platform..."

    local spec_file="infra/do/odoo-saas-platform.yaml"

    if [ "$ENVIRONMENT" = "staging" ]; then
        spec_file="infra/do/odoo-saas-platform-staging.yaml"
    fi

    if [ ! -f "$spec_file" ]; then
        log_error "Spec file not found: $spec_file"
        exit 1
    fi

    # Check if app exists
    local app_name="odoo-saas-platform"
    if [ "$ENVIRONMENT" = "staging" ]; then
        app_name="odoo-saas-platform-staging"
    fi

    local app_id=$(doctl apps list --format ID,Spec.Name --no-header | grep "$app_name" | awk '{print $1}' || echo "")

    if [ -z "$app_id" ]; then
        log_info "Creating new Odoo app..."
        app_id=$(doctl apps create --spec "$spec_file" --format ID --no-header)
        log_info "App created: $app_id"
    else
        log_info "Updating existing Odoo app: $app_id"
        doctl apps update "$app_id" --spec "$spec_file"
    fi

    # Trigger deployment
    log_info "Triggering deployment..."
    doctl apps create-deployment "$app_id" --force-rebuild

    # Monitor deployment
    log_info "Monitoring deployment (this may take 5-10 minutes)..."
    monitor_deployment "$app_id"

    log_info "✅ Odoo deployment complete"
}

deploy_superset() {
    log_step "Deploying Superset Analytics to DigitalOcean App Platform..."

    local spec_file="infra/superset/superset-app.yaml"
    local app_name="superset-analytics"

    if [ ! -f "$spec_file" ]; then
        log_error "Spec file not found: $spec_file"
        exit 1
    fi

    local app_id=$(doctl apps list --format ID,Spec.Name --no-header | grep "$app_name" | awk '{print $1}' || echo "")

    if [ -z "$app_id" ]; then
        log_info "Creating new Superset app..."
        app_id=$(doctl apps create --spec "$spec_file" --format ID --no-header)
        log_info "App created: $app_id"
    else
        log_info "Updating existing Superset app: $app_id"
        doctl apps update "$app_id" --spec "$spec_file"
    fi

    # Trigger deployment
    log_info "Triggering deployment..."
    doctl apps create-deployment "$app_id" --force-rebuild

    # Monitor deployment
    log_info "Monitoring deployment (this may take 6-10 minutes)..."
    monitor_deployment "$app_id"

    log_info "✅ Superset deployment complete"
}

deploy_paddleocr() {
    log_step "Deploying PaddleOCR Service to DigitalOcean Droplet..."

    if [ -x "infra/paddleocr/deploy-droplet.sh" ]; then
        cd infra/paddleocr
        ./deploy-droplet.sh
        cd ../..
    else
        log_error "PaddleOCR deployment script not found or not executable"
        exit 1
    fi

    log_info "✅ PaddleOCR deployment complete"
}

deploy_traefik() {
    log_step "Deploying Traefik Reverse Proxy..."

    if [ -x "infra/reverse-proxy/deploy.sh" ]; then
        cd infra/reverse-proxy
        ./deploy.sh
        cd ../..
    else
        log_error "Traefik deployment script not found or not executable"
        exit 1
    fi

    log_info "✅ Traefik deployment complete"
}

monitor_deployment() {
    local app_id="$1"
    local max_attempts=40
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        local phase=$(doctl apps get "$app_id" --format ActiveDeployment.Phase --no-header)

        case "$phase" in
            "ACTIVE")
                log_info "Deployment is ACTIVE"
                return 0
                ;;
            "ERROR"|"CANCELED")
                log_error "Deployment failed: $phase"
                log_error "View logs: doctl apps logs $app_id --type build"
                return 1
                ;;
            *)
                echo -n "."
                sleep 15
                ;;
        esac

        attempt=$((attempt + 1))
    done

    log_warn "Deployment monitoring timed out. Check status manually."
    return 1
}

health_check() {
    log_step "Running health checks..."

    # Check Odoo
    local odoo_url="https://odoo-saas-platform-xxxxx.ondigitalocean.app/web/health"
    if curl -sf "$odoo_url" > /dev/null 2>&1; then
        log_info "✅ Odoo health check passed"
    else
        log_warn "❌ Odoo health check failed"
    fi

    # Check Superset
    local superset_url="https://superset-analytics-xxxxx.ondigitalocean.app/health"
    if curl -sf "$superset_url" > /dev/null 2>&1; then
        log_info "✅ Superset health check passed"
    else
        log_warn "❌ Superset health check failed"
    fi
}

# Main deployment logic
main() {
    check_prerequisites

    case "$DEPLOYMENT_TYPE" in
        full)
            log_info "Deploying complete InsightPulse platform..."
            deploy_traefik
            deploy_paddleocr
            deploy_odoo
            deploy_superset
            health_check
            ;;
        odoo)
            deploy_odoo
            ;;
        superset)
            deploy_superset
            ;;
        paddleocr)
            deploy_paddleocr
            ;;
        traefik)
            deploy_traefik
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            echo ""
            echo "Usage: $0 [deployment-type] [environment]"
            echo ""
            echo "Deployment types:"
            echo "  full       - Deploy all services (default)"
            echo "  odoo       - Deploy Odoo ERP only"
            echo "  superset   - Deploy Superset only"
            echo "  paddleocr  - Deploy PaddleOCR service only"
            echo "  traefik    - Deploy Traefik proxy only"
            echo ""
            echo "Environments:"
            echo "  production - Production environment (default)"
            echo "  staging    - Staging environment"
            echo ""
            exit 1
            ;;
    esac

    echo ""
    log_info "═══════════════════════════════════════════"
    log_info "  Deployment Complete! 🎉"
    log_info "═══════════════════════════════════════════"
    echo ""
}

# Run main function
main "$@"
