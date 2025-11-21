#!/usr/bin/env python3
"""
import_month_end_tasks.py - Import and deduplicate month-end closing tasks

Purpose:
  Import CSV month-end tasks into Supabase with deduplication logic.
  Validates employee codes, cluster codes, and calculates due dates.

Usage:
  python3 scripts/import_month_end_tasks.py --csv data/month_end_tasks.csv --month-end 2025-01-31

Environment Variables:
  POSTGRES_URL - Supabase connection string with service role key

Dependencies:
  pip install psycopg2-binary python-dotenv pandas
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def log_info(message: str):
    print(f"{BLUE}[INFO]{NC} {message}")


def log_success(message: str):
    print(f"{GREEN}[SUCCESS]{NC} {message}")


def log_warning(message: str):
    print(f"{YELLOW}[WARNING]{NC} {message}")


def log_error(message: str):
    print(f"{RED}[ERROR]{NC} {message}")


def parse_relative_date(relative_due: str) -> Optional[int]:
    """
    Parse relative date string (M-5, M+4) and return offset in days.

    Args:
        relative_due: Relative date string (e.g., 'M-5', 'M+4')

    Returns:
        Integer offset in days, or None if invalid format
    """
    relative_due = relative_due.strip().upper()

    if relative_due.startswith('M-'):
        try:
            return -int(relative_due[2:])
        except ValueError:
            return None
    elif relative_due.startswith('M+'):
        try:
            return int(relative_due[2:])
        except ValueError:
            return None
    elif relative_due == 'M':
        return 0

    return None


def calculate_due_date(month_end: datetime, relative_due: str) -> Optional[datetime]:
    """
    Calculate actual due date from month-end and relative due string.

    Args:
        month_end: Month-end date
        relative_due: Relative due string (e.g., 'M-5', 'M+4')

    Returns:
        Calculated due date, or None if invalid
    """
    offset = parse_relative_date(relative_due)
    if offset is None:
        return None

    return month_end + timedelta(days=offset)


def load_csv_data(csv_path: str) -> List[Dict]:
    """
    Load and parse CSV data.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of task dictionaries
    """
    tasks = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tasks.append({
                    'name': row.get('Task Name', '').strip(),
                    'owner_code': row.get('Owner', '').strip().upper(),
                    'reviewer_code': row.get('Reviewer', '').strip().upper() if row.get('Reviewer') else None,
                    'approver_code': row.get('Approver', '').strip().upper() if row.get('Approver') else None,
                    'cluster_code': row.get('Cluster', '').strip().upper(),
                    'relative_due': row.get('Due Date', '').strip().upper(),
                })

        log_success(f"Loaded {len(tasks)} tasks from CSV")
        return tasks

    except FileNotFoundError:
        log_error(f"CSV file not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        log_error(f"Error reading CSV: {e}")
        sys.exit(1)


def deduplicate_tasks(tasks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Deduplicate tasks by name (case-insensitive).

    Args:
        tasks: List of task dictionaries

    Returns:
        Tuple of (unique_tasks, duplicates)
    """
    seen = {}
    unique = []
    duplicates = []

    for task in tasks:
        name_key = task['name'].lower()

        if name_key in seen:
            duplicates.append(task)
            log_warning(f"Duplicate task: {task['name']}")
        else:
            seen[name_key] = True
            unique.append(task)

    log_info(f"Found {len(duplicates)} duplicate tasks")
    log_success(f"Kept {len(unique)} unique tasks")

    return unique, duplicates


