#!/usr/bin/env python3
"""
Auto-bump __manifest__.py patch version when spec changes detected.
Follows semantic versioning: MAJOR.MINOR.PATCH
"""
import re
import sys
from pathlib import Path
from typing import Optional


def find_manifest_files() -> list[Path]:
    """Find all __manifest__.py files in addons/."""
    addons_dir = Path("addons")
    if not addons_dir.exists():
        return []
    return list(addons_dir.rglob("*/__manifest__.py"))


def extract_version(manifest_content: str) -> Optional[str]:
    """Extract version string from __manifest__.py."""
    version_pattern = r'"version"\s*:\s*"([^"]+)"'
    match = re.search(version_pattern, manifest_content)
    return match.group(1) if match else None


def bump_patch_version(version: str) -> str:
    """Bump patch version: 19.0.1.0.0 → 19.0.1.0.1"""
    parts = version.split(".")
    if len(parts) >= 3:
        # Bump last component (patch version)
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    return version


def update_manifest_version(manifest_path: Path) -> bool:
    """Update version in __manifest__.py file."""
    content = manifest_path.read_text()
    current_version = extract_version(content)

    if not current_version:
        print(f"⚠️  No version found in {manifest_path}")
        return False

    new_version = bump_patch_version(current_version)

    if current_version == new_version:
        print(f"✓ {manifest_path.parent.name}: {current_version} (no change)")
        return False

    # Replace version
    updated_content = re.sub(
        r'"version"\s*:\s*"[^"]+"',
        f'"version": "{new_version}"',
        content
    )

    manifest_path.write_text(updated_content)
    print(f"✅ {manifest_path.parent.name}: {current_version} → {new_version}")
    return True


def main():
    """Main execution: find and bump all manifest versions."""
    print("📦 Bumping __manifest__.py versions...\n")

    manifest_files = find_manifest_files()

    if not manifest_files:
        print("⚠️  No __manifest__.py files found in addons/")
        sys.exit(0)

    updated_count = 0
    for manifest_path in manifest_files:
        if update_manifest_version(manifest_path):
            updated_count += 1

    print(f"\n✅ Updated {updated_count}/{len(manifest_files)} manifests")

    if updated_count > 0:
        print("\n💡 Remember to commit these version bumps:")
        print("   git add addons/*/__manifest__.py")
        print('   git commit -m "chore: bump module versions (spec changes)"')


if __name__ == "__main__":
    main()
