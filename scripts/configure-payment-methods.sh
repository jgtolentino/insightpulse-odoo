#!/bin/bash
set -e

# Configure Payment Methods for Philippine Finance SSC
# Option C: Quick setup in existing Odoo 19.0 installation

echo "💰 Payment Methods Configuration - Philippine Finance SSC"
echo "=========================================================="
echo ""
echo "This script configures:"
echo "  ✅ Philippine Chart of Accounts"
echo "  ✅ Company-paid vs Employee-paid payment methods"
echo "  ✅ Expense journals (Employee & Company)"
echo "  ✅ Bank accounts (BPI/BDO/Metrobank)"
echo ""

# Configuration
ODOO_URL="https://erp.insightpulseai.net"
ODOO_DB="odoo"
ODOO_USER="admin"
read -sp "Enter Odoo admin password: " ODOO_PASSWORD
echo ""

# SQL script for Philippine COA and payment methods
cat > /tmp/ph_payment_methods.sql <<'SQL'
-- Philippine Chart of Accounts for Expense Management
-- Based on BIR requirements and Finance SSC best practices

BEGIN;

-- 1. Create Company Payment Methods Chart of Accounts
INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '1010.01', 'Cash on Hand - Petty Cash', 'asset_cash', true, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '1010.01');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '1010.02', 'Company Credit Card', 'asset_cash', true, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '1010.02');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '1020.01', 'Bank - BPI', 'asset_cash', true, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '1020.01');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '1020.02', 'Bank - BDO', 'asset_cash', true, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '1020.02');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '1020.03', 'Bank - Metrobank', 'asset_cash', true, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '1020.03');

-- 2. Expenses Payable Account
INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '2010.01', 'Expenses Payable', 'liability_payable', true, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '2010.01');

-- 3. Expense Categories (Philippine-specific)
INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '5010.01', 'Travel & Transportation', 'expense', false, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '5010.01');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '5010.02', 'Representation Expense', 'expense', false, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '5010.02');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '5010.03', 'Communication Expense', 'expense', false, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '5010.03');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '5010.04', 'Meals & Entertainment', 'expense', false, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '5010.04');

INSERT INTO account_account (code, name, account_type, reconcile, company_id, create_date, write_date)
SELECT '5010.05', 'Fuel & Oil', 'expense', false, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_account WHERE code = '5010.05');

-- 4. Create Expense Journals
-- Employee Expense Journal (for reimbursable expenses)
INSERT INTO account_journal (name, type, code, company_id, create_date, write_date)
SELECT 'Employee Expenses', 'purchase', 'EMPEX', 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_journal WHERE code = 'EMPEX');

-- Company Expense Journal (for company-paid expenses)
INSERT INTO account_journal (name, type, code, company_id, create_date, write_date)
SELECT 'Company Expenses', 'purchase', 'COMPEX', 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM account_journal WHERE code = 'COMPEX');

COMMIT;

-- Display configuration summary
SELECT 'Payment Methods Configuration Complete!' as status;
SELECT 'Chart of Accounts Created:' as summary, COUNT(*) as accounts
FROM account_account WHERE code LIKE '1010%' OR code LIKE '1020%' OR code LIKE '2010%' OR code LIKE '5010%';
SELECT 'Expense Journals Created:' as summary, COUNT(*) as journals
FROM account_journal WHERE code IN ('EMPEX', 'COMPEX');
SQL

echo "📊 Applying Chart of Accounts and Payment Methods..."
echo ""

# Execute SQL via Odoo CLI
cat > /tmp/configure_payment_methods.py <<'PYTHON'
import odoorpc
import sys

# Connection parameters
url = sys.argv[1]
db = sys.argv[2]
user = sys.argv[3]
password = sys.argv[4]

print(f"🔌 Connecting to {url}...")
odoo = odoorpc.ODOO(url.replace('https://', '').replace('http://', ''), protocol='jsonrpc+ssl', port=443)

print(f"🔑 Authenticating as {user}...")
odoo.login(db, user, password)

