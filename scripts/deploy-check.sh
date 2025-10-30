#!/usr/bin/env bash
#
# deploy-check.sh - Pre-production deployment validation for Odoo 19
# Validates Docker containers, Odoo config, DB connectivity, proxy headers, and assets
#
# Usage: ./scripts/deploy-check.sh [--quick | --full]
#   --quick: Skip asset rebuild and module updates (faster)
#   --full:  Complete validation including asset rebuild (default)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"
ODOO_DB="${ODOO_DB:-odoo_prod}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
MODE="${1:---full}"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
    ((PASSED_CHECKS++))
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    ((FAILED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    ((WARNINGS++))
}

check_header() {
    ((TOTAL_CHECKS++))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}[$TOTAL_CHECKS] $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Validation checks

check_docker_running() {
    check_header "Docker Daemon Status"
    if docker info &>/dev/null; then
        log_success "Docker daemon is running"
    else
        log_error "Docker daemon is not running or not accessible"
        exit 1
    fi
}

check_containers_healthy() {
    check_header "Container Health Status"

    local containers=("odoo" "db")
    local all_healthy=true

    for container in "${containers[@]}"; do
        local full_name=$(docker compose ps --format json 2>/dev/null | jq -r ".[] | select(.Service==\"$container\") | .Name" | head -1)

        if [[ -z "$full_name" ]]; then
            log_error "Container '$container' not found in docker compose"
            all_healthy=false
            continue
        fi

        local status=$(docker inspect --format='{{.State.Status}}' "$full_name" 2>/dev/null || echo "not_found")
        local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no_healthcheck{{end}}' "$full_name" 2>/dev/null || echo "unknown")

        if [[ "$status" == "running" ]]; then
            if [[ "$health" == "healthy" ]]; then
                log_success "Container '$container' ($full_name): running + healthy"
            elif [[ "$health" == "no_healthcheck" ]]; then
                log_warning "Container '$container' ($full_name): running (no healthcheck configured)"
            else
                log_error "Container '$container' ($full_name): running but health=$health"
                all_healthy=false
            fi
        else
            log_error "Container '$container' ($full_name): status=$status"
            all_healthy=false
        fi
    done

    if ! $all_healthy; then
        log_error "Some containers are not healthy. Fix before deployment."
        exit 1
    fi
}

check_odoo_version() {
    check_header "Odoo Version Verification"

    local version_output
    if version_output=$(docker compose exec -T odoo python odoo-bin --version 2>&1); then
        log_success "Odoo version: $(echo "$version_output" | head -1)"

        # Check if Odoo 19.x
        if echo "$version_output" | grep -q "Odoo Server 19"; then
            log_success "Odoo 19.x detected (compatible)"
        else
            log_warning "Expected Odoo 19.x, got: $version_output"
        fi
    else
        log_error "Failed to get Odoo version: $version_output"
    fi
}

check_db_connectivity() {
    check_header "Database Connectivity"

    # Test DB connection via psql
    if docker compose exec -T db pg_isready -U "${PGUSER:-odoo}" -d "${PGDATABASE:-odoo}" -q &>/dev/null; then
        log_success "PostgreSQL is ready and accepting connections"
    else
        log_error "PostgreSQL is not ready or not accepting connections"
        return 1
    fi

    # Test Odoo can connect to DB
    log_info "Testing Odoo → PostgreSQL connectivity..."
    if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$ODOO_DB" --stop-after-init --log-level=error 2>&1 | grep -qE "(error|ERROR|CRITICAL)"; then
        log_error "Odoo failed to connect to database (check logs above)"
    else
        log_success "Odoo successfully connected to database"
    fi
}

check_odoo_config() {
    check_header "Odoo Configuration Validation"

    # Check if config file exists
    if docker compose exec -T odoo test -f "$ODOO_CONF" &>/dev/null; then
        log_success "Config file exists: $ODOO_CONF"
    else
        log_error "Config file not found: $ODOO_CONF"
        return 1
    fi

    # Validate critical config parameters
    local config_content
    config_content=$(docker compose exec -T odoo cat "$ODOO_CONF" 2>/dev/null)

    # Check proxy_mode (required for production behind reverse proxy)
    if echo "$config_content" | grep -qE "^proxy_mode\s*=\s*True"; then
        log_success "proxy_mode = True (correct for reverse proxy)"
    else
        log_warning "proxy_mode not set to True (may cause redirect issues behind proxy)"
    fi

    # Check workers (should be >0 for production)
    if echo "$config_content" | grep -qE "^workers\s*=\s*[1-9]"; then
        local workers=$(echo "$config_content" | grep -E "^workers" | awk -F= '{print $2}' | tr -d ' ')
        log_success "workers = $workers (multi-process mode)"
    else
        log_warning "workers not set or = 0 (single-process mode, not recommended for production)"
    fi

    # Check memory limits
    if echo "$config_content" | grep -qE "^limit_memory_hard"; then
        log_success "Memory limits configured"
    else
        log_warning "Memory limits not configured (may cause OOM issues)"
    fi

    # Check log configuration
    if echo "$config_content" | grep -qE "^logfile"; then
        log_success "Logging configured to file"
    else
        log_warning "Logging not configured to file (logs only to stdout)"
    fi
}

check_addons_path() {
    check_header "Addons Path Validation"

    # Get addons_path from config
    local addons_path
    addons_path=$(docker compose exec -T odoo grep -E "^addons_path" "$ODOO_CONF" 2>/dev/null | awk -F= '{print $2}' | tr -d ' ')

    if [[ -z "$addons_path" ]]; then
        log_error "addons_path not found in config"
        return 1
    fi

    log_info "Configured addons_path: $addons_path"

    # Validate each path exists
    IFS=',' read -ra PATHS <<< "$addons_path"
    local all_exist=true
    for path in "${PATHS[@]}"; do
        if docker compose exec -T odoo test -d "$path" &>/dev/null; then
            log_success "Addons path exists: $path"
        else
            log_error "Addons path missing: $path"
            all_exist=false
        fi
    done

    if ! $all_exist; then
        log_error "Some addons paths are missing. Check volume mounts."
    fi
}

check_python_dependencies() {
    check_header "Python Dependencies"

    # Check critical dependencies
    local deps=("psycopg2" "requests" "werkzeug" "lxml")
    local all_present=true

    for dep in "${deps[@]}"; do
        if docker compose exec -T odoo python -c "import $dep" 2>/dev/null; then
            local version=$(docker compose exec -T odoo python -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "unknown")
            log_success "$dep installed (version: $version)"
        else
            log_error "$dep not installed or import failed"
            all_present=false
        fi
    done

    if ! $all_present; then
        log_error "Some Python dependencies are missing"
    fi
}

check_env_secrets() {
    check_header "Environment Variables & Secrets"

    # Check if .env file exists
    if [[ -f .env ]]; then
        log_success ".env file exists"

        # Check for required variables
        local required_vars=("POSTGRES_PASSWORD" "PGUSER" "PGDATABASE")
        for var in "${required_vars[@]}"; do
            if grep -qE "^${var}=" .env; then
                log_success "$var is set in .env"
            else
                log_warning "$var not found in .env"
            fi
        done
    else
        log_warning ".env file not found (using defaults or compose env)"
    fi

    # Check for hardcoded secrets in config (security issue)
    local config_content
    config_content=$(docker compose exec -T odoo cat "$ODOO_CONF" 2>/dev/null)

    if echo "$config_content" | grep -qE "^admin_passwd\s*=\s*admin"; then
        log_error "Default admin password detected in config (SECURITY RISK!)"
    fi
}

check_asset_build() {
    if [[ "$MODE" == "--quick" ]]; then
        log_info "Skipping asset build (--quick mode)"
        return 0
    fi

    check_header "Asset Build (Clean, Non-Dev)"

    log_info "Building Odoo assets (this may take 30-60 seconds)..."
    if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$ODOO_DB" --dev=none --stop-after-init 2>&1 | tee /tmp/odoo-asset-build.log | grep -qE "(error|ERROR|CRITICAL)"; then
        log_error "Asset build failed (check /tmp/odoo-asset-build.log)"
        cat /tmp/odoo-asset-build.log
    else
        log_success "Assets built successfully (production mode)"
    fi
}

check_module_update() {
    if [[ "$MODE" == "--quick" ]]; then
        log_info "Skipping module update (--quick mode)"
        return 0
    fi

    check_header "Module Update Test (base)"

    log_info "Updating 'base' module to validate Odoo functionality..."
    if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$ODOO_DB" -u base --stop-after-init --log-level=error 2>&1 | tee /tmp/odoo-module-update.log | grep -qE "(error|ERROR|CRITICAL)"; then
        log_error "Module update failed (check /tmp/odoo-module-update.log)"
        cat /tmp/odoo-module-update.log
    else
        log_success "Module 'base' updated successfully"
    fi
}

check_proxy_headers() {
    check_header "Reverse Proxy Header Configuration"

    log_info "Checking if Odoo is accessible via HTTP..."

    # Try to access Odoo health endpoint
    local odoo_url="http://localhost:8069/web/health"
    if curl -fsS --connect-timeout 5 --max-time 10 "$odoo_url" &>/dev/null; then
        log_success "Odoo is accessible at $odoo_url"

        # Check if response includes headers (curl -I)
        local headers
        headers=$(curl -sI "$odoo_url" 2>/dev/null)

        if echo "$headers" | grep -qi "X-Frame-Options"; then
            log_success "Security headers detected in response"
        else
            log_warning "Security headers (X-Frame-Options) not detected"
        fi
    else
        log_warning "Could not access Odoo at $odoo_url (may be normal if not exposed)"
    fi

    log_info "Reminder: Ensure reverse proxy forwards X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Host"
}

check_backup_system() {
    check_header "Backup System Readiness"

    # Check if backup directory exists
    if [[ -d "$BACKUP_DIR" ]]; then
        log_success "Backup directory exists: $BACKUP_DIR"

        # Check write permissions
        if [[ -w "$BACKUP_DIR" ]]; then
            log_success "Backup directory is writable"
        else
            log_error "Backup directory is not writable"
        fi

        # Check recent backups
        local backup_count=$(find "$BACKUP_DIR" -name "*.dump" -o -name "*.tar.gz" | wc -l)
        if [[ $backup_count -gt 0 ]]; then
            log_success "Found $backup_count existing backup(s)"
        else
            log_warning "No backups found in $BACKUP_DIR"
        fi
    else
        log_warning "Backup directory does not exist: $BACKUP_DIR"
        log_info "Creating backup directory..."
        mkdir -p "$BACKUP_DIR"
        log_success "Backup directory created: $BACKUP_DIR"
    fi
}

check_log_rotation() {
    check_header "Docker Log Rotation"

    # Check Docker daemon log configuration
    if [[ -f /etc/docker/daemon.json ]]; then
        if grep -q "log-opts" /etc/docker/daemon.json 2>/dev/null; then
            log_success "Docker log rotation configured in /etc/docker/daemon.json"
        else
            log_warning "Docker log rotation not configured (logs may grow indefinitely)"
        fi
    else
        log_warning "/etc/docker/daemon.json not found (using Docker defaults)"
    fi

    # Check current log sizes
    log_info "Checking container log sizes..."
    local total_size=0
    for container in $(docker compose ps -q 2>/dev/null); do
        if [[ -n "$container" ]]; then
            local log_file=$(docker inspect --format='{{.LogPath}}' "$container" 2>/dev/null)
            if [[ -f "$log_file" ]]; then
                local size=$(du -h "$log_file" | awk '{print $1}')
                log_info "  $(docker inspect --format='{{.Name}}' "$container"): $size"
                total_size=$((total_size + $(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null)))
            fi
        fi
    done

    local total_mb=$((total_size / 1024 / 1024))
    if [[ $total_mb -lt 500 ]]; then
        log_success "Total container logs: ${total_mb}MB (healthy)"
    else
        log_warning "Total container logs: ${total_mb}MB (consider rotation)"
    fi
}

# Generate summary report
generate_report() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}DEPLOYMENT VALIDATION SUMMARY${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "Total Checks: ${TOTAL_CHECKS}"
    echo -e "${GREEN}Passed:${NC} ${PASSED_CHECKS}"
    echo -e "${RED}Failed:${NC} ${FAILED_CHECKS}"
    echo -e "${YELLOW}Warnings:${NC} ${WARNINGS}"
    echo ""

    if [[ $FAILED_CHECKS -eq 0 ]]; then
        echo -e "${GREEN}✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT${NC}"
        echo ""
        echo -e "${BLUE}Next Steps:${NC}"
        echo "  1. Review warnings (if any)"
        echo "  2. Create pre-deployment backup:"
        echo "     docker compose exec db pg_dump -U \$PGUSER -d \$PGDATABASE -Fc > $BACKUP_DIR/preupgrade_\$(date +%F_%H%M%S).dump"
        echo "  3. Deploy with: docker compose up -d"
        echo "  4. Monitor logs: docker compose logs -f"
        echo ""
        return 0
    else
        echo -e "${RED}❌ DEPLOYMENT VALIDATION FAILED${NC}"
        echo ""
        echo -e "${RED}Fix the failed checks above before deploying to production.${NC}"
        echo ""
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Odoo 19 Deployment Validation (InsightPulse)                  ║${NC}"
    echo -e "${BLUE}║  Mode: ${MODE}                                             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Run all checks
    check_docker_running
    check_containers_healthy
    check_odoo_version
    check_db_connectivity
    check_odoo_config
    check_addons_path
    check_python_dependencies
    check_env_secrets
    check_asset_build
    check_module_update
    check_proxy_headers
    check_backup_system
    check_log_rotation

    # Generate final report
    generate_report
}

# Run main function
main "$@"