def validate_task(task: Dict, valid_employees: set, valid_clusters: set) -> Tuple[bool, str]:
    """
    Validate a single task.

    Args:
        task: Task dictionary
        valid_employees: Set of valid employee codes
        valid_clusters: Set of valid cluster codes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if not task['name']:
        return False, "Missing task name"

    if not task['owner_code']:
        return False, "Missing owner code"

    if not task['cluster_code']:
        return False, "Missing cluster code"

    if not task['relative_due']:
        return False, "Missing relative due date"

    # Validate owner exists
    if task['owner_code'] not in valid_employees:
        return False, f"Invalid owner code: {task['owner_code']}"

    # Validate reviewer if present
    if task['reviewer_code'] and task['reviewer_code'] not in valid_employees:
        return False, f"Invalid reviewer code: {task['reviewer_code']}"

    # Validate approver if present
    if task['approver_code'] and task['approver_code'] not in valid_employees:
        return False, f"Invalid approver code: {task['approver_code']}"

    # Validate cluster
    if task['cluster_code'] not in valid_clusters:
        return False, f"Invalid cluster code: {task['cluster_code']}"

    # Validate relative due format
    if parse_relative_date(task['relative_due']) is None:
        return False, f"Invalid relative due format: {task['relative_due']}"

    return True, ""


def get_database_connection(postgres_url: str):
    """
    Create database connection.

    Args:
        postgres_url: PostgreSQL connection string

    Returns:
        psycopg2 connection object
    """
    try:
        conn = psycopg2.connect(postgres_url)
        log_success("Connected to Supabase")
        return conn
    except Exception as e:
        log_error(f"Failed to connect to database: {e}")
        sys.exit(1)


def fetch_valid_codes(conn) -> Tuple[set, set]:
    """
    Fetch valid employee and cluster codes from database.

    Args:
        conn: Database connection

    Returns:
        Tuple of (employee_codes, cluster_codes)
    """
    cursor = conn.cursor()

    # Fetch employee codes
    cursor.execute("SELECT code FROM public.month_end_employees WHERE active = true")
    employee_codes = {row[0] for row in cursor.fetchall()}
    log_info(f"Found {len(employee_codes)} active employees: {sorted(employee_codes)}")

    # Fetch cluster codes
    cursor.execute("SELECT code FROM public.month_end_clusters WHERE active = true")
    cluster_codes = {row[0] for row in cursor.fetchall()}
    log_info(f"Found {len(cluster_codes)} active clusters: {sorted(cluster_codes)}")

    cursor.close()

    return employee_codes, cluster_codes


def import_tasks(
    conn,
    tasks: List[Dict],
    month_end: datetime,
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Import tasks into database.

    Args:
        conn: Database connection
        tasks: List of validated task dictionaries
        month_end: Month-end date
        dry_run: If True, don't commit changes

    Returns:
        Tuple of (inserted_count, skipped_count)
    """
    cursor = conn.cursor()
    inserted = 0
    skipped = 0

    for task in tasks:
        # Calculate due date
        due_date = calculate_due_date(month_end, task['relative_due'])

        if due_date is None:
            log_warning(f"Skipping task (invalid due date): {task['name']}")
            skipped += 1
            continue

        # Check if task already exists
        cursor.execute(
            """
            SELECT id FROM public.month_end_tasks
            WHERE name = %s AND month_end = %s
            """,
            (task['name'], month_end)
        )

        if cursor.fetchone():
            log_warning(f"Skipping task (already exists): {task['name']}")
            skipped += 1
            continue

        # Insert task
        try:
            cursor.execute(
                """
                INSERT INTO public.month_end_tasks (
                    name, cluster_code, relative_due, due_date, month_end,
                    owner_code, reviewer_code, approver_code,
                    status, progress
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Not started', 0)
                """,
                (
                    task['name'],
                    task['cluster_code'],
                    task['relative_due'],
                    due_date,
                    month_end,
                    task['owner_code'],
                    task['reviewer_code'],
                    task['approver_code']
                )
            )
            inserted += 1
            log_success(f"Inserted: {task['name']} (Owner: {task['owner_code']}, Due: {due_date.strftime('%Y-%m-%d')})")

        except Exception as e:
            log_error(f"Failed to insert task '{task['name']}': {e}")
            skipped += 1

    if dry_run:
        conn.rollback()
        log_warning("DRY RUN: Changes rolled back")
    else:
        conn.commit()
        log_success("Changes committed to database")

    cursor.close()

    return inserted, skipped


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Import month-end closing tasks from CSV with deduplication'
    )
    parser.add_argument(
        '--csv',
        required=True,
        help='Path to CSV file'
    )
    parser.add_argument(
        '--month-end',
        required=True,
        help='Month-end date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate without committing changes'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    postgres_url = os.getenv('POSTGRES_URL')

    if not postgres_url:
        log_error("POSTGRES_URL environment variable not set")
        sys.exit(1)

    # Parse month-end date
    try:
        month_end = datetime.strptime(args.month_end, '%Y-%m-%d')
    except ValueError:
        log_error(f"Invalid month-end date format: {args.month_end} (expected YYYY-MM-DD)")
        sys.exit(1)

    log_info("="*80)
    log_info("Month-End Task Import - With Deduplication")
    log_info(f"CSV File: {args.csv}")
    log_info(f"Month-End: {month_end.strftime('%Y-%m-%d')}")
    log_info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE IMPORT'}")
    log_info("="*80)
    print()

    # Load CSV data
    log_info("Step 1: Loading CSV data...")
    tasks = load_csv_data(args.csv)
    print()

    # Deduplicate
    log_info("Step 2: Deduplicating tasks...")
    unique_tasks, duplicates = deduplicate_tasks(tasks)
    print()

    # Connect to database
    log_info("Step 3: Connecting to Supabase...")
    conn = get_database_connection(postgres_url)
    print()

    # Fetch valid codes
    log_info("Step 4: Fetching valid employee and cluster codes...")
    valid_employees, valid_clusters = fetch_valid_codes(conn)
    print()

    # Validate tasks
    log_info("Step 5: Validating tasks...")
    valid_tasks = []
    invalid_tasks = []

    for task in unique_tasks:
        is_valid, error = validate_task(task, valid_employees, valid_clusters)
        if is_valid:
            valid_tasks.append(task)
        else:
            invalid_tasks.append((task, error))
            log_warning(f"Invalid task: {task['name']} - {error}")

    log_success(f"{len(valid_tasks)} tasks are valid")
    if invalid_tasks:
        log_warning(f"{len(invalid_tasks)} tasks are invalid")
    print()

    # Import tasks
    if valid_tasks:
        log_info("Step 6: Importing tasks...")
        inserted, skipped = import_tasks(conn, valid_tasks, month_end, args.dry_run)
        print()

        # Summary
        log_info("="*80)
        log_info("Import Summary")
        log_info("="*80)
        log_info(f"Total tasks in CSV: {len(tasks)}")
        log_info(f"Duplicates found: {len(duplicates)}")
        log_info(f"Unique tasks: {len(unique_tasks)}")
        log_info(f"Valid tasks: {len(valid_tasks)}")
        log_info(f"Invalid tasks: {len(invalid_tasks)}")
        log_success(f"Tasks inserted: {inserted}")
        log_warning(f"Tasks skipped: {skipped}")
        log_info("="*80)
    else:
        log_warning("No valid tasks to import")

    conn.close()


if __name__ == '__main__':
    main()
