#!/bin/bash
# Apache Superset Production Deployment Script
# Target: DigitalOcean App Platform
# Date: 2025-10-30

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPEC_FILE="$PROJECT_ROOT/infra/superset/superset-app.yaml"
APP_NAME="superset-analytics"

echo "========================================="
echo "Apache Superset Production Deployment"
echo "========================================="

# Function to print colored messages
print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check doctl CLI
if ! command -v doctl &> /dev/null; then
    print_error "doctl CLI not found. Install from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi
print_info "doctl CLI installed"

# Check authentication
if ! doctl auth list &> /dev/null; then
    print_error "Not authenticated to DigitalOcean. Run: doctl auth init"
    exit 1
fi
print_info "DigitalOcean authenticated"

# Check spec file exists
if [ ! -f "$SPEC_FILE" ]; then
    print_error "Spec file not found: $SPEC_FILE"
    exit 1
fi
print_info "Spec file found"

# Set default passwords
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-Postgres_26}"
export SUPERSET_ADMIN_PASSWORD="${SUPERSET_ADMIN_PASSWORD:-Postgres_26}"
export SUPERSET_SECRET_KEY="${SUPERSET_SECRET_KEY:-8UToEhL2C0ovd7S4maFPsi7e4mU05pqAH907G5yUaLsr9prnJdHu7+6k}"

# Verify required environment variables
echo ""
echo "Environment variables configured:"

REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "SUPERSET_SECRET_KEY"
    "SUPERSET_ADMIN_PASSWORD"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable not set: $var"
        print_warning "Set in ~/.zshrc or export before running this script"
        exit 1
    fi
    # Show masked value for verification
    masked_value=$(echo "${!var}" | sed 's/./*/g' | sed 's/\(.\{4\}\).*/\1***/')
    print_info "$var = $masked_value"
done

# Optional: Check if secrets exist in DO
echo ""
echo "Checking for existing Superset app..."

if doctl apps list --format Name | grep -q "^$APP_NAME$"; then
    print_warning "App '$APP_NAME' already exists"
    read -p "Do you want to update the existing app? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get existing app ID
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
        print_info "Updating app ID: $APP_ID"

        # Update app
        doctl apps update "$APP_ID" --spec "$SPEC_FILE"

        # Create new deployment
        print_info "Creating new deployment..."
        doctl apps create-deployment "$APP_ID" --force-rebuild

        print_info "Deployment initiated. Monitor progress:"
        echo "  doctl apps logs $APP_ID --follow"
    else
        print_warning "Deployment cancelled"
        exit 0
    fi
else
    print_info "Creating new app: $APP_NAME"

    # Create app
    doctl apps create --spec "$SPEC_FILE"

    # Get app ID
    sleep 5
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')

    if [ -z "$APP_ID" ]; then
        print_error "Failed to get app ID after creation"
        exit 1
    fi

    print_info "App created with ID: $APP_ID"
fi

# Secrets are pre-configured in the spec file
echo ""
print_info "Secrets Pre-configured:"
echo "  - POSTGRES_PASSWORD: Postgres_26"
echo "  - SUPERSET_SECRET_KEY: [Generated 42-character key]"
echo "  - SUPERSET_ADMIN_PASSWORD: Postgres_26"
echo ""
print_info "Secrets are already set in the App Platform spec."
print_warning "To change secrets, edit them in the DO dashboard after deployment:"
echo "  https://cloud.digitalocean.com/apps/$APP_ID → Settings → Environment Variables"
echo ""

# Monitor deployment
echo ""
echo "Monitoring deployment logs..."
print_info "Use Ctrl+C to stop watching logs (deployment will continue)"
echo ""

doctl apps logs "$APP_ID" --follow 2>&1 || true

# Get app URL
echo ""
echo "========================================="
echo "Deployment Summary"
echo "========================================="

APP_URL=$(doctl apps get "$APP_ID" --format LiveURL --no-header)

print_info "App Name: $APP_NAME"
print_info "App ID: $APP_ID"
print_info "Live URL: $APP_URL"

echo ""
print_warning "Next Steps:"
echo "  1. Verify deployment health:"
echo "     curl -f $APP_URL/health"
echo ""
echo "  2. Configure Traefik reverse proxy for /superset path:"
echo "     See: deploy/superset/traefik.yml"
echo ""
echo "  3. Access Superset at:"
echo "     http://insightpulseai.net/superset"
echo "     (after Traefik configuration)"
echo ""
echo "  4. Login with admin credentials:"
echo "     Username: admin"
echo "     Password: Postgres_26"
echo ""
echo "  5. Monitor logs:"
echo "     doctl apps logs $APP_ID --follow"
echo ""

print_info "Deployment complete!"
