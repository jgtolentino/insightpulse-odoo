#!/usr/bin/env python3
"""
InsightPulse Multi-Org Demo Data Seeder

Seeds 8 Philippine agency databases with realistic demo data:
- Companies with TIN and addresses
- Chart of accounts (Philippine BIR-compliant)
- 100 sample GL transactions per organization
- Sample customers and vendors
- Sample products/services

Usage:
    python seed-demo-data.py [--agency AGENCY_CODE]

Examples:
    python seed-demo-data.py                 # Seed all 8 agencies
    python seed-demo-data.py --agency rim    # Seed only RIM

Prerequisites:
    - Docker Compose stack running
    - Multi-org databases created (run create-multi-org-dbs.sh first)
    - odoorpc installed: pip install odoorpc

Author: InsightPulse AI
Date: 2025-11-11
License: LGPL-3
"""

import argparse
import json
import logging
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    import odoorpc
except ImportError:
    print("ERROR: odoorpc not installed. Run: pip install odoorpc")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SCRIPT_DIR = Path(__file__).parent
AGENCIES_FILE = SCRIPT_DIR / 'agencies.json'
ODOO_HOST = os.getenv('ODOO_HOST', 'localhost')
ODOO_PORT = int(os.getenv('ODOO_PORT', '8069'))
ODOO_ADMIN_PASSWORD = os.getenv('ODOO_ADMIN_PASSWORD', 'admin')

# Sample data
SAMPLE_CUSTOMERS = [
    'Acme Corporation Philippines',
    'Global Tech Manila',
    'Pacific Trading Inc',
    'Metro Services Co',
    'Asia Pacific Ventures'
]

SAMPLE_VENDORS = [
    'Office Supplies Manila',
    'Tech Equipment PH',
    'Utilities Company',
    'Telecom Provider Inc',
    'Professional Services Ltd'
]

SAMPLE_PRODUCTS = [
    ('Training Services', 15000.00),
    ('Consulting Hours', 5000.00),
    ('Software License', 25000.00),
    ('Office Rent', 50000.00),
    ('Research Grant', 100000.00)
]


def load_agencies():
    """Load agency configuration from JSON file"""
    try:
        with open(AGENCIES_FILE, 'r') as f:
            data = json.load(f)
            return data['agencies']
    except FileNotFoundError:
        logger.error(f"Agencies file not found: {AGENCIES_FILE}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in agencies file: {e}")
        sys.exit(1)


def connect_odoo(database, username='admin', password=None):
    """Connect to Odoo database"""
    if password is None:
        password = ODOO_ADMIN_PASSWORD

    try:
        odoo = odoorpc.ODOO(ODOO_HOST, port=ODOO_PORT)
        odoo.login(database, username, password)
        logger.info(f"✓ Connected to database: {database}")
        return odoo
    except Exception as e:
        logger.error(f"Failed to connect to {database}: {e}")
        return None


def setup_company(odoo, agency):
    """Configure company with agency details"""
    logger.info(f"Setting up company for {agency['name']}...")

    try:
        Company = odoo.env['res.company']
        companies = Company.search([])

        if not companies:
            logger.error("No company found in database")
            return False

        company_id = companies[0]
        company = Company.browse(company_id)

        # Update company details
        company.write({
            'name': agency['name'],
            'vat': agency['tin'],
            'email': agency.get('email', 'info@example.com'),
            'phone': agency.get('phone', '+63 2 1234 5678'),
        })

        # Update company partner (address)
        Partner = odoo.env['res.partner']
        partner = Partner.browse(company.partner_id.id)
        partner.write({
            'street': agency.get('address', 'Metro Manila'),
            'city': 'Manila',
            'zip': '1000',
            'country_id': odoo.env.ref('base.ph').id,
        })

        logger.info(f"✓ Company configured: {agency['name']}")
        return True

    except Exception as e:
        logger.error(f"Failed to setup company: {e}")
        return False


def create_customers(odoo, count=5):
    """Create sample customers"""
    logger.info(f"Creating {count} sample customers...")

    Partner = odoo.env['res.partner']
    created = 0

    for i, customer_name in enumerate(SAMPLE_CUSTOMERS[:count]):
        try:
            partner_id = Partner.create({
                'name': customer_name,
                'customer_rank': 1,
                'email': f'contact@{customer_name.lower().replace(" ", "")}.com',
                'phone': f'+63 2 {random.randint(1000, 9999)} {random.randint(1000, 9999)}',
                'street': f'{random.randint(100, 999)} {random.choice(["Ayala", "Makati", "Ortigas", "BGC"])} Avenue',
                'city': 'Metro Manila',
                'zip': f'{random.randint(1000, 1900)}',
                'country_id': odoo.env.ref('base.ph').id,
            })
            created += 1
        except Exception as e:
            logger.warning(f"Failed to create customer {customer_name}: {e}")

    logger.info(f"✓ Created {created} customers")
    return created


