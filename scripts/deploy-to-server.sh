#!/bin/bash
###############################################################################
# deploy-to-server.sh - Deploy health check scripts to erp.insightpulseai.net
#
# Usage:
#   ./scripts/deploy-to-server.sh [--env prod|staging|dev]
#
# Requirements:
#   - SSH access to root@erp.insightpulseai.net
#   - Git repository cloned locally
#
# What this script does:
#   1. Creates directory structure on remote server
#   2. Copies scripts to server
#   3. Copies SQL schema to server
#   4. Sets proper permissions
#   5. Validates deployment
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_HOST="erp.insightpulseai.net"
REMOTE_USER="root"
REMOTE_BASE_DIR="/opt/odoo-ce"
ENV="${1:-prod}"

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

# Function to check SSH connectivity
check_ssh_connection() {
    log_info "Checking SSH connection to ${REMOTE_USER}@${REMOTE_HOST}..."

    if ssh -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo 'SSH connection successful'" &>/dev/null; then
        log_success "SSH connection verified"
        return 0
    else
        log_error "Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}"
        log_error "Please ensure:"
        log_error "  1. SSH key is configured: ssh-copy-id ${REMOTE_USER}@${REMOTE_HOST}"
        log_error "  2. Server is reachable"
        exit 1
    fi
}

# Function to create remote directory structure
create_remote_directories() {
    log_info "Creating remote directory structure..."

    ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        mkdir -p ${REMOTE_BASE_DIR}/scripts
        mkdir -p ${REMOTE_BASE_DIR}/notion-n8n-monthly-close/scripts
        mkdir -p ${REMOTE_BASE_DIR}/packages/db/sql
    " || {
        log_error "Failed to create remote directories"
        exit 1
    }

    log_success "Remote directories created"
}

# Function to copy files to server
copy_files_to_server() {
    log_info "Copying files to server..."

    # Copy check_project_tasks.py
    log_info "  → Copying scripts/check_project_tasks.py"
    scp scripts/check_project_tasks.py \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_DIR}/scripts/" || {
        log_error "Failed to copy check_project_tasks.py"
        exit 1
    }

    # Copy verify_finance_stack.sh
    log_info "  → Copying notion-n8n-monthly-close/scripts/verify_finance_stack.sh"
    scp notion-n8n-monthly-close/scripts/verify_finance_stack.sh \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_DIR}/notion-n8n-monthly-close/scripts/" || {
        log_error "Failed to copy verify_finance_stack.sh"
        exit 1
    }

    # Copy SQL schema
    log_info "  → Copying packages/db/sql/02_health_check_table.sql"
    scp packages/db/sql/02_health_check_table.sql \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_DIR}/packages/db/sql/" || {
        log_error "Failed to copy SQL schema"
        exit 1
    }

    log_success "All files copied successfully"
}

# Function to set permissions
set_remote_permissions() {
    log_info "Setting file permissions..."

    ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        chmod +x ${REMOTE_BASE_DIR}/scripts/check_project_tasks.py
        chmod +x ${REMOTE_BASE_DIR}/notion-n8n-monthly-close/scripts/verify_finance_stack.sh
    " || {
        log_error "Failed to set permissions"
        exit 1
    }

    log_success "Permissions set successfully"
}

# Function to validate deployment
validate_deployment() {
    log_info "Validating deployment..."

    local validation_failed=0

    # Check if files exist
    log_info "  → Checking if files exist on server"
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        test -f ${REMOTE_BASE_DIR}/scripts/check_project_tasks.py && \
        test -f ${REMOTE_BASE_DIR}/notion-n8n-monthly-close/scripts/verify_finance_stack.sh && \
        test -f ${REMOTE_BASE_DIR}/packages/db/sql/02_health_check_table.sql
    " || {
        log_error "Some files are missing on server"
        validation_failed=1
    }

    # Check if scripts are executable
    log_info "  → Checking if scripts are executable"
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        test -x ${REMOTE_BASE_DIR}/scripts/check_project_tasks.py && \
        test -x ${REMOTE_BASE_DIR}/notion-n8n-monthly-close/scripts/verify_finance_stack.sh
    " || {
        log_error "Scripts are not executable"
        validation_failed=1
    }

    if [ $validation_failed -eq 0 ]; then
        log_success "Deployment validation passed"
    else
        log_error "Deployment validation failed"
        exit 1
    fi
}

# Function to display next steps
display_next_steps() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "Deployment to ${ENV} environment completed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. Apply Supabase Schema:"
    echo "   ${BLUE}./scripts/apply-supabase-schema.sh${NC}"
    echo ""
    echo "2. Test Scripts Manually:"
    echo "   ${BLUE}ssh root@erp.insightpulseai.net${NC}"
    echo "   ${BLUE}cd ${REMOTE_BASE_DIR}${NC}"
    echo "   ${BLUE}python3 scripts/check_project_tasks.py${NC}"
    echo "   ${BLUE}cd notion-n8n-monthly-close && ./scripts/verify_finance_stack.sh --env ${ENV} --verbose${NC}"
    echo ""
    echo "3. Configure n8n Credentials:"
    echo "   - Navigate to: https://ipa.insightpulseai.net"
    echo "   - Settings → Credentials"
    echo "   - Add Odoo credentials (${ENV})"
    echo ""
    echo "4. Import n8n Workflows:"
    echo "   - Import from: notion-n8n-monthly-close/workflows/*.json"
    echo ""
    echo "5. Set up GitHub Actions secrets:"
    echo "   - SSH_PRIVATE_KEY"
    echo "   - SSH_KNOWN_HOSTS"
    echo "   - SUPABASE_SERVICE_ROLE_KEY"
    echo "   - N8N_API_KEY"
    echo "   - ODOO_PASSWORD"
    echo ""
    echo "📚 Documentation:"
    echo "   - ${BLUE}docs/DEPLOYMENT_GUIDE.md${NC} - Complete deployment guide"
    echo "   - ${BLUE}docs/HEALTH_CHECK.md${NC} - Health check system documentation"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Finance Stack Health Monitor - Server Deployment"
    echo "  Environment: ${ENV}"
    echo "  Target: ${REMOTE_USER}@${REMOTE_HOST}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_ssh_connection
    create_remote_directories
    copy_files_to_server
    set_remote_permissions
    validate_deployment
    display_next_steps
}

# Run main function
main
