# Auto-Patch Scripts

This directory contains autopatch scripts referenced by Fixer skills (FX-*).

## Structure

Each autopatch script must:

1. Define an `apply(repo_dir: str) -> bool` function
2. Be idempotent (safe to run multiple times)
3. Return `True` if applied successfully, `False` otherwise
4. Handle errors gracefully
5. Log what it's doing

## Template

```python
#!/usr/bin/env python3
"""
Auto-patch for: [Brief description]
Skill ID: FX-ABCD1234
Generated: 2025-11-07
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def apply(repo_dir: str) -> bool:
    """
    Apply the patch to fix [specific error pattern]

    Args:
        repo_dir: Root directory of the repository

    Returns:
        True if patch applied successfully, False otherwise
    """
    try:
        # 1. Check if patch already applied
        marker_file = Path(repo_dir) / ".patches" / "fx-abcd1234.applied"
        if marker_file.exists():
            logger.info("Patch already applied, skipping")
            return True

        # 2. Apply your fix here
        # Example: Update a config file, fix a manifest, etc.
        target_file = Path(repo_dir) / "path" / "to" / "file.py"

        if not target_file.exists():
            logger.warning(f"Target file not found: {target_file}")
            return False

        # Read, modify, write (example)
        content = target_file.read_text()
        if "old_pattern" not in content:
            logger.info("Pattern not found, nothing to patch")
            return True

        content = content.replace("old_pattern", "new_pattern")
        target_file.write_text(content)

        # 3. Mark as applied
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(f"Applied at {datetime.utcnow().isoformat()}Z")

        logger.info("Patch applied successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to apply patch: {e}")
        return False


if __name__ == "__main__":
    # Test locally
    import sys
    logging.basicConfig(level=logging.INFO)
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    success = apply(repo_dir)
    sys.exit(0 if success else 1)
```

## Testing

Each autopatch should have a corresponding test:

```python
# tests/test_autopatches.py
import pytest
from autopatches.fx_abcd1234 import apply

def test_fx_abcd1234_apply(tmp_path):
    # Setup test environment
    test_file = tmp_path / "path" / "to" / "file.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("old_pattern")

    # Apply patch
    assert apply(str(tmp_path)) is True

    # Verify fix
    assert "new_pattern" in test_file.read_text()

    # Idempotency: second run should succeed
    assert apply(str(tmp_path)) is True
```

## Best Practices

1. **Safety First**: Never modify files outside the repo directory
2. **Validation**: Check file exists before modifying
3. **Backup**: Consider creating backups before destructive changes
4. **Logging**: Log all actions for auditability
5. **Markers**: Use marker files to track what's been applied
6. **Rollback**: Consider providing an `undo()` function
7. **Testing**: Always test in sandbox before production

## Integration with Skillsmith

When Skillsmith generates a Fixer skill:

1. It creates `skills/proposed/FX-*.yaml` with `script: autopatches/fx-*.py`
2. You implement the script following the template
3. You test it: `pytest tests/test_autopatches.py`
4. You approve the skill by moving it to `skills/`
5. CI runs the autopatch when the error pattern is detected

## Dry Run Mode

Skills start with `dry_run: true`. In this mode:
- The patch logic is validated
- No actual changes are made
- Logs show what would be changed

After validation, set `dry_run: false` to enable.

## Examples

See `examples/` directory for reference implementations:
- `examples/fix_manifest_typo.py` - Fix common manifest errors
- `examples/update_xpath.py` - Update invalid XPath expressions
- `examples/add_missing_import.py` - Add missing imports
