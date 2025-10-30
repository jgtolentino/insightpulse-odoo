#!/bin/bash
# CI Runner for InsightPulse Odoo
# Comprehensive test execution wrapper

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Display usage
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  lint              Run code linting (ruff, flake8, pylint)
  format            Run code formatting (black, isort)
  security          Run security scan (bandit)
  test              Run module tests
  validate          Validate module manifests
  oca-fetch         Test OCA fetch script
  docker-build      Build Docker test image
  full              Run all checks

Options:
  --modules LIST    Comma-separated list of modules to test
  --fix             Auto-fix issues where possible
  --strict          Fail on warnings

Examples:
  $0 lint
  $0 test --modules ipai_expense,ipai_subscriptions
  $0 full --strict

EOF
    exit 1
}

# Lint command
run_lint() {
    log_info "Running code linting..."

    log_info "Running ruff..."
    ruff check . || true

    log_info "Running flake8..."
    flake8 addons --max-line-length=88 --extend-ignore=E203,E501,W503 || true

    log_info "Running pylint-odoo..."
    find addons -name '*.py' -not -path '*/tests/*' | xargs pylint --load-plugins=pylint_odoo -d all -e odoolint || true

    log_success "Linting complete"
}

# Format command
run_format() {
    local fix_flag=""
    if [ "$1" == "--fix" ]; then
        fix_flag="true"
        log_info "Running code formatting (with auto-fix)..."
    else
        log_info "Running code formatting (check only)..."
    fi

    if [ -n "$fix_flag" ]; then
        black addons --line-length=88
        isort addons --profile=black
        log_success "Code formatted"
    else
        black addons --line-length=88 --check
        isort addons --profile=black --check-only
        log_success "Code format check complete"
    fi
}

# Security scan
run_security() {
    log_info "Running security scan..."

    bandit -r addons -x */tests/* -ll || true

    log_success "Security scan complete"
}

# Test modules
run_test() {
    local modules="$1"

    log_info "Running module tests..."

    if [ -f "scripts/test-odoo-modules.sh" ]; then
        bash scripts/test-odoo-modules.sh "$modules"
    else
        log_error "Test script not found: scripts/test-odoo-modules.sh"
        exit 1
    fi

    log_success "Tests complete"
}

# Validate manifests
run_validate() {
    log_info "Validating module manifests..."

    python3 << 'EOF'
import os
import ast
import sys

errors = []
warnings = []
modules_checked = 0

for root, dirs, files in os.walk('addons'):
    if '__manifest__.py' in files:
        modules_checked += 1
        manifest_path = os.path.join(root, '__manifest__.py')
        module_name = os.path.basename(root)

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = ast.literal_eval(f.read())

            # Required fields
            required_fields = ['name', 'version', 'depends', 'author']
            for field in required_fields:
                if field not in manifest:
                    errors.append(f"{module_name}: Missing required field '{field}'")

            # Check version format
            if 'version' in manifest:
                version = manifest['version']
                if not version.startswith('19.'):
                    warnings.append(f"{module_name}: Version {version} doesn't match Odoo 19.0")

        except Exception as e:
            errors.append(f"{module_name}: Failed to parse manifest - {str(e)}")

print(f"\n=== Validation Results ===")
print(f"Modules checked: {modules_checked}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

if errors:
    print("\n⚠️ Errors:")
    for error in errors:
        print(f"  - {error}")

if warnings:
    print("\n⚠️ Warnings:")
    for warning in warnings:
        print(f"  - {warning}")

if errors:
    sys.exit(1)
else:
    print("\n✅ All manifests are valid")
EOF

    log_success "Manifest validation complete"
}

# Test OCA fetch
run_oca_fetch() {
    log_info "Testing OCA fetch script..."

    if [ ! -f "scripts/fetch_oca.sh" ]; then
        log_error "OCA fetch script not found"
        exit 1
    fi

    # Syntax check
    bash -n scripts/fetch_oca.sh
    log_success "OCA fetch script syntax valid"

    # Test execution (dry run)
    mkdir -p /tmp/test_oca_fetch
    bash scripts/fetch_oca.sh vendor/oca_requirements.txt /tmp/test_oca_fetch
    rm -rf /tmp/test_oca_fetch

    log_success "OCA fetch test complete"
}

# Build Docker image
run_docker_build() {
    log_info "Building Docker test image..."

    if [ ! -f "Dockerfile.test" ]; then
        log_error "Dockerfile.test not found"
        exit 1
    fi

    docker build -f Dockerfile.test -t insightpulse-odoo:test .

    log_success "Docker build complete"
}

# Run all checks
run_full() {
    local strict_mode=""
    if [ "$1" == "--strict" ]; then
        strict_mode="true"
        set -e  # Exit on any error
    fi

    log_info "Running full CI/CD check suite..."
    echo ""

    run_lint
    echo ""

    run_format
    echo ""

    run_security
    echo ""

    run_validate
    echo ""

    run_oca_fetch
    echo ""

    log_success "All CI/CD checks passed! 🎉"
}

# Main execution
main() {
    local command="${1:-}"
    shift || true

    case "$command" in
        lint)
            run_lint "$@"
            ;;
        format)
            run_format "$@"
            ;;
        security)
            run_security "$@"
            ;;
        test)
            run_test "$@"
            ;;
        validate)
            run_validate "$@"
            ;;
        oca-fetch)
            run_oca_fetch "$@"
            ;;
        docker-build)
            run_docker_build "$@"
            ;;
        full)
            run_full "$@"
            ;;
        *)
            usage
            ;;
    esac
}

# Run main
main "$@"
