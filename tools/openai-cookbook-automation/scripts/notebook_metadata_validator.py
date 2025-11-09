#!/usr/bin/env python3
"""
Notebook Metadata Validator for OpenAI Cookbook

Validates that notebooks have proper metadata in the 'cookbook' namespace.

Required metadata fields:
  - title: Display title for the notebook
  - difficulty: One of [beginner, intermediate, advanced]
  - tags: List of tags (e.g., ["embeddings", "gpt-4", "rag"])
  - estimated_time: String like "15 minutes" or "1 hour"
  - category: One of the defined categories
  - openai_models: List of OpenAI models used (e.g., ["gpt-4", "text-embedding-ada-002"])

Optional metadata:
  - prerequisites: List of prerequisite knowledge/tools
  - author: Author name or organization
  - last_updated: ISO date string (YYYY-MM-DD)
"""

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import nbformat


# Allowed values for certain fields
ALLOWED_DIFFICULTY = {"beginner", "intermediate", "advanced"}

ALLOWED_CATEGORIES = {
    "chat",
    "embeddings",
    "fine-tuning",
    "vision",
    "audio",
    "assistants",
    "agents",
    "rag",
    "function-calling",
    "batch",
    "reasoning",
    "other",
}

# Known OpenAI model patterns
KNOWN_MODEL_PREFIXES = [
    "gpt-4",
    "gpt-3.5",
    "text-embedding",
    "dall-e",
    "whisper",
    "tts",
    "o1",
    "o3",
]


def find_notebooks(pattern: str, root: Path) -> List[Path]:
    """Find all notebooks matching the pattern."""
    full_pattern = str(root / pattern)
    return sorted([Path(p) for p in glob.glob(full_pattern, recursive=True)])


