#!/usr/bin/env bash
#
# Deploy Apache Superset and make it live at https://insightpulseai.net/superset
#
# This script:
# 1. Deploys Superset to DigitalOcean App Platform
# 2. Generates updated Caddyfile with Superset routing
# 3. Provides instructions for updating Caddy on the server
#
# Usage: ./scripts/deploy-superset-live.sh
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }
log_step() { echo -e "${CYAN}▶${NC} $1"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Deploy Superset to insightpulseai.net"
echo "=========================================="
echo ""

# ==========================================
# Step 1: Check Prerequisites
# ==========================================
log_step "Step 1: Checking prerequisites..."
echo ""

# Check doctl
if ! command -v doctl &> /dev/null; then
    log_error "doctl CLI not found"
    echo ""
    echo "Install doctl:"
    echo "  macOS: brew install doctl"
    echo "  Linux: See https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi
log_success "doctl CLI installed"

# Check authentication
if ! doctl auth list &> /dev/null; then
    log_error "Not authenticated to DigitalOcean"
    echo ""
    echo "Run: doctl auth init"
    exit 1
fi
log_success "DigitalOcean authenticated"

# Check spec file
SPEC_FILE="$PROJECT_ROOT/infra/superset/superset-app.yaml"
if [ ! -f "$SPEC_FILE" ]; then
    log_error "Spec file not found: $SPEC_FILE"
    exit 1
fi
log_success "Spec file found"

echo ""

# ==========================================
# Step 2: Deploy to DigitalOcean
# ==========================================
log_step "Step 2: Deploying Superset to DigitalOcean App Platform..."
echo ""

# Check if app exists
APP_NAME="superset-analytics"
if doctl apps list --format Name --no-header | grep -q "^$APP_NAME$"; then
    log_warning "App '$APP_NAME' already exists"
    echo ""
    read -p "Do you want to update the existing app? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Deployment cancelled"
        echo ""
        log_info "To manually update, run:"
        echo "  ./deploy/superset/deploy.sh"
        exit 0
    fi

    # Update existing app
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
    log_info "Updating app ID: $APP_ID"

    doctl apps update "$APP_ID" --spec "$SPEC_FILE"
    doctl apps create-deployment "$APP_ID" --force-rebuild

    log_success "Deployment initiated"
else
    # Create new app
    log_info "Creating new app: $APP_NAME"

    doctl apps create --spec "$SPEC_FILE"

    # Wait for app to be created
    sleep 5

    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
    if [ -z "$APP_ID" ]; then
        log_error "Failed to get app ID after creation"
        exit 1
    fi

    log_success "App created with ID: $APP_ID"
fi

echo ""
log_info "Waiting for deployment to complete..."
log_info "This may take 5-15 minutes..."
echo ""

# Wait for deployment to be running
RETRIES=0
MAX_RETRIES=60  # 30 minutes max
while [ $RETRIES -lt $MAX_RETRIES ]; do
    STATUS=$(doctl apps get "$APP_ID" --format Status --no-header)

    if [ "$STATUS" == "RUNNING" ]; then
        log_success "Deployment successful!"
        break
    elif [ "$STATUS" == "ERROR" ]; then
        log_error "Deployment failed"
        echo ""
        log_info "Check logs with:"
        echo "  doctl apps logs $APP_ID"
        exit 1
    fi

    echo -ne "Status: $STATUS (${RETRIES}s elapsed)\r"
    sleep 30
    ((RETRIES++))
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    log_error "Deployment timeout after 30 minutes"
    exit 1
fi

echo ""

# ==========================================
# Step 3: Get App URL
# ==========================================
log_step "Step 3: Getting deployment URL..."
echo ""

APP_URL=$(doctl apps get "$APP_ID" --format LiveURL --no-header)
if [ -z "$APP_URL" ]; then
    log_error "Failed to get app URL"
    exit 1
fi

log_success "Superset deployed at: $APP_URL"
echo ""

# Test health endpoint
log_info "Testing health endpoint..."
if curl -sf "$APP_URL/health" > /dev/null; then
    log_success "Health check passed"
else
    log_warning "Health check failed - app may still be initializing"
    log_info "Wait a few minutes and test manually:"
    echo "  curl -f $APP_URL/health"
fi

echo ""

# ==========================================
# Step 4: Generate Caddy Configuration
# ==========================================
log_step "Step 4: Generating Caddy configuration..."
echo ""

# Extract hostname from URL
APP_HOSTNAME=$(echo "$APP_URL" | sed 's|https://||' | sed 's|http://||')

# Generate Caddyfile
CADDY_OUTPUT="/tmp/Caddyfile.superset.$(date +%s)"

cat > "$CADDY_OUTPUT" << EOF
# Caddyfile for insightpulseai.net
# Auto-generated: $(date)

insightpulseai.net {
  encode zstd gzip

  # Superset BI Dashboard
  @superset path /superset* /static/appbuilder* /static/assets*
  handle @superset {
    reverse_proxy https://${APP_HOSTNAME} {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-Host {host}
      header_up X-Forwarded-Proto {scheme}
      header_up X-Real-IP {remote_host}
    }
  }

  # Odoo paths
  @odoo path /odoo* /web* /longpolling* /calendar* /website* /shop*
  handle @odoo {
    reverse_proxy 127.0.0.1:8069
  }

  # Block database manager
  @dbm path /web/database/* /database/*
  respond @dbm 403

  # Default
  handle {
    respond "OK" 200
  }

  # Security headers
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "SAMEORIGIN"
    Referrer-Policy "strict-origin-when-cross-origin"
  }
}
EOF

log_success "Caddyfile generated: $CADDY_OUTPUT"

# Save to repo
cp "$CADDY_OUTPUT" "$PROJECT_ROOT/caddy/Caddyfile.production"
log_success "Caddyfile saved to: caddy/Caddyfile.production"

echo ""

# ==========================================
# Step 5: Instructions for Caddy Update
# ==========================================
log_step "Step 5: Update Caddy on insightpulseai.net server"
echo ""

log_warning "MANUAL STEPS REQUIRED:"
echo ""
echo "1. SSH to server:"
echo "   ${GREEN}ssh user@insightpulseai.net${NC}"
echo ""
echo "2. Backup current Caddyfile:"
echo "   ${GREEN}sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup.\$(date +%Y%m%d)${NC}"
echo ""
echo "3. Copy new Caddyfile from this machine:"
echo "   ${GREEN}scp $CADDY_OUTPUT user@insightpulseai.net:/tmp/Caddyfile.new${NC}"
echo ""
echo "4. On server, move to Caddy directory:"
echo "   ${GREEN}sudo mv /tmp/Caddyfile.new /etc/caddy/Caddyfile${NC}"
echo ""
echo "5. Validate Caddy configuration:"
echo "   ${GREEN}sudo caddy validate --config /etc/caddy/Caddyfile${NC}"
echo ""
echo "6. Reload Caddy:"
echo "   ${GREEN}sudo systemctl reload caddy${NC}"
echo ""
echo "7. Check status:"
echo "   ${GREEN}sudo systemctl status caddy${NC}"
echo ""

# ==========================================
# Step 6: Final Verification
# ==========================================
log_step "Step 6: Verify deployment"
echo ""

echo "After updating Caddy, test these endpoints:"
echo ""
echo "Health check:"
echo "  ${GREEN}curl -f https://insightpulseai.net/superset/health${NC}"
echo ""
echo "Login page:"
echo "  ${GREEN}curl -I https://insightpulseai.net/superset/login/${NC}"
echo ""
echo "Open in browser:"
echo "  ${GREEN}https://insightpulseai.net/superset${NC}"
echo ""

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
log_success "Deployment Complete!"
echo "=========================================="
echo ""

echo "📊 Superset Details:"
echo "  App ID: $APP_ID"
echo "  Direct URL: $APP_URL"
echo "  Public URL: https://insightpulseai.net/superset (after Caddy update)"
echo ""

echo "🔑 Login Credentials:"
echo "  Username: admin"
echo "  Password: Postgres_26"
echo "  ⚠️  Change password after first login!"
echo ""

echo "📖 Documentation:"
echo "  Full guide: docs/superset/GOING_LIVE_CHECKLIST.md"
echo "  Deployment guide: docs/superset/DEPLOYMENT_GUIDE.md"
echo "  Caddyfile: caddy/Caddyfile.production"
echo ""

echo "🔧 Useful Commands:"
echo "  View logs: doctl apps logs $APP_ID --follow"
echo "  Check status: doctl apps get $APP_ID"
echo "  Redeploy: doctl apps create-deployment $APP_ID --force-rebuild"
echo ""

log_success "Next: Update Caddy on insightpulseai.net (see instructions above)"
