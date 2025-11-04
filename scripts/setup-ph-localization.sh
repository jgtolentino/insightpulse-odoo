#!/bin/bash
# Setup Philippine Accounting Localization for Odoo 19
# Installs l10n_ph modules and configures for BIR compliance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="${DB_NAME:-insightpulse_prod}"
ODOO_BIN="${ODOO_BIN:-/opt/odoo16/odoo16-venv/bin/python /opt/odoo16/odoo16/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo16.conf}"

echo -e "${BLUE}🇵🇭 Philippine Accounting Localization Setup${NC}"
echo "==========================================="
echo ""

# Step 1: Check if database exists
echo -e "${BLUE}📋 Step 1: Checking database...${NC}"
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" != "1" ]; then
    echo -e "${RED}❌ Database '$DB_NAME' does not exist!${NC}"
    echo "   Create it first at: https://erp.insightpulseai.net/web/database/manager"
    echo "   Master password: 2ca2a768b7c9016f52364921bb78ab2a359da05a23dd0bf1"
    exit 1
fi

echo -e "${GREEN}✅ Database found: $DB_NAME${NC}"
echo ""

# Step 2: Check current module status
echo -e "${BLUE}📋 Step 2: Checking current modules...${NC}"

sudo -u odoo16 $ODOO_BIN shell -d "$DB_NAME" -c "$ODOO_CONF" --no-http <<'EOF'
import sys
env = self.env
mods = env['ir.module.module'].search([('name', 'ilike', 'l10n_ph')])

if not mods:
    print("❌ No PH modules found in module list")
    sys.exit(0)

print("\nCurrent PH modules:")
for mod in mods:
    status = "✅" if mod.state == "installed" else "⚠️ "
    print(f"  {status} {mod.name}: {mod.state}")

sys.exit(0)
EOF

echo ""

# Step 3: Install base PH localization
echo -e "${BLUE}📋 Step 3: Installing l10n_ph (base PH Chart of Accounts)...${NC}"

sudo -u odoo16 $ODOO_BIN -d "$DB_NAME" -c "$ODOO_CONF" -i l10n_ph --stop-after-init --no-http

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ l10n_ph installed successfully${NC}"
else
    echo -e "${RED}❌ l10n_ph installation failed${NC}"
    exit 1
fi

echo ""

# Step 4: Install withholding tax module (if available)
echo -e "${BLUE}📋 Step 4: Installing l10n_ph_withholding (EWT/2307)...${NC}"

sudo -u odoo16 $ODOO_BIN -d "$DB_NAME" -c "$ODOO_CONF" -i l10n_ph_withholding --stop-after-init --no-http 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ l10n_ph_withholding installed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  l10n_ph_withholding not available (may not exist in Odoo 16/19)${NC}"
    echo "   You can add OCA modules later if needed."
fi

echo ""

# Step 5: Verify installation
echo -e "${BLUE}📋 Step 5: Verifying installation...${NC}"

VERIFICATION=$(sudo -u odoo16 $ODOO_BIN shell -d "$DB_NAME" -c "$ODOO_CONF" --no-http <<'EOF'
import sys
env = self.env

# Check l10n_ph
l10n_ph = env['ir.module.module'].search([('name', '=', 'l10n_ph')])
if not l10n_ph or l10n_ph.state != 'installed':
    print("FAIL: l10n_ph not installed")
    sys.exit(1)

# Check chart of accounts
coa_count = env['account.account'].search_count([])
if coa_count < 10:
    print("FAIL: Chart of accounts not loaded (found only {coa_count} accounts)")
    sys.exit(1)

# Check taxes
tax_count = env['account.tax'].search_count([])
if tax_count < 3:
    print("FAIL: Taxes not configured (found only {tax_count} taxes)")
    sys.exit(1)

print("PASS")
sys.exit(0)
EOF
)

if echo "$VERIFICATION" | grep -q "PASS"; then
    echo -e "${GREEN}✅ Verification passed${NC}"
else
    echo -e "${RED}❌ Verification failed:${NC}"
    echo "$VERIFICATION"
    exit 1
fi

echo ""

# Step 6: Configuration checklist
echo -e "${BLUE}📋 Step 6: Configuration Checklist${NC}"
echo ""
echo -e "${YELLOW}⚠️  Manual steps required in Odoo web interface:${NC}"
echo ""
echo "1. Login to Odoo: https://erp.insightpulseai.net"
echo "   Database: $DB_NAME"
echo "   Admin: (use your admin email/password)"
echo ""
echo "2. Company Settings:"
echo "   Settings → Companies → Your Company"
echo "   - Country: Philippines"
echo "   - Currency: PHP (Philippine Peso)"
echo "   - TIN: (enter your BIR TIN)"
echo ""
echo "3. Accounting Settings:"
echo "   Settings → Accounting"
echo "   - Chart of Accounts: Review loaded accounts"
echo "   - Taxes:"
echo "     * VAT 12% (Sales and Purchase)"
echo "     * Zero-rated (0%)"
echo "     * VAT-exempt"
echo "     * EWT rates (1%, 2%, 5%, 10% as needed)"
echo ""
echo "4. Fiscal Positions:"
echo "   Accounting → Configuration → Fiscal Positions"
echo "   Create:"
echo "   - Domestic VATable"
echo "   - Zero-rated (Export)"
echo "   - VAT Exempt"
echo ""
echo "5. Journals:"
echo "   Accounting → Configuration → Journals"
echo "   Verify:"
echo "   - Sales Journal"
echo "   - Purchase Journal"
echo "   - Cash Journal"
echo "   - Bank Journals"
echo "   - Withholding Tax Journal (if using EWT)"
echo ""
echo "6. Test Transactions:"
echo "   - Create a test invoice with VAT 12%"
echo "   - Verify accounting entries are correct"
echo "   - Check Tax Report shows correct figures"
echo ""

