#!/bin/bash
# InsightPulse ERP - Baseline Validation Script
# Purpose: Capture production state for v0.2.1-quality baseline
# Usage: ./scripts/baseline-validation.sh > baseline-report.txt

set -e

echo "=================================================="
echo "InsightPulse ERP - Baseline Validation Report"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "Baseline Version: v0.2.1-quality"
echo "=================================================="
echo ""

echo "## 1. Production Server Connection"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "echo '✅ SSH connection successful'" || echo "❌ SSH connection failed"
echo ""

echo "## 2. Odoo Service Status"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker ps | grep odoo" || echo "❌ Odoo containers not running"
echo ""

echo "## 3. Installed Modules Count by License"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT license, COUNT(*) as count FROM ir_module_module WHERE state = 'installed' GROUP BY license ORDER BY license;\"" \
  2>/dev/null || echo "❌ Database query failed"
echo ""

echo "## 4. Total Installed Modules"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT COUNT(*) as total_installed FROM ir_module_module WHERE state = 'installed';\"" \
  2>/dev/null || echo "❌ Database query failed"
echo ""

echo "## 5. Enterprise License Validation (Should be 0)"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT COUNT(*) as enterprise_modules FROM ir_module_module WHERE state = 'installed' AND license IN ('OPL-1', 'OEEL-1');\"" \
  2>/dev/null || echo "❌ Database query failed"
echo ""

echo "## 6. odoo.com Links Validation (Should be 0)"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT COUNT(*) as odoo_com_links FROM ir_module_module WHERE website LIKE '%odoo.com%';\"" \
  2>/dev/null || echo "❌ Database query failed"
echo ""

echo "## 7. Custom InsightPulse Modules"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT name, state, license, website FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;\"" \
  2>/dev/null || echo "❌ Database query failed"
echo ""

echo "## 8. OCR Expense Log Records (Quality Metrics)"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT COUNT(*) as total_ocr_scans FROM ocr_expense_log;\"" \
  2>/dev/null || echo "❌ Table not found (module not installed)"
echo ""

echo "## 9. OCR Adapter Health Check"
echo "---------------------------------------------------"
curl -sf https://ocr.insightpulseai.net/health | jq . 2>/dev/null || echo "❌ OCR adapter health check failed"
echo ""

echo "## 10. Database Size"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker exec odoo-db-1 psql -U odoo -d odoo -c \
  \"SELECT pg_size_pretty(pg_database_size('odoo')) as database_size;\"" \
  2>/dev/null || echo "❌ Database query failed"
echo ""

echo "## 11. Odoo Version"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 2>&1 | grep 'Odoo version' | tail -1" || echo "❌ Version check failed"
echo ""

echo "## 12. Worker Status"
echo "---------------------------------------------------"
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 2>&1 | grep 'Worker.*alive' | tail -10" || echo "❌ Worker status check failed"
echo ""

echo "=================================================="
echo "Baseline Validation Complete"
echo "Status: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "=================================================="
echo ""
echo "✅ SUCCESS CRITERIA:"
echo "  - Total modules: 169-175 (LGPL-3 + AGPL-3 only)"
echo "  - Enterprise modules: 0"
echo "  - odoo.com links: 0"
echo "  - Custom ipai modules: 2-5 installed"
echo "  - Odoo version: 18.0-20251106"
echo "  - Workers: 4 HTTP + 1 Cron alive"
echo ""
