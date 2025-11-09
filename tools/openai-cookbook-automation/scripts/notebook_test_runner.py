#!/usr/bin/env python3
"""
Notebook Test Runner for OpenAI Cookbook
Supports two modes:
  - structure: Validates notebook structure, metadata, and checks for secrets (no execution)
  - smoke: Executes notebooks to verify they run without errors
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError


# Patterns that might indicate hardcoded secrets
SECRET_PATTERNS = [
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
    r'api_key\s*=\s*["\'][^"\']+["\']',  # api_key = "..."
    r'OPENAI_API_KEY\s*=\s*["\'][^"\']+["\']',  # OPENAI_API_KEY = "..."
    r'Bearer\s+[a-zA-Z0-9_-]{20,}',  # Bearer token
]


def find_notebooks(pattern: str, root: Path) -> List[Path]:
    """Find all notebooks matching the pattern."""
    full_pattern = str(root / pattern)
    return sorted([Path(p) for p in glob.glob(full_pattern, recursive=True)])


def check_cell_for_secrets(cell, cell_idx: int) -> List[str]:
    """Check a code cell for potential hardcoded secrets."""
    warnings = []

    if cell.cell_type != "code":
        return warnings

    source = cell.source or ""

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, source):
            warnings.append(
                f"Cell {cell_idx}: Potential hardcoded secret detected (pattern: {pattern[:30]}...)"
            )

    return warnings


def check_notebook_structure(nb_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate notebook structure without executing it.

    Checks:
    - Valid JSON format
    - Has kernelspec metadata
    - Has language_info metadata
    - No hardcoded secrets
    - Has at least one markdown cell (documentation)
    """
    errors = []

    try:
        nb = nbformat.read(nb_path, as_version=4)
    except Exception as e:
        errors.append(f"Failed to read notebook: {e}")
        return False, errors

    # Check metadata
    if "kernelspec" not in nb.metadata:
        errors.append("Missing 'kernelspec' in notebook metadata")

    if "language_info" not in nb.metadata:
        errors.append("Missing 'language_info' in notebook metadata")

    # Check for secrets
    for idx, cell in enumerate(nb.cells):
        secret_warnings = check_cell_for_secrets(cell, idx)
        errors.extend(secret_warnings)

    # Check for at least one markdown cell (documentation)
    has_markdown = any(cell.cell_type == "markdown" for cell in nb.cells)
    if not has_markdown:
        errors.append("No markdown cells found - notebook should have documentation")

    # Check for empty notebook
    if len(nb.cells) == 0:
        errors.append("Notebook is empty")

    return len(errors) == 0, errors


def execute_notebook(nb_path: Path, timeout: int = 180) -> Tuple[bool, List[str]]:
    """
    Execute the notebook and check for errors.

    Args:
        nb_path: Path to the notebook
        timeout: Execution timeout in seconds per cell

    Returns:
        (success, errors)
    """
    errors = []

    try:
        nb = nbformat.read(nb_path, as_version=4)
    except Exception as e:
        errors.append(f"Failed to read notebook: {e}")
        return False, errors

    kernel_name = nb.metadata.get("kernelspec", {}).get("name", "python3")

    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name=kernel_name,
        allow_errors=False,
    )

    try:
        client.execute()
    except CellExecutionError as e:
        errors.append(f"Cell execution error: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Execution error: {e}")
        return False, errors

    return True, []


def run_structure_tests(notebooks: List[Path]) -> int:
    """Run structure tests on notebooks."""
    failures = 0

    print(f"\n{'='*80}")
    print("STRUCTURE TESTS")
    print(f"{'='*80}\n")

    for nb_path in notebooks:
        print(f"Testing: {nb_path}")
        success, errors = check_notebook_structure(nb_path)

        if success:
            print(f"  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL")
            for error in errors:
                print(f"     - {error}")
            print()
            failures += 1

    return failures


def run_smoke_tests(notebooks: List[Path], timeout: int) -> int:
    """Run smoke tests (execute notebooks) on notebooks."""
    failures = 0

    print(f"\n{'='*80}")
    print("SMOKE TESTS (Execution)")
    print(f"{'='*80}\n")

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Some notebooks may fail.\n")

    for nb_path in notebooks:
        print(f"Executing: {nb_path}")
        success, errors = execute_notebook(nb_path, timeout=timeout)

        if success:
            print(f"  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL")
            for error in errors:
                print(f"     - {error}")
            print()
            failures += 1

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Test OpenAI Cookbook notebooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run structure tests on all notebooks
  python notebook_test_runner.py --mode structure

  # Run structure tests on specific pattern
  python notebook_test_runner.py --mode structure --pattern "examples/chat/**/*.ipynb"

  # Run smoke tests with API key
  OPENAI_API_KEY=sk-... python notebook_test_runner.py --mode smoke

  # Run smoke tests with custom timeout
  python notebook_test_runner.py --mode smoke --timeout 300
        """
    )

    parser.add_argument(
        "--mode",
        choices=["structure", "smoke"],
        default="structure",
        help="Test mode: structure (no execution) or smoke (execute notebooks)"
    )

    parser.add_argument(
        "--pattern",
        default="examples/**/*.ipynb",
        help="Glob pattern for notebooks to test (default: examples/**/*.ipynb)"
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory for notebook search (default: current directory)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Execution timeout per cell in seconds (default: 180)"
    )

    args = parser.parse_args()

    # Find notebooks
    notebooks = find_notebooks(args.pattern, args.root)

    if not notebooks:
        print(f"❌ No notebooks found matching pattern: {args.pattern}")
        print(f"   Root directory: {args.root}")
        return 1

    print(f"Found {len(notebooks)} notebook(s) matching pattern: {args.pattern}")

    # Run tests
    if args.mode == "structure":
        failures = run_structure_tests(notebooks)
    else:
        failures = run_smoke_tests(notebooks, args.timeout)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total: {len(notebooks)}")
    print(f"Passed: {len(notebooks) - failures}")
    print(f"Failed: {failures}")

    if failures > 0:
        print(f"\n❌ {failures} notebook(s) failed {args.mode} tests")
        return 1
    else:
        print(f"\n✅ All notebooks passed {args.mode} tests")
        return 0


if __name__ == "__main__":
    sys.exit(main())