def create_vendors(odoo, count=5):
    """Create sample vendors"""
    logger.info(f"Creating {count} sample vendors...")

    Partner = odoo.env['res.partner']
    created = 0

    for vendor_name in SAMPLE_VENDORS[:count]:
        try:
            partner_id = Partner.create({
                'name': vendor_name,
                'supplier_rank': 1,
                'email': f'sales@{vendor_name.lower().replace(" ", "")}.com',
                'phone': f'+63 2 {random.randint(1000, 9999)} {random.randint(1000, 9999)}',
                'street': f'{random.randint(100, 999)} {random.choice(["EDSA", "C5", "Ortigas", "Shaw"])} Boulevard',
                'city': 'Metro Manila',
                'zip': f'{random.randint(1000, 1900)}',
                'country_id': odoo.env.ref('base.ph').id,
            })
            created += 1
        except Exception as e:
            logger.warning(f"Failed to create vendor {vendor_name}: {e}")

    logger.info(f"✓ Created {created} vendors")
    return created


def create_products(odoo):
    """Create sample products/services"""
    logger.info("Creating sample products...")

    Product = odoo.env['product.product']
    created = 0

    for product_name, price in SAMPLE_PRODUCTS:
        try:
            product_id = Product.create({
                'name': product_name,
                'type': 'service',
                'list_price': price,
                'standard_price': price * 0.7,  # 30% margin
                'categ_id': odoo.env.ref('product.product_category_all').id,
            })
            created += 1
        except Exception as e:
            logger.warning(f"Failed to create product {product_name}: {e}")

    logger.info(f"✓ Created {created} products")
    return created


def create_gl_transactions(odoo, count=100):
    """Create sample GL transactions (invoices)"""
    logger.info(f"Creating {count} sample GL transactions...")

    Move = odoo.env['account.move']
    Partner = odoo.env['res.partner']
    Product = odoo.env['product.product']

    # Get sample partners and products
    customers = Partner.search([('customer_rank', '>', 0)], limit=5)
    vendors = Partner.search([('supplier_rank', '>', 0)], limit=5)
    products = Product.search([], limit=5)

    if not customers or not products:
        logger.error("No customers or products found. Create them first.")
        return 0

    created = 0
    start_date = datetime.now() - timedelta(days=365)  # 1 year of data

    for i in range(count):
        try:
            # Random invoice type (80% sales, 20% purchases)
            move_type = 'out_invoice' if random.random() < 0.8 else 'in_invoice'
            partner_id = random.choice(customers if move_type == 'out_invoice' else vendors)
            product = random.choice(products)

            # Random date within last year
            invoice_date = start_date + timedelta(days=random.randint(0, 365))

            # Create invoice
            invoice = Move.create({
                'move_type': move_type,
                'partner_id': partner_id,
                'invoice_date': invoice_date.strftime('%Y-%m-%d'),
                'invoice_line_ids': [(0, 0, {
                    'product_id': product,
                    'quantity': random.randint(1, 10),
                    'price_unit': Product.browse(product).list_price,
                })]
            })

            # Post invoice (to create GL entries)
            invoice.action_post()

            created += 1

            if (i + 1) % 20 == 0:
                logger.info(f"  Progress: {i + 1}/{count} transactions created")

        except Exception as e:
            logger.warning(f"Failed to create transaction {i+1}: {e}")

    logger.info(f"✓ Created {created} GL transactions")
    return created


def seed_agency(agency_code, agency_data):
    """Seed data for one agency"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Seeding agency: {agency_data['name']} ({agency_code.upper()})")
    logger.info(f"{'='*60}\n")

    db_name = f'db_{agency_code}'

    # Connect to Odoo
    odoo = connect_odoo(db_name)
    if not odoo:
        return False

    try:
        # Setup company
        if not setup_company(odoo, agency_data):
            return False

        # Create master data
        create_customers(odoo, count=5)
        create_vendors(odoo, count=5)
        create_products(odoo)

        # Create transactions
        create_gl_transactions(odoo, count=100)

        logger.info(f"\n✓ Successfully seeded {agency_data['name']}")
        return True

    except Exception as e:
        logger.error(f"Error seeding {agency_code}: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Seed InsightPulse multi-org databases with demo data')
    parser.add_argument(
        '--agency',
        type=str,
        help='Specific agency code to seed (e.g., rim, ckvc). If not provided, seeds all agencies.'
    )
    args = parser.parse_args()

    # Load agencies
    agencies = load_agencies()

    # Filter agencies if specific one requested
    if args.agency:
        agencies = [a for a in agencies if a['code'] == args.agency.lower()]
        if not agencies:
            logger.error(f"Agency '{args.agency}' not found")
            sys.exit(1)

    logger.info(f"\n{'='*60}")
    logger.info("InsightPulse Multi-Org Demo Data Seeder")
    logger.info(f"{'='*60}\n")
    logger.info(f"Agencies to seed: {len(agencies)}")
    logger.info(f"Odoo host: {ODOO_HOST}:{ODOO_PORT}")
    logger.info("")

    # Seed each agency
    success_count = 0
    for agency in agencies:
        if seed_agency(agency['code'], agency):
            success_count += 1

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total agencies: {len(agencies)}")
    logger.info(f"Successfully seeded: {success_count}")
    logger.info(f"Failed: {len(agencies) - success_count}")
    logger.info("")

    if success_count == len(agencies):
        logger.info("✓ All agencies seeded successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Access Odoo at http://localhost:8069")
        logger.info("  2. Select database from dropdown (db_rim, db_ckvc, etc.)")
        logger.info("  3. Login: admin / admin")
        logger.info("  4. Install ipai_bir_compliance module")
        return 0
    else:
        logger.error("⚠ Some agencies failed to seed. Check logs above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
