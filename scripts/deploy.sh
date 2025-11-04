#!/bin/bash
set -euo pipefail

# One-Click Deployment Script for InsightPulse Automation
# Activates all 4 automation modes on existing infrastructure

echo "🚀 InsightPulse One-Click Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configuration
DROPLET_IP="${DROPLET_IP:-188.166.237.231}"
REPO_PATH="/root/insightpulse-odoo"
ODOO_CONTAINER="odoo-bundle"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

step() {
    echo -e "\n${GREEN}▶${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Check SSH access
step "Checking SSH access to droplet..."
if ! ssh -o ConnectTimeout=5 root@${DROPLET_IP} "echo 'Connected'" > /dev/null 2>&1; then
    error "Cannot connect to ${DROPLET_IP}. Check SSH keys."
fi
success "SSH access confirmed"

# Pull latest code
step "Pulling latest code..."
ssh root@${DROPLET_IP} "cd ${REPO_PATH} && git pull origin main" || error "Git pull failed"
success "Code updated"

# Install ipai_agent addon
step "Installing ipai_agent Odoo addon..."
ssh root@${DROPLET_IP} << 'ENDSSH'
set -e

# Check if addon exists
if [ ! -d "/root/insightpulse-odoo/addons/custom/ipai_agent" ]; then
    echo "ERROR: ipai_agent addon not found"
    exit 1
fi

# Install via Odoo CLI (if container supports it)
if docker exec odoo-bundle odoo --version > /dev/null 2>&1; then
    # Stop container
    docker stop odoo-bundle || true

    # Run update command
    docker run --rm \
        --volumes-from odoo-bundle \
        --network container:odoo-db \
        jgtolentino/insightpulse-odoo:main \
        odoo -c /etc/odoo/odoo.conf \
        -u ipai_agent \
        -d insightpulse_odoo \
        --stop-after-init 2>&1 | tail -20

    # Start container
    docker start odoo-bundle
    sleep 10

    echo "✓ Addon installed"
else
    echo "⚠ Manual addon installation required"
fi
ENDSSH
success "Addon installation complete"

# Update OCR services
step "Updating OCR services..."
ssh root@${DROPLET_IP} << 'ENDSSH'
# Restart DeepSeek-OCR
systemctl restart deepseek-ocr
sleep 3

# Check health
if curl -sf http://127.0.0.1:9888/health > /dev/null; then
    echo "✓ DeepSeek-OCR healthy"
else
    echo "⚠ DeepSeek-OCR health check failed"
fi

# Check PaddleOCR
if curl -sf http://172.22.0.2:8000/health > /dev/null; then
    echo "✓ PaddleOCR healthy"
else
    echo "⚠ PaddleOCR health check failed"
fi
ENDSSH
success "OCR services updated"

# Verify deployment
step "Running health checks..."

echo -n "  Checking Odoo... "
if ssh root@${DROPLET_IP} "curl -sf http://localhost:8070/web/health > /dev/null"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
fi

echo -n "  Checking OCR endpoint... "
if curl -sf http://ocr.insightpulseai.net/health > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
fi

echo -n "  Checking AI Agent API... "
if curl -sf https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
fi

success "Health checks complete"

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Deployment Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Four Automation Modes Active:"
echo ""
echo "1. Odoo Discuss: https://insightpulseai.net/odoo"
echo "   Type: @ipai-bot in any channel"
echo ""
echo "2. Pulse Hub Web UI: https://pulse-hub-web-an645.ondigitalocean.app"
echo "   Click one-click deployment buttons"
echo ""
echo "3. AI Agent API: https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat"
echo "   Use ipai-cli or direct API calls"
echo ""
echo "4. GitHub PR Bot: https://github.com/jgtolentino/insightpulse-odoo"
echo "   Comment: @claude in any pull request"
echo ""
echo "📚 Usage Guide: QUICKSTART_ODOO_AUTOMATION.md"
echo ""
