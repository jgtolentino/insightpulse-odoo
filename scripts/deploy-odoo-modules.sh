#!/bin/bash
###############################################################################
# deploy-odoo-modules.sh - Deploy IPAI Odoo modules to production
#
# Usage:
#   ./scripts/deploy-odoo-modules.sh [module1] [module2] ...
#   ./scripts/deploy-odoo-modules.sh --all
#
# Examples:
#   ./scripts/deploy-odoo-modules.sh ipai_expense
#   ./scripts/deploy-odoo-modules.sh ipai_expense ipai_equipment ipai_finance_monthly_closing
#   ./scripts/deploy-odoo-modules.sh --all
#
# Requirements:
#   - SSH access to root@erp.insightpulseai.net
#   - Git repository cloned locally
#   - Modules in addons/ directory
#
# What this script does:
#   1. Validates modules exist locally
#   2. Rsyncs modules to /opt/odoo/custom-addons/ on server
#   3. Restarts Odoo container
#   4. Optionally upgrades modules (with confirmation)
#   5. Checks Odoo health endpoint
#
# Based on: agents/AGENT_SKILLS_REGISTRY.yaml → deploy_odoo_module skill
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REMOTE_HOST="erp.insightpulseai.net"
REMOTE_USER="root"
REMOTE_ODOO_DIR="/opt/odoo/custom-addons"
LOCAL_ADDONS_DIR="addons"
ODOO_CONTAINER="odoo-odoo-1"
ODOO_DB="odoo"

# Available IPAI modules
AVAILABLE_MODULES=(
    "ipai_ce_cleaner"
    "ipai_expense"
    "ipai_equipment"
    "ipai_ocr_expense"
    "ipai_finance_monthly_closing"
)

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}==>${NC} $1"
}

# Function to check SSH connectivity
check_ssh_connection() {
    log_step "Checking SSH connection to ${REMOTE_USER}@${REMOTE_HOST}..."

    if ssh -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo 'SSH connection successful'" &>/dev/null; then
        log_success "SSH connection verified"
        return 0
    else
        log_error "Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}"
        log_error "Please ensure SSH key is configured: ssh-copy-id ${REMOTE_USER}@${REMOTE_HOST}"
        exit 1
    fi
}

# Function to validate module exists locally
validate_module() {
    local module=$1

    if [ ! -d "${LOCAL_ADDONS_DIR}/${module}" ]; then
        log_error "Module '${module}' not found in ${LOCAL_ADDONS_DIR}/"
        return 1
    fi

    if [ ! -f "${LOCAL_ADDONS_DIR}/${module}/__manifest__.py" ]; then
        log_error "Module '${module}' missing __manifest__.py"
        return 1
    fi

    log_success "Module '${module}' validated locally"
    return 0
}

# Function to check CE/OCA compliance
check_ce_compliance() {
    local module=$1
    local module_path="${LOCAL_ADDONS_DIR}/${module}"

    log_step "Checking CE/OCA compliance for ${module}..."

    # Check for Enterprise license
    if grep -r "OEEL" "${module_path}" &>/dev/null; then
        log_error "ENTERPRISE MODULE DETECTED: ${module} contains OEEL license"
        log_error "CE/OCA compliance check FAILED"
        return 1
    fi

    # Check for odoo.com links (except in comments)
    if grep -r "odoo\.com" "${module_path}" | grep -v "^[[:space:]]*#" &>/dev/null; then
        log_warning "Found odoo.com links in ${module} (may be in comments)"
    fi

    log_success "CE/OCA compliance check passed for ${module}"
    return 0
}

# Function to rsync module to server
deploy_module() {
    local module=$1

    log_step "Deploying ${module} to ${REMOTE_HOST}..."

    # Create remote directory if doesn't exist
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p ${REMOTE_ODOO_DIR}/${module}" || {
        log_error "Failed to create remote directory for ${module}"
        return 1
    }

    # Rsync module
    rsync -avz --delete \
        --exclude="*.pyc" \
        --exclude="__pycache__" \
        --exclude=".git" \
        "${LOCAL_ADDONS_DIR}/${module}/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_ODOO_DIR}/${module}/" || {
        log_error "Rsync failed for ${module}"
        return 1
    }

    log_success "Module ${module} deployed successfully"
    return 0
}

