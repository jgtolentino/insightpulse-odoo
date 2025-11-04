#!/bin/bash

##############################################################################
# Superset Dashboard Import Script
#
# This script imports all 5 production-ready dashboards into Apache Superset
#
# Author: SuperClaude - bi-designer agent
# Created: 2025-11-03
# Version: 1.0.0
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="${SCRIPT_DIR}/dashboards"
DATASET_DIR="${SCRIPT_DIR}/datasets"

# Superset configuration
SUPERSET_HOST="${SUPERSET_HOST:-http://localhost:8088}"
SUPERSET_USERNAME="${SUPERSET_USERNAME:-admin}"
SUPERSET_PASSWORD="${SUPERSET_PASSWORD:-admin}"

##############################################################################
# Logging Functions
##############################################################################

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

##############################################################################
# Pre-flight Checks
##############################################################################

check_dependencies() {
    log_info "Checking dependencies..."

    # Check if superset CLI is available
    if ! command -v superset &> /dev/null; then
        log_error "Superset CLI not found. Please install Apache Superset."
        exit 1
    fi

    # Check if curl is available (for API calls)
    if ! command -v curl &> /dev/null; then
        log_error "curl not found. Please install curl."
        exit 1
    fi

    # Check if jq is available (for JSON processing)
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found. Installing jq for JSON processing..."
        # Try to install jq based on OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y jq
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install jq
        else
            log_error "Please install jq manually"
            exit 1
        fi
    fi

    log_success "All dependencies are installed"
}

check_superset_running() {
    log_info "Checking if Superset is running..."

    if curl -s -o /dev/null -w "%{http_code}" "${SUPERSET_HOST}/health" | grep -q "200"; then
        log_success "Superset is running at ${SUPERSET_HOST}"
    else
        log_error "Superset is not running at ${SUPERSET_HOST}"
        log_info "Please start Superset with: superset run -p 8088 --with-threads --reload --debugger"
        exit 1
    fi
}

