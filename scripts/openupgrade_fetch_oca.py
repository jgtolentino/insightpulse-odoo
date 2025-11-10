#!/usr/bin/env python3
"""
OCA Module Migration Fetcher

Downloads OpenUpgrade migration scripts for OCA modules used in InsightPulse.

Usage:
    python3 scripts/openupgrade_fetch_oca.py --module account
    python3 scripts/openupgrade_fetch_oca.py --all  # Fetch all dependencies
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OPENUPGRADE_REPO = "https://github.com/OCA/OpenUpgrade.git"
OPENUPGRADE_BRANCH = "19.0"

CUSTOM_ADDONS_PATH = Path(__file__).parent.parent / "odoo" / "custom-addons"
OCA_MIGRATIONS_PATH = Path(__file__).parent.parent / "odoo" / "oca-migrations"


def get_module_dependencies(module_path: Path) -> list:
    """
    Extract dependencies from module manifest.
    """
    manifest_path = module_path / "__manifest__.py"

    if not manifest_path.exists():
        return []

    try:
        with open(manifest_path) as f:
            manifest = eval(f.read())
        return manifest.get("depends", [])
    except Exception as e:
        print(f"⚠️  Failed to parse manifest for {module_path.name}: {e}")
        return []


def fetch_oca_migration(module_name: str, output_dir: Path) -> bool:
    """
    Fetch OpenUpgrade migration scripts for an OCA module.

    Returns:
        True if migration scripts were found and downloaded
    """
    print(f"🔍 Checking for {module_name} migration scripts...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Clone OpenUpgrade repo (sparse checkout for specific module)
        try:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=tmpdir, check=True, capture_output=True)

            # Add remote
            subprocess.run(
                ["git", "remote", "add", "origin", OPENUPGRADE_REPO],
                cwd=tmpdir,
                check=True,
                capture_output=True,
            )

            # Enable sparse checkout
            subprocess.run(
                ["git", "config", "core.sparseCheckout", "true"],
                cwd=tmpdir,
                check=True,
                capture_output=True,
            )

            # Specify path to checkout
            sparse_file = tmpdir / ".git" / "info" / "sparse-checkout"
            sparse_file.parent.mkdir(parents=True, exist_ok=True)
            with open(sparse_file, "w") as f:
                f.write(f"openupgrade_scripts/scripts/{module_name}/\n")

            # Pull
            subprocess.run(
                ["git", "pull", "--depth=1", "origin", OPENUPGRADE_BRANCH],
                cwd=tmpdir,
                check=True,
                capture_output=True,
            )

            # Check if migration scripts exist
            module_scripts_path = (
                tmpdir / "openupgrade_scripts" / "scripts" / module_name
            )

            if module_scripts_path.exists() and list(module_scripts_path.iterdir()):
                # Copy to output directory
                module_output_path = output_dir / module_name
                module_output_path.mkdir(parents=True, exist_ok=True)

                shutil.copytree(
                    module_scripts_path, module_output_path, dirs_exist_ok=True
                )

                # Count scripts
                script_count = len(list(module_output_path.rglob("*.py")))
                print(
                    f"✅ Downloaded {script_count} migration scripts for {module_name}"
                )
                return True
            else:
                print(f"ℹ️  No migration scripts available for {module_name}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fetch {module_name}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Fetch OCA module migration scripts from OpenUpgrade"
    )
    parser.add_argument("--module", help="Specific OCA module to fetch")
    parser.add_argument("--all", action="store_true", help="Fetch all dependencies")
    parser.add_argument(
        "--force", action="store_true", help="Re-download even if already exists"
    )
    args = parser.parse_args()

    if not args.module and not args.all:
        parser.error("Specify --module MODULE or --all")

    # Create output directory
    OCA_MIGRATIONS_PATH.mkdir(parents=True, exist_ok=True)

    modules_to_fetch = set()

    if args.all:
        print("🔎 Scanning custom modules for OCA dependencies...")

        # Scan all custom modules
        for module_path in CUSTOM_ADDONS_PATH.iterdir():
            if module_path.is_dir() and not module_path.name.startswith((".", "__")):
                deps = get_module_dependencies(module_path)
                modules_to_fetch.update(deps)

        # Filter common OCA modules
        oca_modules = {
            "account",
            "sale",
            "purchase",
            "stock",
            "mrp",
            "website",
            "crm",
            "hr",
            "project",
            "mail",
            "product",
            "base",
            "account_accountant",
            "sale_management",
            "purchase_stock",
        }

        modules_to_fetch = modules_to_fetch & oca_modules

        print(f"Found {len(modules_to_fetch)} OCA dependencies:")
        for mod in sorted(modules_to_fetch):
            print(f"  - {mod}")

    else:
        modules_to_fetch = {args.module}

    # Fetch each module
    print("\n" + "=" * 60)
    print("DOWNLOADING MIGRATION SCRIPTS")
    print("=" * 60 + "\n")

    successful = 0
    failed = 0
    skipped = 0

    for module_name in sorted(modules_to_fetch):
        output_path = OCA_MIGRATIONS_PATH / module_name

        if output_path.exists() and not args.force:
            print(
                f"⏭️  Skipping {module_name} (already exists, use --force to re-download)"
            )
            skipped += 1
            continue

        if fetch_oca_migration(module_name, OCA_MIGRATIONS_PATH):
            successful += 1
        else:
            failed += 1

        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total modules: {len(modules_to_fetch)}")
    print(f"✅ Downloaded: {successful}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed/Not found: {failed}")
    print(f"\nMigration scripts saved to: {OCA_MIGRATIONS_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
