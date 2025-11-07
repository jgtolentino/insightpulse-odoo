#!/bin/bash
# InsightPulse AI - Automated Wave Installation
# Installs all module waves sequentially
#
# Usage:
#   ./scripts/install-all-waves.sh [database_name]
#
# Default database: production

set -euo pipefail

# Configuration
DB_NAME="${1:-production}"
WAVES_DIR="./install-waves"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if database exists
check_database() {
    print_info "Checking database: ${DB_NAME}"

    if docker exec odoo psql -U odoo -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
        print_success "Database exists: ${DB_NAME}"
    else
        print_error "Database does not exist: ${DB_NAME}"
        print_info "Create it first with:"
        print_info "  docker exec -it odoo odoo-bin -d ${DB_NAME} --stop-after-init"
        exit 1
    fi
}

# Install a single wave
install_wave() {
    local wave_file="$1"
    local wave_name=$(basename "$wave_file" .txt)

    print_info "========================================="
    print_info "Installing Wave: ${wave_name}"
    print_info "========================================="

    # Extract modules (excluding comments and empty lines)
    MODULES=$(cat "$wave_file" | grep -v '^#' | grep -v '^$' | tr '\n' ',' | sed 's/,$//')

    if [ -z "$MODULES" ]; then
        print_warning "No modules found in ${wave_file}, skipping"
        return 0
    fi

    print_info "Modules to install: ${MODULES}"

    # Install modules
    if docker exec odoo odoo-bin -d "${DB_NAME}" -i "${MODULES}" --stop-after-init; then
        print_success "Wave installed: ${wave_name}"
        return 0
    else
        print_error "Failed to install wave: ${wave_name}"
        return 1
    fi
}

# Main installation process
main() {
    echo ""
    echo "======================================"
    echo "InsightPulse AI - Wave Installation"
    echo "======================================"
    echo ""
    print_info "Database: ${DB_NAME}"
    print_info "Waves directory: ${WAVES_DIR}"
    echo ""

    # Check prerequisites
    check_database

    # Install waves in order
    WAVES=(
        "${WAVES_DIR}/00_base.txt"
        "${WAVES_DIR}/10_web_ux.txt"
        "${WAVES_DIR}/20_sales_inventory.txt"
        "${WAVES_DIR}/25_localization.txt"
        "${WAVES_DIR}/30_accounting.txt"
        "${WAVES_DIR}/40_hr_project.txt"
        "${WAVES_DIR}/90_optional.txt"
    )

    TOTAL=${#WAVES[@]}
    CURRENT=0
    FAILED=0

    for wave in "${WAVES[@]}"; do
        CURRENT=$((CURRENT + 1))

        print_info "[${CURRENT}/${TOTAL}] Processing: $(basename "$wave")"

        if [ ! -f "$wave" ]; then
            print_warning "Wave file not found: $wave, skipping"
            continue
        fi

        if ! install_wave "$wave"; then
            FAILED=$((FAILED + 1))
            print_error "Installation failed for: $(basename "$wave")"

            # Ask user if they want to continue
            read -p "Continue with remaining waves? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_error "Installation aborted by user"
                exit 1
            fi
        fi

        echo ""
    done

    # Summary
    echo ""
    echo "======================================"
    echo "Installation Summary"
    echo "======================================"
    echo ""
    echo "Total waves: ${TOTAL}"
    echo "Successful:  $((TOTAL - FAILED))"
    echo "Failed:      ${FAILED}"
    echo ""

    if [ ${FAILED} -eq 0 ]; then
        print_success "All waves installed successfully!"
    else
        print_warning "Some waves failed to install"
        print_info "Check the logs above for details"
    fi

    echo ""
    print_info "Next steps:"
    print_info "  1. Restart Odoo: docker-compose restart odoo"
    print_info "  2. Access Odoo: http://localhost:8069"
    print_info "  3. Configure your company and chart of accounts"
    echo ""
}

# Run main function
main
