#!/bin/bash
# InsightPulse AI - DigitalOcean Spaces Backend Setup
# This script creates a DigitalOcean Space for OpenTofu/Terraform state management
#
# Prerequisites:
# 1. DigitalOcean CLI (doctl) installed and configured
# 2. DigitalOcean API token with write access
#
# Usage:
#   ./scripts/setup-digitalocean-backend.sh
#
# Cost: $5/month (includes 250GB storage + 1TB transfer)

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SPACE_NAME="${DO_SPACE_NAME:-insightpulse-terraform-state}"
SPACE_REGION="${DO_SPACE_REGION:-sgp1}"

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

# Check if doctl is installed
check_doctl() {
    if ! command -v doctl &> /dev/null; then
        print_error "DigitalOcean CLI (doctl) is not installed"
        print_info "Install it from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        print_info ""
        print_info "Quick install:"
        print_info "  macOS:   brew install doctl"
        print_info "  Ubuntu:  snap install doctl"
        print_info "  Manual:  https://github.com/digitalocean/doctl/releases"
        exit 1
    fi
    print_success "doctl is installed"
}

# Check doctl authentication
check_doctl_auth() {
    if ! doctl auth list | grep -q "current"; then
        print_error "doctl is not authenticated"
        print_info "Run: doctl auth init"
        print_info "Then enter your DigitalOcean API token"
        exit 1
    fi
    print_success "doctl is authenticated"

    # Display current context
    ACCOUNT_EMAIL=$(doctl account get --format Email --no-header 2>/dev/null || echo "unknown")
    print_info "Using account: ${ACCOUNT_EMAIL}"
}

# Create DigitalOcean Space
create_space() {
    print_info "Creating DigitalOcean Space: ${SPACE_NAME}"

    # Check if Space already exists
    if doctl spaces list --format Name --no-header 2>/dev/null | grep -q "^${SPACE_NAME}$"; then
        print_warning "Space ${SPACE_NAME} already exists"
        return 0
    fi

    # Create Space
    doctl spaces create "${SPACE_NAME}" --region "${SPACE_REGION}"

    print_success "Space created: ${SPACE_NAME}"
}

# Enable versioning on Space (not supported by doctl, manual step)
print_versioning_instructions() {
    print_warning "Note: DigitalOcean Spaces versioning cannot be enabled via CLI"
    print_info "To enable versioning (recommended for state files):"
    print_info "  1. Go to: https://cloud.digitalocean.com/spaces/${SPACE_NAME}"
    print_info "  2. Click Settings → Enable Versioning"
    print_info ""
}

# Create Spaces access keys
create_spaces_keys() {
    print_info "Checking for Spaces access keys..."

    # List existing keys
    EXISTING_KEYS=$(doctl spaces keys list --format Name --no-header 2>/dev/null || echo "")

    if echo "$EXISTING_KEYS" | grep -q "terraform-state-key"; then
        print_warning "Spaces key 'terraform-state-key' already exists"
        print_info "Use existing key or create a new one in DigitalOcean console"
        return 0
    fi

    print_info "To create Spaces access keys:"
    print_info "  1. Go to: https://cloud.digitalocean.com/account/api/spaces"
    print_info "  2. Click 'Generate New Key'"
    print_info "  3. Name it: terraform-state-key"
    print_info "  4. Save the Access Key and Secret Key"
    print_info ""
    print_info "Then set environment variables:"
    print_info "  export AWS_ACCESS_KEY_ID='your-spaces-access-key'"
    print_info "  export AWS_SECRET_ACCESS_KEY='your-spaces-secret-key'"
    print_info ""
}

# Test Space access
test_space_access() {
    print_info "Testing Space access..."

    # This requires s3cmd or aws cli to be configured
    if command -v aws &> /dev/null && [ -n "${AWS_ACCESS_KEY_ID:-}" ] && [ -n "${AWS_SECRET_ACCESS_KEY:-}" ]; then
        if aws s3 ls "s3://${SPACE_NAME}" --endpoint="https://${SPACE_REGION}.digitaloceanspaces.com" &> /dev/null; then
            print_success "Space is accessible"
            return 0
        else
            print_warning "Cannot verify Space access (credentials may not be set)"
        fi
    else
        print_info "Skipping Space access test (AWS CLI not configured with Spaces credentials)"
    fi
}

# Display summary
display_summary() {
    echo ""
    echo "======================================"
    echo "DigitalOcean Spaces Setup Complete!"
    echo "======================================"
    echo ""
    echo "Space Name:       ${SPACE_NAME}"
    echo "Region:           ${SPACE_REGION}"
    echo "Endpoint:         https://${SPACE_REGION}.digitaloceanspaces.com"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Create Spaces access keys:"
    echo "   https://cloud.digitalocean.com/account/api/spaces"
    echo ""
    echo "2. Set environment variables:"
    echo "   export AWS_ACCESS_KEY_ID='your-spaces-access-key'"
    echo "   export AWS_SECRET_ACCESS_KEY='your-spaces-secret-key'"
    echo ""
    echo "3. Optional: Enable versioning (recommended):"
    echo "   https://cloud.digitalocean.com/spaces/${SPACE_NAME}"
    echo ""
    echo "4. Update terraform/backend.tf if needed:"
    echo "   - bucket = \"${SPACE_NAME}\""
    echo "   - endpoint = \"${SPACE_REGION}.digitaloceanspaces.com\""
    echo ""
    echo "5. Initialize Terraform:"
    echo "   cd terraform && tofu init"
    echo ""
    echo "Cost: \$5/month (includes 250GB storage + 1TB transfer)"
    echo ""
    echo "Important: DigitalOcean Spaces does NOT support state locking."
    echo "Only one person should run 'tofu apply' at a time."
    echo ""
}

# Main function
main() {
    echo ""
    echo "======================================"
    echo "InsightPulse AI - DO Spaces Setup"
    echo "======================================"
    echo ""

    print_info "Space Name:       ${SPACE_NAME}"
    print_info "Region:           ${SPACE_REGION}"
    echo ""

    # Check prerequisites
    check_doctl
    check_doctl_auth

    # Create resources
    create_space
    print_versioning_instructions
    create_spaces_keys
    test_space_access

    # Display summary
    display_summary
}

# Run main function
main