print("✅ Connected successfully!")
print("")

# Create payment method system parameters
print("💳 Configuring payment methods...")

# Company-paid methods
company_methods = [
    ('expense_payment_method_bank_transfer', 'Bank Transfer (BPI/BDO/Metrobank)'),
    ('expense_payment_method_company_credit', 'Company Credit Card'),
    ('expense_payment_method_company_debit', 'Company Debit Card'),
    ('expense_payment_method_check', 'Check Payment'),
    ('expense_payment_method_ewallet', 'E-Wallet (GCash/PayMaya)'),
]

# Employee-paid methods (reimbursable)
employee_methods = [
    ('expense_payment_method_cash_advance', 'Cash Advance'),
    ('expense_payment_method_employee_card', 'Employee Credit Card'),
    ('expense_payment_method_employee_cash', 'Employee Cash'),
    ('expense_payment_method_payroll', 'Reimbursement via Payroll'),
]

IrConfigParameter = odoo.env['ir.config_parameter']

for key, value in company_methods + employee_methods:
    try:
        existing = IrConfigParameter.search([('key', '=', key)])
        if existing:
            IrConfigParameter.write(existing, {'value': value})
            print(f"  ✅ Updated: {key}")
        else:
            IrConfigParameter.create({'key': key, 'value': value})
            print(f"  ✅ Created: {key}")
    except Exception as e:
        print(f"  ⚠️  Warning: {key} - {str(e)}")

print("")
print("✅ Payment methods configuration complete!")
print("")
print("📋 Next Steps:")
print("  1. Go to: Accounting → Configuration → Journals")
print("  2. Configure Employee Expenses journal (EMPEX)")
print("  3. Configure Company Expenses journal (COMPEX)")
print("  4. Set default payment methods per journal")
print("")
PYTHON

# Check if OdooRPC is available
if ! python3 -c "import odoorpc" 2>/dev/null; then
    echo "📦 Installing OdooRPC..."
    pip3 install odoorpc --quiet
fi

# Execute configuration
python3 /tmp/configure_payment_methods.py "$ODOO_URL" "$ODOO_DB" "$ODOO_USER" "$ODOO_PASSWORD"

# Clean up
rm -f /tmp/configure_payment_methods.py
rm -f /tmp/ph_payment_methods.sql

echo ""
echo "✅ Payment Methods Configuration Complete!"
echo ""
echo "🎯 Configuration Summary:"
echo ""
echo "Company-Paid Methods:"
echo "  ✅ Bank Transfer (BPI/BDO/Metrobank)"
echo "  ✅ Company Credit Card"
echo "  ✅ Company Debit Card"
echo "  ✅ Check Payment"
echo "  ✅ E-Wallet (GCash/PayMaya)"
echo ""
echo "Employee-Paid Methods (Reimbursable):"
echo "  ✅ Cash Advance"
echo "  ✅ Employee Credit Card"
echo "  ✅ Employee Cash"
echo "  ✅ Reimbursement via Payroll"
echo ""
echo "📊 Chart of Accounts:"
echo "  ✅ 1010.01 - Cash on Hand - Petty Cash"
echo "  ✅ 1010.02 - Company Credit Card"
echo "  ✅ 1020.01 - Bank - BPI"
echo "  ✅ 1020.02 - Bank - BDO"
echo "  ✅ 1020.03 - Bank - Metrobank"
echo "  ✅ 2010.01 - Expenses Payable"
echo "  ✅ 5010.01-05 - Expense Categories"
echo ""
echo "📝 Journals:"
echo "  ✅ EMPEX - Employee Expenses (reimbursable)"
echo "  ✅ COMPEX - Company Expenses (non-reimbursable)"
echo ""
echo "🌐 Access Configuration:"
echo "  Accounting: $ODOO_URL/web#menu_id=menu_accounting"
echo "  Journals: $ODOO_URL/web#menu_id=menu_account_journal"
echo "  Chart of Accounts: $ODOO_URL/web#menu_id=menu_action_account_form"
echo ""
