#!/bin/bash
# ERP Droplet Diagnostic Script
# Checks Odoo service, firewall, and connectivity

set -euo pipefail

DROPLET_IP="165.227.10.178"
DROPLET_NAME="ipai-odoo-erp"
DOMAIN="erp.insightpulseai.net"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "ERP Droplet Diagnostics"
echo "========================================="
echo ""
echo "Droplet: $DROPLET_NAME"
echo "IP: $DROPLET_IP"
echo "Domain: $DOMAIN"
echo ""

# Test 1: DNS Resolution
echo "1. Testing DNS resolution..."
DNS_IP=$(getent hosts $DOMAIN | awk '{ print $1 }' | head -1 || echo "")
if [ -z "$DNS_IP" ]; then
    DNS_IP=$(nslookup $DOMAIN 2>/dev/null | grep -A 1 "Name:" | grep "Address:" | awk '{print $2}' || echo "unknown")
fi
if [ "$DNS_IP" == "$DROPLET_IP" ]; then
    echo -e "${GREEN}✅ DNS resolves correctly: $DNS_IP${NC}"
else
    echo -e "${YELLOW}⚠️ DNS: Got $DNS_IP, Expected: $DROPLET_IP${NC}"
fi
echo ""

# Test 2: Ping Droplet
echo "2. Testing network connectivity (ping)..."
if ping -c 3 $DROPLET_IP &> /dev/null; then
    echo -e "${GREEN}✅ Droplet is reachable${NC}"
else
    echo -e "${RED}❌ Droplet is NOT reachable${NC}"
fi
echo ""

# Test 3: Port 22 (SSH)
echo "3. Testing SSH port (22)..."
if timeout 5 bash -c "nc -zv $DROPLET_IP 22" &> /dev/null; then
    echo -e "${GREEN}✅ SSH port is open${NC}"
else
    echo -e "${RED}❌ SSH port is CLOSED or filtered${NC}"
fi
echo ""

# Test 4: Port 80 (HTTP)
echo "4. Testing HTTP port (80)..."
if timeout 5 bash -c "nc -zv $DROPLET_IP 80" &> /dev/null; then
    echo -e "${GREEN}✅ HTTP port is open${NC}"
else
    echo -e "${RED}❌ HTTP port is CLOSED or filtered${NC}"
fi
echo ""

# Test 5: Port 443 (HTTPS)
echo "5. Testing HTTPS port (443)..."
if timeout 5 bash -c "nc -zv $DROPLET_IP 443" &> /dev/null; then
    echo -e "${GREEN}✅ HTTPS port is open${NC}"
else
    echo -e "${RED}❌ HTTPS port is CLOSED or filtered${NC}"
fi
echo ""

# Test 6: HTTP Request
echo "6. Testing HTTP request..."
HTTP_CODE=$(curl -sk -o /dev/null -w "%{http_code}" --connect-timeout 10 http://$DROPLET_IP 2>/dev/null || echo "000")
if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "301" ] || [ "$HTTP_CODE" == "302" ]; then
    echo -e "${GREEN}✅ HTTP responds with code: $HTTP_CODE${NC}"
else
    echo -e "${RED}❌ HTTP error or timeout (code: $HTTP_CODE)${NC}"
fi
echo ""

# Test 7: HTTPS Request
echo "7. Testing HTTPS request..."
HTTPS_CODE=$(curl -sk -o /dev/null -w "%{http_code}" --connect-timeout 10 https://$DROPLET_IP 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" == "200" ] || [ "$HTTPS_CODE" == "301" ] || [ "$HTTPS_CODE" == "302" ]; then
    echo -e "${GREEN}✅ HTTPS responds with code: $HTTPS_CODE${NC}"
else
    echo -e "${RED}❌ HTTPS error or timeout (code: $HTTPS_CODE)${NC}"
fi
echo ""

# Test 8: Odoo Health Check
echo "8. Testing Odoo health endpoint..."
HEALTH_CODE=$(curl -sk -o /dev/null -w "%{http_code}" --connect-timeout 10 http://$DROPLET_IP/web/health 2>/dev/null || echo "000")
if [ "$HEALTH_CODE" == "200" ]; then
    echo -e "${GREEN}✅ Odoo health check passed${NC}"
else
    echo -e "${RED}❌ Odoo health check failed (code: $HEALTH_CODE)${NC}"
fi
echo ""

# Test 9: SSL Certificate
echo "9. Checking SSL certificate..."
if timeout 10 openssl s_client -connect $DROPLET_IP:443 -servername $DOMAIN </dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    echo -e "${GREEN}✅ SSL certificate is valid${NC}"
else
    echo -e "${YELLOW}⚠️ SSL certificate issue or not configured${NC}"
fi
echo ""

# SSH Diagnostic Commands (if SSH access available)
echo "========================================="
echo "SSH Diagnostic Commands (run on droplet)"
echo "========================================="
echo ""
echo "If you have SSH access, run these commands:"
echo ""
echo "# Check Odoo service status"
echo "sudo systemctl status odoo19"
echo ""
echo "# Check Nginx status"
echo "sudo systemctl status nginx"
echo ""
echo "# Check firewall rules"
echo "sudo ufw status verbose"
echo ""
echo "# Check listening ports"
echo "sudo netstat -tulpn | grep -E '(80|443|8069)'"
echo ""
echo "# Check Odoo logs"
echo "sudo journalctl -u odoo19 -n 50 --no-pager"
echo ""
echo "# Check Nginx logs"
echo "sudo tail -n 50 /var/log/nginx/error.log"
echo ""

# Summary
echo "========================================="
echo "Summary"
echo "========================================="
echo ""
if [ "$DNS_IP" == "$DROPLET_IP" ] && ([ "$HTTP_CODE" == "200" ] || [ "$HTTPS_CODE" == "200" ]); then
    echo -e "${GREEN}✅ ERP endpoint appears to be working!${NC}"
elif [ "$DNS_IP" != "$DROPLET_IP" ]; then
    echo -e "${RED}❌ DNS configuration issue${NC}"
elif [ "$HTTP_CODE" == "000" ] && [ "$HTTPS_CODE" == "000" ]; then
    echo -e "${RED}❌ Droplet is unreachable or firewall is blocking${NC}"
    echo ""
    echo "Possible causes:"
    echo "1. UFW firewall blocking ports 80/443"
    echo "2. Odoo service not running"
    echo "3. Nginx not configured or not running"
    echo "4. DigitalOcean Cloud Firewall blocking access"
    echo ""
    echo "Action required: SSH into droplet and run diagnostic commands above"
else
    echo -e "${YELLOW}⚠️ Partial connectivity - check service status${NC}"
fi
echo ""
