#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Odoo 19 Enterprise-parity + Notion Clone - Complete Deployment Script
# Domain: insightpulseai.net
# Email: jgtolentino_rn@yahoo.com
# ============================================================================

BUNDLE_DIR="${BUNDLE_DIR:-/Users/tbwa/insightpulse-odoo/bundle}"
DOMAIN="${DOMAIN:-insightpulseai.net}"
EMAIL="${EMAIL:-jgtolentino_rn@yahoo.com}"
DB_NAME="${DB_NAME:-odoo}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-$(openssl rand -base64 32)}"

echo "═══════════════════════════════════════════════════════════════"
echo "  Odoo 19 Complete Deployment"
echo "═══════════════════════════════════════════════════════════════"
echo "Domain:        $DOMAIN"
echo "Email:         $EMAIL"
echo "Database:      $DB_NAME"
echo "Admin Pass:    $ADMIN_PASSWORD"
echo "Bundle Dir:    $BUNDLE_DIR"
echo "═══════════════════════════════════════════════════════════════"

cd "$BUNDLE_DIR"

# Step 1: Update environment configuration
echo "▶ Updating environment configuration..."
cat > .env <<EOF
DOMAIN=$DOMAIN
EMAIL=$EMAIL

POSTGRES_DB=$DB_NAME
POSTGRES_USER=odoo
POSTGRES_PASSWORD=$(openssl rand -base64 24)

# OCR provider: tesseract|google|azure
OCR_PROVIDER=tesseract
GOOGLE_CREDENTIALS_JSON=
AZURE_ENDPOINT=
AZURE_KEY=
EOF

# Step 2: Update Odoo configuration with admin password
echo "▶ Updating Odoo master password..."
sed -i.bak "s/admin_passwd = .*/admin_passwd = $ADMIN_PASSWORD/" odoo/odoo.conf

# Step 3: Restart services with new configuration
echo "▶ Restarting services with new configuration..."
docker compose down
docker compose up -d

# Step 4: Wait for services to be ready
echo "▶ Waiting for services to be ready..."
sleep 15

# Check if database exists
DB_EXISTS=$(docker compose exec -T postgres psql -U odoo -lqt | cut -d \| -f 1 | grep -w "$DB_NAME" | wc -l || echo "0")

if [ "$DB_EXISTS" -eq "0" ]; then
    echo "▶ Creating database: $DB_NAME"
    docker compose exec -T postgres psql -U odoo -c "CREATE DATABASE $DB_NAME;"
fi

# Step 5: Collect all available modules
echo "▶ Scanning for available modules..."
MODULES=""

# OCA modules from server-tools
if [ -d "addons/oca/server-tools" ]; then
    MODULES="$MODULES,auth_totp,auth_password_policy,auth_session_timeout"
    MODULES="$MODULES,base_user_role,server_environment"
fi

# OCA modules from server-auth
if [ -d "addons/oca/server-auth" ]; then
    MODULES="$MODULES,auth_totp"
fi

# OCA modules from web
if [ -d "addons/oca/web" ]; then
    MODULES="$MODULES,web_responsive,web_environment_ribbon"
fi

# OCA modules from queue
if [ -d "addons/oca/queue" ]; then
    MODULES="$MODULES,queue_job"
fi

# OCA modules from account-financial-tools
if [ -d "addons/oca/account-financial-tools" ]; then
    MODULES="$MODULES,account_move_line_purchase_info"
fi

# OCA modules from reporting-engine
if [ -d "addons/oca/reporting-engine" ]; then
    MODULES="$MODULES,report_xlsx"
fi

# Custom addons
if [ -d "addons/knowledge_notion_clone" ]; then
    MODULES="$MODULES,knowledge_notion_clone"
fi

# Remove leading comma
MODULES="${MODULES#,}"

# Step 6: Install modules
echo "▶ Installing modules: $MODULES"
docker compose exec -T odoo odoo \
    -c /etc/odoo/odoo.conf \
    -d "$DB_NAME" \
    --without-demo=all \
    -i "$MODULES" \
    --stop-after-init

# Step 7: Set system parameters
echo "▶ Configuring system parameters..."
docker compose exec -T postgres psql -U odoo -d "$DB_NAME" <<EOSQL
-- Set OCR endpoint
INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
VALUES ('expenseflow.ocr_url', 'http://ocr-api:8000/parse', NOW(), NOW(), 1, 1)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();

-- Set web.base.url
INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
VALUES ('web.base.url', 'https://$DOMAIN', NOW(), NOW(), 1, 1)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();

-- Enable developer mode by default
INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
VALUES ('web.base.url.freeze', 'True', NOW(), NOW(), 1, 1)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
EOSQL

# Step 8: Restart Odoo to apply changes
echo "▶ Restarting Odoo..."
docker compose restart odoo odoo-longpoll

# Step 9: Health checks
echo "▶ Running health checks..."
sleep 10

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Deployment Status"
echo "═══════════════════════════════════════════════════════════════"

# Check container status
docker compose ps

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Access Information"
echo "═══════════════════════════════════════════════════════════════"
echo "URL:           https://$DOMAIN"
echo "Database:      $DB_NAME"
echo "Admin Pass:    $ADMIN_PASSWORD"
echo ""
echo "First Login:"
echo "  1. Navigate to https://$DOMAIN"
echo "  2. Select database: $DB_NAME"
echo "  3. Create your first user account"
echo ""
echo "Installed Modules:"
echo "  - Authentication & Security: auth_totp, auth_password_policy"
echo "  - Web UI: web_responsive, web_environment_ribbon"
echo "  - Background Jobs: queue_job"
echo "  - Knowledge Management: knowledge_notion_clone (Notion-style)"
echo "  - Reporting: report_xlsx"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Next Steps"
echo "═══════════════════════════════════════════════════════════════"
echo "1. Configure DNS: Point $DOMAIN A record to your server IP"
echo "2. Wait 2-3 minutes for Caddy to obtain TLS certificate"
echo "3. Access your instance at https://$DOMAIN"
echo "4. Install additional modules as needed from Apps menu"
echo ""
echo "Master Password saved in: $BUNDLE_DIR/odoo/odoo.conf"
echo "Environment config saved in: $BUNDLE_DIR/.env"
echo "═══════════════════════════════════════════════════════════════"
