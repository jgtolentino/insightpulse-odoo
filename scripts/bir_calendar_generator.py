#!/usr/bin/env python3
"""
BIR Compliance Calendar Generator

Generates BIR compliance calendar for Philippine agencies.
Supports Forms: 1601-C (monthly), 2550Q (quarterly), 1702-RT (annual), 2307 (as-needed)

Usage:
    python scripts/bir_calendar_generator.py --month 1 --year 2025 --output docs/bir_calendar_2025_01.json
"""

import os
import json
import argparse
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# BIR Form definitions
BIR_FORMS = {
    '1601-C': {
        'name': 'Monthly Withholding Tax',
        'deadline_day': 10,
        'frequency': 'monthly',
        'agencies': ['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB']
    },
    '1702-RT': {
        'name': 'Annual Income Tax Return',
        'deadline_day': 15,
        'deadline_month': 4,  # April 15
        'frequency': 'annual',
        'agencies': ['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB']
    },
    '2550Q': {
        'name': 'Quarterly VAT Return',
        'deadline_day': 25,
        'frequency': 'quarterly',
        'months': [4, 7, 10, 1],  # Last month of quarter + 25 days
        'agencies': ['RIM', 'CKVC', 'BOM', 'JPAL']
    },
    '2307': {
        'name': 'Certificate of Creditable Tax Withheld',
        'deadline_day': 20,
        'frequency': 'as_needed',
        'agencies': ['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB']
    }
}


def generate_bir_calendar(year: int, month: int) -> list:
    """
    Generate BIR compliance calendar for given month.

    Args:
        year: Calendar year
        month: Calendar month (1-12)

    Returns:
        List of BIR calendar entries
    """
    logger.info(f"Generating BIR compliance calendar for {month}/{year}")

    calendar_entries = []

    for form_code, form_info in BIR_FORMS.items():
        # Check if form is due this month
        is_due = False

        if form_info['frequency'] == 'monthly':
            is_due = True
            deadline = datetime(year, month, form_info['deadline_day'])

        elif form_info['frequency'] == 'quarterly':
            if month in form_info['months']:
                is_due = True
                deadline = datetime(year, month, form_info['deadline_day'])

        elif form_info['frequency'] == 'annual':
            if month == form_info['deadline_month']:
                is_due = True
                deadline = datetime(year, month, form_info['deadline_day'])

        if is_due:
            for agency in form_info['agencies']:
                entry = {
                    'form': form_code,
                    'name': form_info['name'],
                    'agency': agency,
                    'deadline': deadline.strftime('%Y-%m-%d'),
                    'reminder_date': (deadline - timedelta(days=3)).strftime('%Y-%m-%d')
                }
                calendar_entries.append(entry)

    logger.info(f"✅ Generated {len(calendar_entries)} BIR compliance entries")
    return calendar_entries


def main():
    parser = argparse.ArgumentParser(description='Generate BIR compliance calendar')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--year', type=int, required=True, help='Year (YYYY)')
    parser.add_argument('--output', default='docs/bir_calendar.json', help='Output JSON file')
    args = parser.parse_args()

    calendar_entries = generate_bir_calendar(year=args.year, month=args.month)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(calendar_entries, f, indent=2)

    logger.info(f"📄 Saved to: {args.output}")


if __name__ == '__main__':
    main()
