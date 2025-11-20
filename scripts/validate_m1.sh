#!/usr/bin/env bash
################################################################################
# M1 Validation Script
# Purpose: Validate M1 deployment is healthy and meets acceptance criteria
# Usage: sudo bash validate_m1.sh
################################################################################

set -euo pipefail

DOMAIN="erp.insightpulseai.net"
INSTALL_DIR="/opt/odoo-ce"

echo "========================================="
echo "M1 Validation Script"
echo "========================================="
echo ""

# Test 1: Docker containers running
echo "1. Checking Docker containers..."
if docker ps | grep -q "odoo-ce" && docker ps | grep -q "odoo-db"; then
    echo "   ✅ Both containers running"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "   ❌ Containers not running"
    exit 1
fi
echo ""

# Test 2: Health endpoints
echo "2. Checking Odoo health endpoint..."
if curl -sf http://127.0.0.1:8069/web/health > /dev/null; then
    echo "   ✅ Odoo health endpoint responding"
else
    echo "   ❌ Odoo health endpoint not responding"
    exit 1
fi
echo ""

echo "3. Checking HTTPS access..."
if curl -sf "https://$DOMAIN/web/health" > /dev/null; then
    echo "   ✅ HTTPS access working"
else
    echo "   ⚠️  HTTPS not accessible (check DNS and SSL cert)"
fi
echo ""

# Test 3: Firewall configuration
echo "4. Checking UFW firewall..."
if sudo ufw status | grep -q "Status: active"; then
    echo "   ✅ UFW firewall active"
    sudo ufw status numbered | grep -E "(22|80|443)"
else
    echo "   ⚠️  UFW firewall not active"
fi
echo ""

# Test 4: Deployment log
echo "5. Checking deployment log..."
if [ -f "/var/log/odoo_deploy.log" ]; then
    echo "   ✅ Deployment log exists"
    tail -5 /var/log/odoo_deploy.log
else
    echo "   ⚠️  Deployment log not found"
fi
echo ""

# Test 5: Backup cron job
echo "6. Checking backup cron job..."
if crontab -l 2>/dev/null | grep -q "backup_odoo.sh"; then
    echo "   ✅ Backup cron job configured"
    crontab -l | grep backup_odoo
else
    echo "   ⚠️  Backup cron job not found"
    echo "   Run: (crontab -l; echo '0 2 * * * /usr/local/bin/backup_odoo.sh >> /var/log/odoo_backup.log 2>&1') | crontab -"
fi
echo ""

# Test 6: SSL certificate
echo "7. Checking SSL certificate..."
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "   ✅ SSL certificate exists"
    expiry=$(openssl x509 -enddate -noout -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" | cut -d= -f2)
    echo "   Expires: $expiry"
else
    echo "   ⚠️  SSL certificate not found"
fi
echo ""

# Test 7: Resource limits
echo "8. Checking Docker resource limits..."
echo "   PostgreSQL limits:"
docker inspect odoo-db --format '{{.HostConfig.Memory}}' | awk '{print "   Memory: " $1/1024/1024/1024 " GB"}'
docker inspect odoo-db --format '{{.HostConfig.NanoCpus}}' | awk '{print "   CPU: " $1/1000000000 " cores"}'
echo "   Odoo limits:"
docker inspect odoo-ce --format '{{.HostConfig.Memory}}' | awk '{print "   Memory: " $1/1024/1024/1024 " GB"}'
docker inspect odoo-ce --format '{{.HostConfig.NanoCpus}}' | awk '{print "   CPU: " $1/1000000000 " cores"}'
echo ""

# Test 8: Backups
echo "9. Checking backups..."
if [ -d "/opt/odoo-backups" ]; then
    backup_count=$(find /opt/odoo-backups -name "odoo-db-*.sql.gz" | wc -l)
    echo "   ✅ Backup directory exists"
    echo "   Database backups found: $backup_count"
    if [ "$backup_count" -gt 0 ]; then
        latest=$(ls -t /opt/odoo-backups/odoo-db-*.sql.gz | head -1)
        echo "   Latest: $(basename "$latest")"
    fi
else
    echo "   ⚠️  Backup directory not found"
fi
echo ""

echo "========================================="
echo "M1 Validation Summary"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Access https://$DOMAIN/web"
echo "2. Create database 'insightpulse'"
echo "3. Install ipai_expense, ipai_equipment, ipai_ce_cleaner"
echo "4. Verify no Enterprise/IAP banners appear"
echo ""
echo "Validation complete!"
