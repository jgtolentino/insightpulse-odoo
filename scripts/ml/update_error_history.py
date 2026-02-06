#!/usr/bin/env python3
"""
Update error history for ML model training.

Maintains a JSON database of historical CI errors and their fixes.

Usage:
    python update_error_history.py \
        --category dependency_missing \
        --fix-applied claude-code-auto-fix \
        --confidence 87 \
        --success true \
        --timestamp 2025-11-10T12:00:00Z
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def update_error_history(
    category: str,
    fix_applied: str,
    confidence: float,
    success: bool,
    timestamp: str = None,
    message: str = None,
):
    """Add error entry to history database"""

    history_file = Path("data/error_history.json")
    history_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing history
    if history_file.exists():
        with open(history_file) as f:
            history = json.load(f)
    else:
        history = []

    # Create new entry
    entry = {
        "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
        "category": category,
        "fix_applied": fix_applied,
        "confidence": confidence,
        "success": success,
        "auto_fixed": fix_applied.startswith("claude-code"),
        "message": message or f"{category} - {fix_applied}",
    }

    history.append(entry)

    # Save updated history
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Added entry to error history: {category} ({confidence}% confidence)")
    print(f"   Total entries: {len(history)}")
    print(
        f"   Auto-fix success rate: {sum(1 for e in history if e.get('auto_fixed') and e.get('success')) / max(sum(1 for e in history if e.get('auto_fixed')), 1):.1%}"
    )


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="Update error history database")
    parser.add_argument("--category", required=True, help="Error category")
    parser.add_argument("--fix-applied", required=True, help="Fix method applied")
    parser.add_argument(
        "--confidence", required=True, type=float, help="ML confidence (0-100)"
    )
    parser.add_argument(
        "--success",
        required=True,
        type=lambda x: x.lower() == "true",
        help="Whether fix was successful",
    )
    parser.add_argument("--timestamp", help="ISO 8601 timestamp (defaults to now)")
    parser.add_argument("--message", help="Optional error message")

    args = parser.parse_args()

    update_error_history(
        category=args.category,
        fix_applied=args.fix_applied,
        confidence=args.confidence,
        success=args.success,
        timestamp=args.timestamp,
        message=args.message,
    )


if __name__ == "__main__":
    main()
