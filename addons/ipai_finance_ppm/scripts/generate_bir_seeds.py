#!/usr/bin/env python3
"""
Generate Odoo XML seed data from BIR Schedule CSV

This script creates comprehensive BIR schedule seed data for:
- 8 employees (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- Multiple form types (1601-C monthly, 2550Q quarterly, W101 weekly)
- Complete 2026 calendar year
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path


def generate_monthly_deadlines(form_type, year=2026):
    """Generate monthly BIR form deadlines for a full year"""
    deadlines = []
    for month in range(1, 13):
        # 1601-C due 10th day of following month
        due_month = month + 1 if month < 12 else 1
        due_year = year if month < 12 else year + 1
        deadline = datetime(due_year, due_month, 10)

        period_start = datetime(year, month, 1)
        period_end = (datetime(year, month + 1, 1) - timedelta(days=1)) if month < 12 else datetime(year, 12, 31)

        deadlines.append({
            'name': f"{form_type} - {period_start.strftime('%B %Y')}",
            'period_covered': f"{period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}",
            'filing_deadline': deadline.strftime('%Y-%m-%d'),
            'prep_deadline': (deadline - timedelta(days=5)).strftime('%Y-%m-%d'),
            'review_deadline': (deadline - timedelta(days=3)).strftime('%Y-%m-%d'),
            'approval_deadline': (deadline - timedelta(days=1)).strftime('%Y-%m-%d'),
        })
    return deadlines


def generate_quarterly_deadlines(form_type, year=2026):
    """Generate quarterly BIR form deadlines"""
    deadlines = []
    quarters = [
        (1, 'Q1', 60),  # Q1 due 60 days after Mar 31
        (2, 'Q2', 60),  # Q2 due 60 days after Jun 30
        (3, 'Q3', 60),  # Q3 due 60 days after Sep 30
        (4, 'Q4', 60),  # Q4 due 60 days after Dec 31
    ]

    for q_num, q_name, days_after in quarters:
        quarter_end = datetime(year, q_num * 3, 1)
        # Get last day of quarter
        if q_num < 4:
            quarter_end = datetime(year, q_num * 3 + 1, 1) - timedelta(days=1)
        else:
            quarter_end = datetime(year, 12, 31)

        deadline = quarter_end + timedelta(days=days_after)
        period_start = datetime(year, (q_num - 1) * 3 + 1, 1)

        deadlines.append({
            'name': f"{form_type} - {year} {q_name}",
            'period_covered': f"{period_start.strftime('%Y-%m-%d')} to {quarter_end.strftime('%Y-%m-%d')}",
            'filing_deadline': deadline.strftime('%Y-%m-%d'),
            'prep_deadline': (deadline - timedelta(days=10)).strftime('%Y-%m-%d'),
            'review_deadline': (deadline - timedelta(days=5)).strftime('%Y-%m-%d'),
            'approval_deadline': (deadline - timedelta(days=2)).strftime('%Y-%m-%d'),
        })
    return deadlines


def generate_xml_records(csv_file, output_file):
    """Generate Odoo XML seed data from CSV"""

    # Read CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        schedules = list(reader)

    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>', '<odoo>', '    <data noupdate="1">']
    xml_lines.append('        <!-- BIR Schedule Templates for 2026 -->')
    xml_lines.append('')

    record_id = 1

    for schedule in schedules:
        employee = schedule['Employee'].strip()
        form_type = schedule['Form Type'].strip()
        frequency = schedule['Frequency'].strip()

        # Skip if employee is "ALL" (special case)
        if employee == 'ALL':
            continue

        # Generate deadlines based on frequency
        if frequency == 'Monthly':
            deadlines = generate_monthly_deadlines(form_type, 2026)
        elif frequency == 'Quarterly':
            deadlines = generate_quarterly_deadlines(form_type, 2026)
        else:
            # Weekly and other frequencies handled separately
            continue

        # Create XML records for each deadline
        for deadline_info in deadlines:
            xml_lines.append(f'        <record id="bir_schedule_{employee.lower()}_{form_type.replace("-", "_").lower()}_{record_id}" model="ipai.finance.bir_schedule">')
            xml_lines.append(f'            <field name="name">{deadline_info["name"]}</field>')
            xml_lines.append(f'            <field name="period_covered">{deadline_info["period_covered"]}</field>')
            xml_lines.append(f'            <field name="filing_deadline">{deadline_info["filing_deadline"]}</field>')
            xml_lines.append(f'            <field name="prep_deadline">{deadline_info["prep_deadline"]}</field>')
            xml_lines.append(f'            <field name="review_deadline">{deadline_info["review_deadline"]}</field>')
            xml_lines.append(f'            <field name="approval_deadline">{deadline_info["approval_deadline"]}</field>')
            xml_lines.append('            <field name="logframe_id" ref="finance_logframe_im2"/>')
            xml_lines.append('            <field name="status">draft</field>')
            xml_lines.append('        </record>')
            xml_lines.append('')
            record_id += 1

    xml_lines.append('    </data>')
    xml_lines.append('</odoo>')

    # Write XML file
    with open(output_file, 'w') as f:
        f.write('\n'.join(xml_lines))

    print(f"✅ Generated {record_id - 1} BIR schedule records")
    print(f"📁 Output: {output_file}")


if __name__ == '__main__':
    csv_file = Path('/Users/tbwa/config/finance/BIR_SCHEDULE_2026.xlsx.csv')
    output_file = Path('/Users/tbwa/odoo-ce/addons/ipai_finance_ppm/data/finance_bir_schedule_2026_full.xml')

    generate_xml_records(csv_file, output_file)