# Function to restart Odoo container
restart_odoo() {
    log_step "Restarting Odoo container..."

    ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker restart ${ODOO_CONTAINER}" || {
        log_error "Failed to restart Odoo container"
        return 1
    }

    log_info "Waiting 10 seconds for Odoo to start..."
    sleep 10

    log_success "Odoo container restarted"
    return 0
}

# Function to upgrade module in Odoo
upgrade_module() {
    local module=$1

    log_step "Upgrading module ${module} in Odoo..."

    ssh "${REMOTE_USER}@${REMOTE_HOST}" \
        "docker exec ${ODOO_CONTAINER} odoo -d ${ODOO_DB} -u ${module} --workers=0 --stop-after-init" || {
        log_error "Module upgrade failed for ${module}"
        log_error "Check Odoo logs: docker logs ${ODOO_CONTAINER} --tail 100"
        return 1
    }

    log_success "Module ${module} upgraded successfully"
    return 0
}

# Function to check Odoo health
check_odoo_health() {
    log_step "Checking Odoo health endpoint..."

    local health_status=$(curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/web/health || echo "000")

    if [ "${health_status}" = "200" ]; then
        log_success "Odoo health check passed (HTTP 200)"
        return 0
    else
        log_warning "Odoo health check returned HTTP ${health_status}"
        log_warning "This may be normal if health endpoint not configured"
        return 0
    fi
}

# Function to display deployment summary
display_summary() {
    local deployed_modules=("$@")

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "Deployment completed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📦 Deployed Modules:"
    for module in "${deployed_modules[@]}"; do
        echo "   ✅ ${module}"
    done
    echo ""
    echo "🔗 Access Odoo:"
    echo "   ${BLUE}https://erp.insightpulseai.net/web${NC}"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Log in to Odoo"
    echo "   2. Go to Apps → Update Apps List"
    echo "   3. Search for deployed modules"
    echo "   4. Install or upgrade as needed"
    echo ""
    echo "🔍 Check Logs (if issues):"
    echo "   ${BLUE}ssh root@erp.insightpulseai.net${NC}"
    echo "   ${BLUE}docker logs ${ODOO_CONTAINER} --tail 100${NC}"
    echo ""
}

# Main execution
main() {
    local modules_to_deploy=()

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  InsightPulse Odoo CE - Module Deployment"
    echo "  Target: ${REMOTE_USER}@${REMOTE_HOST}"
    echo "  Odoo Directory: ${REMOTE_ODOO_DIR}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Parse arguments
    if [ $# -eq 0 ]; then
        log_error "No modules specified"
        echo ""
        echo "Usage: $0 [module1] [module2] ... or --all"
        echo ""
        echo "Available modules:"
        for module in "${AVAILABLE_MODULES[@]}"; do
            echo "  - ${module}"
        done
        echo ""
        exit 1
    fi

    if [ "$1" = "--all" ]; then
        modules_to_deploy=("${AVAILABLE_MODULES[@]}")
        log_info "Deploying ALL modules: ${modules_to_deploy[*]}"
    else
        modules_to_deploy=("$@")
        log_info "Deploying modules: ${modules_to_deploy[*]}"
    fi

    echo ""

    # Validate modules locally
    log_step "Validating modules..."
    for module in "${modules_to_deploy[@]}"; do
        validate_module "${module}" || exit 1
        check_ce_compliance "${module}" || exit 1
    done

    echo ""

    # Check SSH connection
    check_ssh_connection

    echo ""

    # Deploy each module
    local deployed_count=0
    for module in "${modules_to_deploy[@]}"; do
        deploy_module "${module}" || {
            log_error "Deployment failed for ${module}, aborting"
            exit 1
        }
        ((deployed_count++))
    done

    echo ""

    # Restart Odoo
    restart_odoo || exit 1

    echo ""

    # Ask if user wants to upgrade modules
    echo ""
    read -p "Do you want to upgrade modules in Odoo now? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for module in "${modules_to_deploy[@]}"; do
            upgrade_module "${module}" || {
                log_warning "Failed to upgrade ${module}, continuing..."
            }
        done

        # Restart again after upgrades
        restart_odoo || exit 1
    else
        log_info "Skipping module upgrades - you can upgrade manually via Odoo UI"
    fi

    echo ""

    # Check health
    check_odoo_health

    # Display summary
    display_summary "${modules_to_deploy[@]}"
}

# Run main function
main "$@"
