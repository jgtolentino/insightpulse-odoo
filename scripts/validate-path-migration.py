#!/usr/bin/env python3
"""
Validate that path migration from custom/ to odoo/modules/ is complete.

This script checks for any remaining 'custom/' references in critical files
to ensure the path migration is complete and consistent.
"""

import os
import sys
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def check_path_references() -> List[Dict[str, any]]:
    """Check for any remaining 'custom/' references in files."""

    issues = []

    # Patterns of files to check
    check_patterns = [
        '.github/workflows/*.yml',
        'scripts/**/*.py',
        'scripts/**/*.sh',
        'Makefile',
        'docs/**/*.md',
        '*.yml',
        '*.yaml',
        '.flake8',
        '.pre-commit-config.yaml',
    ]

    # Patterns to exclude from checks
    exclude_patterns = [
        'node_modules/',
        '.git/',
        '__pycache__/',
        '.venv/',
        'venv/',
        'bundle/',
        'claudedocs/',
        '.superclaude/',
        'docs/',  # Exclude documentation
        'scripts/validate-path-migration.py',  # Exclude this script itself
        '.github/workflows/path-migration-guard.yml',  # Exclude the guard workflow
    ]

    # Words that indicate this is documentation about the migration, not actual usage
    migration_doc_keywords = [
        'migration',
        'migrated',
        'old path',
        'previous',
        'legacy',
        'deprecated',
        'before:',
        'after:',
        'from custom/',
        'was custom/',
    ]

    print(f"{BLUE}🔍 Scanning for 'custom/' path references...{NC}\n")

    for pattern in check_patterns:
        matching_files = glob.glob(pattern, recursive=True)

        for file_path in matching_files:
            # Skip excluded paths
            if any(exc in file_path for exc in exclude_patterns):
                continue

            # Skip if file doesn't exist
            if not os.path.isfile(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    # Look for custom/ references
                    for i, line in enumerate(lines, 1):
                        if 'custom/' in line.lower():
                            line_lower = line.lower()

                            # Skip if it's a comment about the migration
                            if any(keyword in line_lower for keyword in migration_doc_keywords):
                                continue

                            # Skip comments in shell scripts and Python
                            stripped = line.strip()
                            if stripped.startswith('#') or stripped.startswith('//'):
                                # Check if it's documenting the migration
                                if any(keyword in line_lower for keyword in migration_doc_keywords):
                                    continue

                            # This looks like an actual usage, not documentation
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'content': line.strip()
                            })

            except (UnicodeDecodeError, PermissionError) as e:
                print(f"{YELLOW}⚠️  Skipping {file_path}: {e}{NC}")
                continue

    return issues


def check_directory_structure() -> Tuple[bool, List[str]]:
    """Verify the new directory structure exists."""

    required_dirs = [
        'odoo',
        'odoo/modules',
        'odoo/addons',
        'odoo/custom-addons',
    ]

    missing = []
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing.append(dir_path)

    return len(missing) == 0, missing


def main():
    """Main validation function."""

    print(f"{BLUE}╔══════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║  Path Migration Validation                              ║{NC}")
    print(f"{BLUE}║  Checking for 'custom/' → 'odoo/modules/' migration     ║{NC}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════╝{NC}\n")

    # Check 1: Verify directory structure
    print(f"{BLUE}[1/2] Checking directory structure...{NC}")
    structure_ok, missing_dirs = check_directory_structure()

    if structure_ok:
        print(f"{GREEN}✅ Directory structure is correct{NC}")
        print(f"   - odoo/modules/ exists")
        print(f"   - odoo/addons/ exists")
        print(f"   - odoo/custom-addons/ exists\n")
    else:
        print(f"{RED}❌ Missing required directories:{NC}")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        print()

    # Check 2: Scan for path references
    print(f"{BLUE}[2/2] Scanning for 'custom/' path references...{NC}")
    issues = check_path_references()

    if not issues:
        print(f"{GREEN}✅ No problematic 'custom/' references found{NC}\n")
    else:
        print(f"{RED}❌ Found {len(issues)} file(s) with 'custom/' references:{NC}\n")

        # Group by file for better readability
        issues_by_file = {}
        for issue in issues:
            file_path = issue['file']
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        for file_path, file_issues in issues_by_file.items():
            print(f"{YELLOW}  📄 {file_path}{NC}")
            for issue in file_issues[:3]:  # Show first 3 per file
                print(f"     Line {issue['line']}: {issue['content'][:80]}")
            if len(file_issues) > 3:
                print(f"     ... and {len(file_issues) - 3} more")
            print()

    # Final verdict
    print(f"{BLUE}═══════════════════════════════════════════════════════════{NC}")

    if structure_ok and not issues:
        print(f"{GREEN}✅ Path migration validation PASSED{NC}")
        print(f"{GREEN}   All paths have been successfully migrated!{NC}\n")
        return 0
    else:
        print(f"{RED}❌ Path migration validation FAILED{NC}")
        if not structure_ok:
            print(f"{RED}   - Directory structure incomplete{NC}")
        if issues:
            print(f"{RED}   - Found {len(issues)} 'custom/' references to fix{NC}")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
