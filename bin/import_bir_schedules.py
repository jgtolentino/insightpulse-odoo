#!/usr/bin/env python3
"""
Parse BIR schedule XML and generate SQL INSERT statements for direct database loading.
This bypasses Odoo's noupdate mechanism entirely.
"""

import xml.etree.ElementTree as ET
import sys
from datetime import datetime

def parse_bir_xml(xml_file):
    """Parse Odoo XML data file and extract BIR schedule records."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    records = []
    for record in root.findall('.//record[@model="ipai.finance.bir_schedule"]'):
        rec_id = record.get('id')
        rec_data = {'xml_id': rec_id}

        for field in record.findall('field'):
            field_name = field.get('name')
            field_value = field.text
            rec_data[field_name] = field_value

        records.append(rec_data)

    return records

def generate_sql_inserts(records):
    """Generate SQL INSERT statements from parsed records."""
    sql_statements = []

    for i, rec in enumerate(records, 1):
        # Get values with defaults
        name = rec.get('name', 'Unknown').replace("'", "''")
        period = rec.get('period_covered', 'N/A').replace("'", "''")
        filing_date = rec.get('filing_deadline', '2026-01-01')
        prep_date = rec.get('prep_deadline', '2026-01-01')
        review_date = rec.get('review_deadline', '2026-01-01')
        approval_date = rec.get('approval_deadline', '2026-01-01')
        status = rec.get('status', 'draft').replace("'", "''")

        sql = f"""
INSERT INTO ipai_finance_bir_schedule (
    id, create_uid, create_date, write_uid, write_date,
    name, period_covered, filing_deadline, prep_deadline,
    review_deadline, approval_deadline, status
) VALUES (
    {i}, 1, NOW(), 1, NOW(),
    '{name}', '{period}', '{filing_date}', '{prep_date}',
    '{review_date}', '{approval_date}', '{status}'
) ON CONFLICT (id) DO NOTHING;"""

        sql_statements.append(sql)

    return sql_statements

def main():
    xml_file = '/Users/tbwa/odoo-ce/addons/ipai_finance_ppm/data/finance_bir_schedule_2026_full.xml'

    print("Parsing BIR schedule XML...", file=sys.stderr)
    records = parse_bir_xml(xml_file)
    print(f"Found {len(records)} BIR schedule records", file=sys.stderr)

    print("Generating SQL INSERT statements...", file=sys.stderr)
    sql_statements = generate_sql_inserts(records)

    # Output SQL to stdout
    print("BEGIN;")
    for sql in sql_statements:
        print(sql)
    print("COMMIT;")

    print(f"Generated {len(sql_statements)} SQL statements", file=sys.stderr)

if __name__ == '__main__':
    main()