# Step 7: BIR Forms (if available)
echo -e "${BLUE}📋 Step 7: BIR Forms Configuration${NC}"
echo ""
echo "Required BIR Forms for Philippine businesses:"
echo ""
echo "Monthly:"
echo "  1601-C - Monthly Remittance Return of Income Taxes Withheld"
echo "  1601-F - Monthly Remittance of Final Withholding Taxes"
echo ""
echo "Quarterly:"
echo "  2550Q - Quarterly VAT Return"
echo ""
echo "Annual:"
echo "  1702-RT - Annual Income Tax Return (Regular/Non-Individual)"
echo "  2316 - Certificate of Compensation Payment/Tax Withheld"
echo ""
echo -e "${YELLOW}⚠️  Note: BIR form templates not included in base l10n_ph.${NC}"
echo "   You may need:"
echo "   - Custom report templates for BIR formats"
echo "   - OCA modules: https://github.com/OCA/l10n-philippines"
echo "   - Third-party BIR eFiling integration"
echo ""

# Step 8: Testing script
echo -e "${BLUE}📋 Step 8: Generating test script...${NC}"

cat > /tmp/test-ph-localization.py <<'PYEOF'
#!/usr/bin/env python3
"""Test Philippine localization setup"""

import sys

def test_modules(env):
    """Test required modules are installed"""
    l10n_ph = env['ir.module.module'].search([('name', '=', 'l10n_ph')])
    assert l10n_ph.state == 'installed', "l10n_ph not installed"
    print("✅ l10n_ph module installed")

def test_chart_of_accounts(env):
    """Test chart of accounts is loaded"""
    accounts = env['account.account'].search([])
    assert len(accounts) >= 50, f"Only {len(accounts)} accounts found (expected 50+)"
    print(f"✅ Chart of Accounts loaded: {len(accounts)} accounts")

def test_taxes(env):
    """Test Philippine taxes are configured"""
    vat_12 = env['account.tax'].search([('name', 'ilike', '12%')], limit=1)
    assert vat_12, "VAT 12% tax not found"
    print(f"✅ VAT 12% configured: {vat_12.name}")

    zero_rated = env['account.tax'].search([('name', 'ilike', 'zero')], limit=1)
    if zero_rated:
        print(f"✅ Zero-rated tax configured: {zero_rated.name}")

def test_company_settings(env):
    """Test company is configured for Philippines"""
    company = env.user.company_id
    assert company.country_id.code == 'PH', "Company country not set to Philippines"
    print(f"✅ Company country: {company.country_id.name}")

    assert company.currency_id.name == 'PHP', "Company currency not set to PHP"
    print(f"✅ Company currency: {company.currency_id.name}")

def run_tests(env):
    """Run all tests"""
    print("\n🧪 Testing Philippine Localization...")
    print("=" * 50)

    try:
        test_modules(env)
        test_chart_of_accounts(env)
        test_taxes(env)
        test_company_settings(env)

        print("=" * 50)
        print("✅ All tests passed!")
        return 0

    except AssertionError as e:
        print("=" * 50)
        print(f"❌ Test failed: {e}")
        return 1
    except Exception as e:
        print("=" * 50)
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    # This script is meant to be run via odoo shell
    # Usage: odoo shell -d DB_NAME < test-ph-localization.py
    sys.exit(run_tests(self.env))
PYEOF

echo -e "${GREEN}✅ Test script created: /tmp/test-ph-localization.py${NC}"
echo ""
echo "Run tests with:"
echo "  sudo -u odoo16 $ODOO_BIN shell -d $DB_NAME -c $ODOO_CONF --no-http < /tmp/test-ph-localization.py"
echo ""

# Final summary
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Philippine Localization Setup Complete!       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Complete manual configuration checklist above"
echo "  2. Run test script to verify setup"
echo "  3. Create test transactions"
echo "  4. Configure BIR forms and reports"
echo ""
echo "Documentation:"
echo "  - Odoo Accounting: https://www.odoo.com/documentation/19.0/applications/finance/accounting.html"
echo "  - OCA l10n-philippines: https://github.com/OCA/l10n-philippines"
echo "  - BIR eFPS: https://www.bir.gov.ph/index.php/eservices/efps.html"
echo ""
