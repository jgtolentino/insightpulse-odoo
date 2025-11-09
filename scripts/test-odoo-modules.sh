#!/bin/bash
# test-odoo-modules.sh
# Comprehensive Odoo module testing script for CI/CD

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"
DB_NAME="${DB_NAME:-test_db_$(date +%s)}"
ODOO_CONFIG="${ODOO_CONFIG:-/etc/odoo/odoo-test.conf}"
TEST_TAGS="${TEST_TAGS:-}"
MODULE_LIST="${1:-}"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to wait for PostgreSQL
wait_for_postgres() {
    log_info "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

    for i in {1..30}; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    log_error "PostgreSQL not available after 30 seconds"
    return 1
}

# Function to discover modules
discover_modules() {
    log_info "Discovering Odoo modules..."

    local modules=()

    # Find all modules in addons directories
    for dir in /mnt/extra-addons/insightpulse/* /mnt/extra-addons/modules/* /mnt/extra-addons/custom-addons/*; do
        if [ -f "$dir/__manifest__.py" ]; then
            module_name=$(basename "$dir")
            modules+=("$module_name")
        fi
    done

    echo "${modules[@]}"
}

# Function to install and test a module
test_module() {
    local module=$1
    local temp_db="test_${module}_$(date +%s)"

    log_info "Testing module: $module"

    # Create database
    createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db" || {
        log_error "Failed to create database for $module"
        return 1
    }

    # Initialize database with base module
    log_info "Initializing database..."
    odoo -c "$ODOO_CONFIG" -d "$temp_db" -i base --stop-after-init --log-level=error || {
        log_error "Failed to initialize database"
        dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db" 2>/dev/null || true
        return 1
    }

    # Install and test the module
    log_info "Installing and testing $module..."
    if [ -n "$TEST_TAGS" ]; then
        odoo -c "$ODOO_CONFIG" -d "$temp_db" -i "$module" --test-enable --test-tags "$TEST_TAGS" --stop-after-init --log-level=test || {
            log_error "Tests failed for $module"
            dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db" 2>/dev/null || true
            return 1
        }
    else
        odoo -c "$ODOO_CONFIG" -d "$temp_db" -i "$module" --test-enable --stop-after-init --log-level=test || {
            log_error "Tests failed for $module"
            dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db" 2>/dev/null || true
            return 1
        }
    fi

    log_success "Module $module passed all tests"

    # Cleanup
    dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db" || {
        log_warning "Failed to drop test database"
    }

    return 0
}

# Main execution
main() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       InsightPulse Odoo Module Test Suite            ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Wait for database
    wait_for_postgres || exit 1

    # Get module list
    local modules
    if [ -n "$MODULE_LIST" ]; then
        IFS=',' read -ra modules <<< "$MODULE_LIST"
    else
        modules=($(discover_modules))
    fi

    log_info "Found ${#modules[@]} modules to test"
    echo ""

    # Test each module
    local passed=0
    local failed=0
    local failed_modules=()

    for module in "${modules[@]}"; do
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        if test_module "$module"; then
            ((passed++))
        else
            ((failed++))
            failed_modules+=("$module")
        fi

        echo ""
    done

    # Summary
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   Test Summary                        ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Total modules tested: ${#modules[@]}"
    echo -e "${GREEN}Passed: $passed${NC}"

    if [ $failed -gt 0 ]; then
        echo -e "${RED}Failed: $failed${NC}"
        echo ""
        echo -e "${RED}Failed modules:${NC}"
        for module in "${failed_modules[@]}"; do
            echo -e "  ${RED}✗${NC} $module"
        done
        echo ""
        exit 1
    else
        echo ""
        log_success "All modules passed! 🎉"
        exit 0
    fi
}

# Run main
main
