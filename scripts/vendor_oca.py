#!/usr/bin/env python3
"""
OCA Module Vendoring Script

This script helps vendor (copy) OCA modules into your project and
maintains an index of available OCA modules.

Usage:
    python vendor_oca.py --update-index
    python vendor_oca.py --module base_rest --target ./addons/
    python vendor_oca.py --search "rest api"
    python vendor_oca.py --list-repo server-tools
"""

import argparse
import json
import pathlib
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional


class OCAVendor:
    """OCA module vendoring and index management"""

    OCA_BASE_URL = "https://github.com/OCA"
    ODOO_VERSION = "19.0"  # Default version

    # Core OCA repositories
    REPOSITORIES = [
        "server-tools",
        "reporting-engine",
        "sale-workflow",
        "purchase-workflow",
        "stock-logistics-warehouse",
        "account-financial-reporting",
        "account-payment",
        "commission",
        "web",
        "rest-framework",
        "connector",
        "queue",
        "project",
        "crm",
        "data-protection",
        "hr",
        "manufacture",
        "product-attribute",
    ]

    def __init__(self, version: str = None):
        self.version = version or self.ODOO_VERSION
        self.index_file = pathlib.Path("datasets/oca_index.json")
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load OCA module index"""
        if self.index_file.exists():
            with self.index_file.open("r") as f:
                return json.load(f)
        return {
            "metadata": {
                "version": "1.0",
                "updated": datetime.utcnow().isoformat(),
                "odoo_version": self.version,
            },
            "repositories": [],
        }

    def _save_index(self):
        """Save OCA module index"""
        self.index["metadata"]["updated"] = datetime.utcnow().isoformat()
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with self.index_file.open("w") as f:
            json.dump(self.index, f, indent=2)
        print(f"Index saved to: {self.index_file}")

    def update_index(self):
        """Update the OCA module index"""
        print(f"Updating OCA index for Odoo {self.version}...")

        updated_repos = []

        for repo_name in self.REPOSITORIES:
            print(f"Fetching modules from {repo_name}...")
            repo_info = self._fetch_repository_info(repo_name)
            if repo_info:
                updated_repos.append(repo_info)

        self.index["repositories"] = updated_repos
        self._save_index()

        total_modules = sum(len(repo.get("modules", [])) for repo in updated_repos)
        print(
            f"Index updated: {len(updated_repos)} repositories, {total_modules} modules"
        )

    def _fetch_repository_info(self, repo_name: str) -> Optional[Dict]:
        """Fetch repository information from GitHub"""
        url = f"{self.OCA_BASE_URL}/{repo_name}"

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = pathlib.Path(tmpdir)

            try:
                # Clone repository (shallow, specific branch)
                print(f"  Cloning {repo_name} (branch {self.version})...")
                result = subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth",
                        "1",
                        "--branch",
                        self.version,
                        "--single-branch",
                        url,
                        str(tmppath / repo_name),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    print(
                        f"  Warning: Could not clone {repo_name} (branch {self.version})"
                    )
                    print(f"  {result.stderr}")
                    return None

                # Scan for modules
                repo_path = tmppath / repo_name
                modules = self._scan_repository_modules(repo_path)

                return {
                    "name": repo_name,
                    "url": url,
                    "branch": self.version,
                    "modules": modules,
                }

            except subprocess.TimeoutExpired:
                print(f"  Timeout cloning {repo_name}")
                return None
            except Exception as e:
                print(f"  Error processing {repo_name}: {e}")
                return None

    def _scan_repository_modules(self, repo_path: pathlib.Path) -> List[Dict]:
        """Scan repository for Odoo modules"""
        modules = []

        for manifest_path in repo_path.glob("*/__manifest__.py"):
            try:
                # Parse manifest
                import ast

                content = manifest_path.read_text(encoding="utf-8")
                manifest = ast.literal_eval(content)

                module_name = manifest_path.parent.name

                module_info = {
                    "name": module_name,
                    "display_name": manifest.get("name", module_name),
                    "summary": manifest.get("summary", ""),
                    "version": manifest.get("version", ""),
                    "author": manifest.get("author", ""),
                    "license": manifest.get("license", ""),
                    "depends": manifest.get("depends", []),
                    "installable": manifest.get("installable", True),
                }

                modules.append(module_info)

            except Exception as e:
                print(f"    Error parsing {manifest_path}: {e}")

        print(f"  Found {len(modules)} modules")
        return modules

    def search_modules(self, query: str) -> List[Dict]:
        """Search for modules by name or summary"""
        results = []
        query_lower = query.lower()

        for repo in self.index.get("repositories", []):
            for module in repo.get("modules", []):
                if (
                    query_lower in module.get("name", "").lower()
                    or query_lower in module.get("summary", "").lower()
                    or query_lower in module.get("display_name", "").lower()
                ):

                    results.append(
                        {
                            "repository": repo["name"],
                            "module": module["name"],
                            "display_name": module.get("display_name", ""),
                            "summary": module.get("summary", ""),
                            "installable": module.get("installable", True),
                        }
                    )

        return results

    def list_repository_modules(self, repo_name: str) -> List[Dict]:
        """List all modules in a repository"""
        for repo in self.index.get("repositories", []):
            if repo["name"] == repo_name:
                return repo.get("modules", [])
        return []

    def vendor_module(self, module_name: str, target_path: str, repo_name: str = None):
        """Vendor (copy) an OCA module to target path"""
        # Find module in index
        module_info = None
        source_repo = None

        for repo in self.index.get("repositories", []):
            if repo_name and repo["name"] != repo_name:
                continue

            for module in repo.get("modules", []):
                if module["name"] == module_name:
                    module_info = module
                    source_repo = repo
                    break

            if module_info:
                break

        if not module_info:
            print(f"Module '{module_name}' not found in index")
            if not repo_name:
                print("Try specifying a repository with --repo")
            return False

        print(f"Vendoring {module_name} from {source_repo['name']}...")

        # Clone repository
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = pathlib.Path(tmpdir)
            repo_url = source_repo["url"]

            try:
                print(f"  Cloning {source_repo['name']}...")
                result = subprocess.run(
                    [
                        "git",
                        "clone",
                        "--depth",
                        "1",
                        "--branch",
                        self.version,
                        "--single-branch",
                        repo_url,
                        str(tmppath / source_repo["name"]),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    print(f"  Error cloning repository: {result.stderr}")
                    return False

                # Copy module
                source_module_path = tmppath / source_repo["name"] / module_name
                target_module_path = pathlib.Path(target_path) / module_name

                if not source_module_path.exists():
                    print(f"  Module not found in repository: {source_module_path}")
                    return False

                print(f"  Copying module to {target_module_path}...")

                if target_module_path.exists():
                    print(f"  Warning: {target_module_path} already exists")
                    response = input("  Overwrite? [y/N]: ")
                    if response.lower() != "y":
                        print("  Cancelled")
                        return False
                    shutil.rmtree(target_module_path)

                shutil.copytree(source_module_path, target_module_path)

                # Create .oca_info file with metadata
                oca_info = {
                    "source_repository": source_repo["name"],
                    "source_url": repo_url,
                    "module_name": module_name,
                    "version": module_info.get("version", ""),
                    "vendored_at": datetime.utcnow().isoformat(),
                    "odoo_version": self.version,
                }

                oca_info_path = target_module_path / ".oca_info"
                with oca_info_path.open("w") as f:
                    json.dump(oca_info, f, indent=2)

                print(f"  ✓ Successfully vendored {module_name}")
                print(f"  Dependencies: {', '.join(module_info.get('depends', []))}")

                return True

            except subprocess.TimeoutExpired:
                print(f"  Timeout cloning repository")
                return False
            except Exception as e:
                print(f"  Error: {e}")
                return False

    def check_updates(self, addon_path: str):
        """Check for updates to vendored modules"""
        addon_path = pathlib.Path(addon_path)

        print(f"Checking for updates in: {addon_path}")

        updates_available = []

        for module_path in addon_path.iterdir():
            if not module_path.is_dir():
                continue

            oca_info_file = module_path / ".oca_info"
            if not oca_info_file.exists():
                continue

            try:
                with oca_info_file.open("r") as f:
                    oca_info = json.load(f)

                module_name = oca_info["module_name"]
                source_repo = oca_info["source_repository"]
                vendored_version = oca_info.get("version", "")

                # Find current version in index
                for repo in self.index.get("repositories", []):
                    if repo["name"] == source_repo:
                        for module in repo.get("modules", []):
                            if module["name"] == module_name:
                                current_version = module.get("version", "")
                                if current_version != vendored_version:
                                    updates_available.append(
                                        {
                                            "module": module_name,
                                            "vendored_version": vendored_version,
                                            "current_version": current_version,
                                            "repository": source_repo,
                                        }
                                    )

            except Exception as e:
                print(f"  Error checking {module_path}: {e}")

        if updates_available:
            print(f"\nUpdates available for {len(updates_available)} modules:")
            for update in updates_available:
                print(
                    f"  - {update['module']}: {update['vendored_version']} → {update['current_version']}"
                )
        else:
            print("\nAll vendored modules are up to date")

        return updates_available


def main():
    parser = argparse.ArgumentParser(description="OCA module vendoring tool")
    parser.add_argument("--version", type=str, help="Odoo version (default: 19.0)")
    parser.add_argument(
        "--update-index", action="store_true", help="Update OCA module index"
    )
    parser.add_argument("--search", type=str, help="Search for modules")
    parser.add_argument("--list-repo", type=str, help="List modules in repository")
    parser.add_argument("--module", type=str, help="Module to vendor")
    parser.add_argument("--repo", type=str, help="Source repository name")
    parser.add_argument("--target", type=str, help="Target directory for vendoring")
    parser.add_argument(
        "--check-updates", type=str, help="Check for updates in addon path"
    )

    args = parser.parse_args()

    vendor = OCAVendor(version=args.version)

    if args.update_index:
        vendor.update_index()

    elif args.search:
        results = vendor.search_modules(args.search)
        if results:
            print(f"\nFound {len(results)} modules matching '{args.search}':")
            for result in results:
                installable = "✓" if result["installable"] else "✗"
                print(f"  [{installable}] {result['repository']}/{result['module']}")
                print(f"      {result['display_name']}")
                if result["summary"]:
                    print(f"      {result['summary']}")
                print()
        else:
            print(f"No modules found matching '{args.search}'")

    elif args.list_repo:
        modules = vendor.list_repository_modules(args.list_repo)
        if modules:
            print(f"\nModules in {args.list_repo}:")
            for module in modules:
                installable = "✓" if module.get("installable", True) else "✗"
                print(f"  [{installable}] {module['name']}")
                print(f"      {module.get('display_name', '')}")
                if module.get("summary"):
                    print(f"      {module['summary']}")
                print()
        else:
            print(f"Repository '{args.list_repo}' not found in index")

    elif args.module and args.target:
        vendor.vendor_module(args.module, args.target, args.repo)

    elif args.check_updates:
        vendor.check_updates(args.check_updates)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
