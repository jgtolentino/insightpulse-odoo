#!/usr/bin/env python3
"""
Month-End Closing Tasks Generator

Generates month-end closing tasks for Finance SSC agencies.
8 agencies × 8 tasks = 64 automated tasks per month.

Usage:
    python scripts/month_end_generator.py --year 2025 --month 1 --output docs/month_end_tasks_2025_01.json
"""

import argparse
import calendar
import json
import logging
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

AGENCIES = ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"]

CLOSING_TASKS = [
    {
        "task": "Bank Reconciliation",
        "priority": "critical",
        "deadline_offset": 3,
        "subtasks": [
            "Download bank statements",
            "Match deposits and withdrawals",
            "Investigate unreconciled items",
            "Prepare reconciliation report",
            "Get Finance Officer approval",
        ],
    },
    {
        "task": "Accounts Payable Review",
        "priority": "high",
        "deadline_offset": 4,
        "subtasks": [
            "Review pending invoices",
            "Verify aging report accuracy",
            "Schedule payments for next month",
            "Update payment tracking sheet",
        ],
    },
    {
        "task": "Accounts Receivable Review",
        "priority": "high",
        "deadline_offset": 4,
        "subtasks": [
            "Review aging report",
            "Follow up on overdue accounts",
            "Prepare collection letters",
            "Update receivables tracking",
        ],
    },
    {
        "task": "Expense Report Processing",
        "priority": "high",
        "deadline_offset": 5,
        "subtasks": [
            "Review pending expense reports",
            "Verify receipts and documentation",
            "Process approved reports",
            "Schedule reimbursements",
        ],
    },
    {
        "task": "General Ledger Review",
        "priority": "critical",
        "deadline_offset": 5,
        "subtasks": [
            "Review all journal entries",
            "Verify account balances",
            "Post adjusting entries",
            "Run trial balance report",
            "Review for errors or anomalies",
        ],
    },
    {
        "task": "Fixed Assets Review",
        "priority": "medium",
        "deadline_offset": 6,
        "subtasks": [
            "Record new asset acquisitions",
            "Process disposals",
            "Calculate depreciation",
            "Update asset register",
        ],
    },
    {
        "task": "Payroll Reconciliation",
        "priority": "high",
        "deadline_offset": 5,
        "subtasks": [
            "Verify payroll transactions posted",
            "Reconcile to payroll reports",
            "Review withholding tax accruals",
            "Update employee records if needed",
        ],
    },
    {
        "task": "Financial Reports Generation",
        "priority": "critical",
        "deadline_offset": 7,
        "subtasks": [
            "Generate income statement",
            "Generate balance sheet",
            "Generate cash flow statement",
            "Prepare management reports",
            "Submit to Finance Manager for review",
        ],
    },
]


def generate_month_end_tasks(year: int, month: int) -> list:
    """
    Generate month-end closing tasks.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        List of month-end tasks
    """
    month_name = calendar.month_name[month]
    logger.info(f"Generating month-end tasks for {month_name} {year}")

    last_day = calendar.monthrange(year, month)[1]
    month_end = datetime(year, month, last_day)

    all_tasks = []

    for agency in AGENCIES:
        for task_template in CLOSING_TASKS:
            deadline = month_end + relativedelta(days=task_template["deadline_offset"])

            task = {
                "agency": agency,
                "task": task_template["task"],
                "priority": task_template["priority"],
                "deadline": deadline.strftime("%Y-%m-%d"),
                "month": f"{month_name} {year}",
                "subtasks": task_template["subtasks"],
            }
            all_tasks.append(task)

    logger.info(f"✅ Generated {len(all_tasks)} month-end tasks")
    return all_tasks


def main():
    parser = argparse.ArgumentParser(description="Generate month-end closing tasks")
    parser.add_argument("--year", type=int, required=True, help="Year (YYYY)")
    parser.add_argument("--month", type=int, required=True, help="Month (1-12)")
    parser.add_argument(
        "--output", default="docs/month_end_tasks.json", help="Output JSON file"
    )
    args = parser.parse_args()

    tasks = generate_month_end_tasks(year=args.year, month=args.month)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(tasks, f, indent=2)

    logger.info(f"📄 Saved to: {args.output}")


if __name__ == "__main__":
    main()