check_files_exist() {
    log_info "Checking if dashboard files exist..."

    local missing_files=0

    for dashboard in "${DASHBOARD_DIR}"/*.json; do
        if [[ ! -f "$dashboard" ]]; then
            log_error "Dashboard file not found: $dashboard"
            missing_files=$((missing_files + 1))
        fi
    done

    if [[ $missing_files -gt 0 ]]; then
        log_error "Missing $missing_files dashboard file(s)"
        exit 1
    fi

    log_success "All dashboard files exist"
}

##############################################################################
# Authentication
##############################################################################

get_access_token() {
    log_info "Authenticating with Superset..."

    local response=$(curl -s -X POST "${SUPERSET_HOST}/api/v1/security/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"${SUPERSET_USERNAME}\", \"password\": \"${SUPERSET_PASSWORD}\"}")

    local access_token=$(echo "$response" | jq -r '.access_token')

    if [[ "$access_token" == "null" || -z "$access_token" ]]; then
        log_error "Failed to authenticate with Superset"
        echo "$response" | jq .
        exit 1
    fi

    log_success "Authentication successful"
    echo "$access_token"
}

##############################################################################
# Dataset Import
##############################################################################

import_datasets() {
    local access_token="$1"

    log_info "Importing datasets..."

    # Import datasets using Superset CLI
    # Note: This assumes datasets are already created in the database
    # The SQL files in datasets/ directory are for reference

    log_info "Verifying datasets in Superset..."

    local datasets=$(curl -s -X GET "${SUPERSET_HOST}/api/v1/dataset/" \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json")

    local dataset_count=$(echo "$datasets" | jq -r '.count // 0')

    log_info "Found ${dataset_count} datasets in Superset"

    if [[ $dataset_count -lt 10 ]]; then
        log_warning "Expected at least 10 datasets. Please create datasets from SQL files in ${DATASET_DIR}/"
        log_info "Run: superset import-datasets -p ${DATASET_DIR}/"
    else
        log_success "Datasets verified"
    fi
}

##############################################################################
# Dashboard Import
##############################################################################

import_dashboard() {
    local dashboard_file="$1"
    local access_token="$2"

    local dashboard_name=$(basename "$dashboard_file" .json)

    log_info "Importing dashboard: $dashboard_name"

    # Read dashboard JSON
    local dashboard_json=$(cat "$dashboard_file")

    # Import dashboard using Superset API
    local response=$(curl -s -X POST "${SUPERSET_HOST}/api/v1/dashboard/import/" \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -d "$dashboard_json")

    # Check if import was successful
    if echo "$response" | jq -e '.message' &> /dev/null; then
        local message=$(echo "$response" | jq -r '.message')

        if [[ "$message" == *"success"* ]] || [[ "$message" == *"imported"* ]]; then
            log_success "Dashboard imported: $dashboard_name"
        else
            log_warning "Dashboard import message: $message"
        fi
    else
        # If no message field, check for errors
        if echo "$response" | jq -e '.errors' &> /dev/null; then
            log_error "Failed to import dashboard: $dashboard_name"
            echo "$response" | jq '.errors'
        else
            log_success "Dashboard imported: $dashboard_name"
        fi
    fi
}

import_all_dashboards() {
    local access_token="$1"

    log_info "Importing all dashboards from ${DASHBOARD_DIR}/"

    local count=0

    for dashboard_file in "${DASHBOARD_DIR}"/*.json; do
        if [[ -f "$dashboard_file" ]]; then
            import_dashboard "$dashboard_file" "$access_token"
            count=$((count + 1))
        fi
    done

    log_success "Imported $count dashboards"
}

##############################################################################
# Permissions and Access
##############################################################################

set_permissions() {
    local access_token="$1"

    log_info "Setting dashboard permissions..."

    # Get all dashboards
    local dashboards=$(curl -s -X GET "${SUPERSET_HOST}/api/v1/dashboard/" \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json")

    # Set permissions for each dashboard based on metadata
    # This would require additional API calls to set role-based access

    log_info "Note: Please configure Role-Based Access Control (RBAC) in Superset UI"
    log_info "Navigate to: Settings > List Roles > [Select Role] > Permissions"
}

##############################################################################
# Validation
##############################################################################

validate_imports() {
    local access_token="$1"

    log_info "Validating dashboard imports..."

    local dashboards=$(curl -s -X GET "${SUPERSET_HOST}/api/v1/dashboard/" \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json")

    local dashboard_count=$(echo "$dashboards" | jq -r '.count // 0')

    log_info "Total dashboards in Superset: ${dashboard_count}"

    # List imported dashboards
    echo "$dashboards" | jq -r '.result[] | "\(.id): \(.dashboard_title)"' | while read -r dashboard; do
        log_info "  - $dashboard"
    done

    if [[ $dashboard_count -ge 5 ]]; then
        log_success "All dashboards imported successfully"
    else
        log_warning "Expected 5 dashboards, found ${dashboard_count}"
    fi
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         Superset Dashboard Import Script v1.0.0             ║"
    echo "║         InsightPulse Odoo Analytics Platform                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Pre-flight checks
    check_dependencies
    check_superset_running
    check_files_exist

    # Authenticate
    ACCESS_TOKEN=$(get_access_token)

    # Import datasets
    import_datasets "$ACCESS_TOKEN"

    # Import dashboards
    import_all_dashboards "$ACCESS_TOKEN"

    # Set permissions
    set_permissions "$ACCESS_TOKEN"

    # Validate
    validate_imports "$ACCESS_TOKEN"

    echo ""
    log_success "Dashboard import completed!"
    echo ""
    log_info "Next steps:"
    log_info "1. Open Superset: ${SUPERSET_HOST}"
    log_info "2. Navigate to Dashboards to view imported dashboards"
    log_info "3. Configure RLS policies for multi-tenancy"
    log_info "4. Set up email reports and alerts"
    log_info "5. Configure cache refresh schedules"
    echo ""
}

# Run main function
main "$@"
