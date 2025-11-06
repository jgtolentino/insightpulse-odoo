#!/bin/bash
# Install all Odoo 16 modules - Complete workflow
# Run this on your local machine where Docker/Colima is running

set -e

echo "=== Step 1: Initialize database with base modules ==="
docker exec -it odoo16_app odoo \
  -d odoo16 \
  --without-demo=all \
  --load-language=en_US \
  -i base \
  --stop-after-init

echo ""
echo "=== Step 2: Install core Odoo modules ==="
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -i web,account,hr_expense,stock,sale,purchase,project,website \
  --stop-after-init

echo ""
echo "=== Step 3: Install custom IP Expense MVP module ==="
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -i ip_expense_mvp \
  --stop-after-init

echo ""
echo "=== Step 4: Configure system parameters (OCR URL) ==="
docker exec -it odoo16_postgres psql -U odoo16 -d odoo16 << 'EOF'
INSERT INTO ir_config_parameter (key, value, create_date, write_date)
VALUES (
  'ip_expense.ocr_api_url',
  'https://ocr.insightpulseai.net/api/v1/extract',
  NOW(),
  NOW()
)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
EOF

echo ""
echo "=== Step 5: Upgrade all modules ==="
docker exec -it odoo16_app odoo \
  -d odoo16 \
  -u all \
  --stop-after-init

echo ""
echo "=== Step 6: Verify installation ==="
docker exec -it odoo16_postgres psql -U odoo16 -d odoo16 -c \
  "SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;"

echo ""
echo "=== Step 7: Start Odoo in normal mode ==="
docker compose -f docker-compose.odoo16.yml restart odoo16_app

echo ""
echo "✅ All modules installed successfully!"
echo "🌐 Access Odoo at: http://localhost:8069"
echo ""
echo "Login credentials:"
echo "  - Email: admin@example.com"
echo "  - Password: admin123"