def validate_notebook_metadata(nb_path: Path, strict: bool = False) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a notebook's metadata.

    Args:
        nb_path: Path to the notebook
        strict: If True, treat warnings as errors

    Returns:
        (valid, errors, warnings)
    """
    errors = []
    warnings = []

    try:
        nb = nbformat.read(nb_path, as_version=4)
    except Exception as e:
        errors.append(f"Failed to read notebook: {e}")
        return False, errors, warnings

    # Get cookbook metadata namespace
    metadata = nb.metadata.get("cookbook", {})

    if not metadata:
        errors.append("Missing 'cookbook' metadata namespace")
        return False, errors, warnings

    # Required fields
    required_fields = ["title", "difficulty", "tags", "estimated_time", "category"]

    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: cookbook.{field}")

    # Validate difficulty
    if "difficulty" in metadata:
        difficulty = metadata["difficulty"]
        if difficulty not in ALLOWED_DIFFICULTY:
            errors.append(
                f"Invalid difficulty '{difficulty}'. "
                f"Must be one of: {sorted(ALLOWED_DIFFICULTY)}"
            )

    # Validate category
    if "category" in metadata:
        category = metadata["category"]
        if category not in ALLOWED_CATEGORIES:
            errors.append(
                f"Invalid category '{category}'. "
                f"Must be one of: {sorted(ALLOWED_CATEGORIES)}"
            )

    # Validate tags (must be list)
    if "tags" in metadata:
        tags = metadata["tags"]
        if not isinstance(tags, list):
            errors.append("cookbook.tags must be a list of strings")
        elif len(tags) == 0:
            warnings.append("cookbook.tags is empty - consider adding relevant tags")
        elif not all(isinstance(tag, str) for tag in tags):
            errors.append("All cookbook.tags entries must be strings")

    # Validate estimated_time
    if "estimated_time" in metadata:
        est_time = metadata["estimated_time"]
        if not isinstance(est_time, str):
            errors.append("cookbook.estimated_time must be a string (e.g., '15 minutes')")
        elif len(est_time) == 0:
            warnings.append("cookbook.estimated_time is empty")

    # Validate openai_models (recommended but not required)
    if "openai_models" in metadata:
        models = metadata["openai_models"]
        if not isinstance(models, list):
            errors.append("cookbook.openai_models must be a list of strings")
        elif not all(isinstance(model, str) for model in models):
            errors.append("All cookbook.openai_models entries must be strings")
        else:
            # Check if models look valid
            for model in models:
                if not any(model.startswith(prefix) for prefix in KNOWN_MODEL_PREFIXES):
                    warnings.append(
                        f"Unrecognized model '{model}' - verify this is a valid OpenAI model"
                    )
    else:
        warnings.append("cookbook.openai_models not specified - consider adding models used")

    # Validate prerequisites if present
    if "prerequisites" in metadata:
        prereqs = metadata["prerequisites"]
        if not isinstance(prereqs, list):
            errors.append("cookbook.prerequisites must be a list of strings")

    # Check for title
    if "title" in metadata:
        title = metadata["title"]
        if not isinstance(title, str):
            errors.append("cookbook.title must be a string")
        elif len(title) == 0:
            errors.append("cookbook.title cannot be empty")
        elif len(title) > 100:
            warnings.append(f"cookbook.title is very long ({len(title)} chars) - consider shortening")

    # Validate last_updated if present
    if "last_updated" in metadata:
        last_updated = metadata["last_updated"]
        if not isinstance(last_updated, str):
            errors.append("cookbook.last_updated must be a string (ISO date: YYYY-MM-DD)")
        else:
            # Simple ISO date validation
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', last_updated):
                errors.append(
                    f"cookbook.last_updated '{last_updated}' doesn't match ISO format (YYYY-MM-DD)"
                )

    # If strict mode, convert warnings to errors
    if strict:
        errors.extend(warnings)
        warnings = []

    valid = len(errors) == 0
    return valid, errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Validate OpenAI Cookbook notebook metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all notebooks
  python notebook_metadata_validator.py

  # Validate specific pattern
  python notebook_metadata_validator.py --pattern "examples/chat/**/*.ipynb"

  # Strict mode (warnings treated as errors)
  python notebook_metadata_validator.py --strict

  # Output JSON report
  python notebook_metadata_validator.py --json-output metadata-report.json
        """
    )

    parser.add_argument(
        "--pattern",
        default="examples/**/*.ipynb",
        help="Glob pattern for notebooks to validate (default: examples/**/*.ipynb)"
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory for notebook search (default: current directory)"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    parser.add_argument(
        "--json-output",
        type=Path,
        help="Write validation report to JSON file"
    )

    args = parser.parse_args()

    # Find notebooks
    notebooks = find_notebooks(args.pattern, args.root)

    if not notebooks:
        print(f"❌ No notebooks found matching pattern: {args.pattern}")
        print(f"   Root directory: {args.root}")
        return 1

    print(f"Found {len(notebooks)} notebook(s) matching pattern: {args.pattern}")
    print(f"{'='*80}\n")

    # Validate each notebook
    results = {}
    total_errors = 0
    total_warnings = 0

    for nb_path in notebooks:
        rel_path = nb_path.relative_to(args.root)
        print(f"Validating: {rel_path}")

        valid, errors, warnings = validate_notebook_metadata(nb_path, strict=args.strict)

        results[str(rel_path)] = {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        }

        if errors:
            print("  ❌ ERRORS:")
            for error in errors:
                print(f"     - {error}")
            total_errors += len(errors)

        if warnings:
            print("  ⚠️  WARNINGS:")
            for warning in warnings:
                print(f"     - {warning}")
            total_warnings += len(warnings)

        if valid and not warnings:
            print("  ✅ VALID")

        print()

    # Summary
    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total notebooks: {len(notebooks)}")
    print(f"Valid: {sum(1 for r in results.values() if r['valid'])}")
    print(f"Invalid: {sum(1 for r in results.values() if not r['valid'])}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")

    # Write JSON output if requested
    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 JSON report written to: {args.json_output}")

    # Determine exit code
    invalid_count = sum(1 for r in results.values() if not r['valid'])

    if invalid_count > 0:
        print(f"\n❌ {invalid_count} notebook(s) have invalid metadata")
        return 1
    elif total_warnings > 0:
        print(f"\n⚠️  All notebooks valid, but {total_warnings} warning(s) found")
        return 0
    else:
        print("\n✅ All notebooks have valid metadata")
        return 0


if __name__ == "__main__":
    sys.exit(main())
