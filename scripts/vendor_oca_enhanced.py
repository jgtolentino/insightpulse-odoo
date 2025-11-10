#!/usr/bin/env python3
"""
Enhanced OCA Module Vendoring Script for InsightPulse Odoo
Extends the existing vendor_oca.py with multi-repo support
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

# OCA repositories for Odoo 19
OCA_REPOS = {
    "account-financial-tools": {
        "url": "https://github.com/OCA/account-financial-tools.git",
        "branch": "19.0",
        "path": "addons/oca/account-financial-tools",
        "description": "Financial Reports, Analysis, and Tools",
    },
    "server-tools": {
        "url": "https://github.com/OCA/server-tools.git",
        "branch": "19.0",
        "path": "addons/oca/server-tools",
        "description": "Server Environment, Auto-backup, Date Ranges",
    },
    "web": {
        "url": "https://github.com/OCA/web.git",
        "branch": "19.0",
        "path": "addons/oca/web",
        "description": "Responsive UI, Advanced Search, Notifications",
    },
    "reporting-engine": {
        "url": "https://github.com/OCA/reporting-engine.git",
        "branch": "19.0",
        "path": "addons/oca/reporting-engine",
        "description": "Excel Reports, PDF Enhancements, Templates",
    },
    "account-invoicing": {
        "url": "https://github.com/OCA/account-invoicing.git",
        "branch": "19.0",
        "path": "addons/oca/account-invoicing",
        "description": "Invoice Automation and Management",
    },
    "hr": {
        "url": "https://github.com/OCA/hr.git",
        "branch": "19.0",
        "path": "addons/oca/hr",
        "description": "HR Management, Expenses, Timesheets",
    },
    "manufacture": {
        "url": "https://github.com/OCA/manufacture.git",
        "branch": "19.0",
        "path": "addons/oca/manufacture",
        "description": "Manufacturing Operations",
    },
}


def setup_all_repos(update: bool = False) -> None:
    """Clone or update all OCA repositories"""
    print("🚀 Setting up OCA repositories for Odoo 19...")
    print()

    for repo_name, repo_info in OCA_REPOS.items():
        repo_path = Path(repo_info["path"])

        if repo_path.exists() and (repo_path / ".git").exists():
            if update:
                print(f"📦 Updating {repo_name}...")
                try:
                    subprocess.run(
                        ["git", "pull"], cwd=repo_path, check=True, capture_output=True
                    )
                    print(f"   ✅ {repo_name} updated")
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  Failed to update {repo_name}: {e}")
            else:
                print(f"   ℹ️  {repo_name} already exists (use --update to refresh)")
        else:
            print(f"📦 Cloning {repo_name}...")
            print(f"   📝 {repo_info['description']}")

            # Create parent directory
            repo_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "-b",
                        repo_info["branch"],
                        "--depth",
                        "1",
                        repo_info["url"],
                        str(repo_path),
                    ],
                    check=True,
                    capture_output=True,
                )
                print(f"   ✅ {repo_name} cloned successfully")
            except subprocess.CalledProcessError as e:
                # Try fallback to 18.0 if 19.0 doesn't exist
                try:
                    print(f"   ⚠️  Branch 19.0 not found, trying 18.0...")
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            "-b",
                            "18.0",
                            "--depth",
                            "1",
                            repo_info["url"],
                            str(repo_path),
                        ],
                        check=True,
                        capture_output=True,
                    )
                    print(f"   ✅ {repo_name} cloned (18.0 branch)")
                except subprocess.CalledProcessError:
                    print(f"   ❌ Failed to clone {repo_name}")

        print()


def list_modules(repo_name: Optional[str] = None) -> None:
    """List all modules in OCA repositories"""
    if repo_name and repo_name in OCA_REPOS:
        repos = {repo_name: OCA_REPOS[repo_name]}
    else:
        repos = OCA_REPOS

    print("📚 Available OCA Modules:")
    print()

    total_modules = 0

    for repo_name, repo_info in repos.items():
        repo_path = Path(repo_info["path"])

        if not repo_path.exists():
            print(f"⚠️  {repo_name}: Not cloned yet (run with --setup)")
            continue

        print(f"🔷 {repo_name}")
        print(f"   {repo_info['description']}")

        # Find all modules (directories with __manifest__.py)
        modules = []
        for item in repo_path.iterdir():
            if item.is_dir() and (item / "__manifest__.py").exists():
                modules.append(item.name)

        if modules:
            modules.sort()
            for module in modules:
                print(f"   - {module}")
            print(f"   Total: {len(modules)} modules")
            total_modules += len(modules)
        else:
            print(f"   No modules found")

        print()

    print(f"📊 Grand Total: {total_modules} modules across {len(repos)} repositories")


def search_modules(query: str) -> None:
    """Search for modules by name or description"""
    print(f"🔍 Searching for: '{query}'")
    print()

    results = []

    for repo_name, repo_info in OCA_REPOS.items():
        repo_path = Path(repo_info["path"])

        if not repo_path.exists():
            continue

        for item in repo_path.iterdir():
            if not item.is_dir():
                continue

            manifest_path = item / "__manifest__.py"
            if not manifest_path.exists():
                continue

            # Check module name
            if query.lower() in item.name.lower():
                results.append(
                    {
                        "module": item.name,
                        "repo": repo_name,
                        "path": str(item),
                        "match": "name",
                    }
                )
                continue

            # Check manifest for description/summary
            try:
                with open(manifest_path, "r") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append(
                            {
                                "module": item.name,
                                "repo": repo_name,
                                "path": str(item),
                                "match": "description",
                            }
                        )
            except Exception:
                pass

    if results:
        print(f"Found {len(results)} matching modules:")
        print()
        for result in results:
            print(f"🔷 {result['module']}")
            print(f"   Repository: {result['repo']}")
            print(f"   Path: {result['path']}")
            print(f"   Match: {result['match']}")
            print()
    else:
        print("❌ No modules found matching your query")


def generate_catalog() -> None:
    """Generate a catalog of all OCA modules"""
    catalog = {
        "version": "19.0",
        "generated": subprocess.check_output(["date", "-Iseconds"]).decode().strip(),
        "repositories": {},
        "total_modules": 0,
    }

    for repo_name, repo_info in OCA_REPOS.items():
        repo_path = Path(repo_info["path"])

        if not repo_path.exists():
            continue

        modules = []

        for item in repo_path.iterdir():
            if not item.is_dir():
                continue

            manifest_path = item / "__manifest__.py"
            if not manifest_path.exists():
                continue

            try:
                # Read manifest
                with open(manifest_path, "r") as f:
                    content = f.read()
                    # Basic parsing (you could use ast.literal_eval for better parsing)
                    module_info = {
                        "name": item.name,
                        "path": str(item),
                        "source": "oca",
                        "repository": repo_name,
                    }
                    modules.append(module_info)
            except Exception as e:
                print(f"⚠️  Error reading {item.name}: {e}")

        catalog["repositories"][repo_name] = {
            "description": repo_info["description"],
            "url": repo_info["url"],
            "branch": repo_info["branch"],
            "path": repo_info["path"],
            "module_count": len(modules),
            "modules": modules,
        }

        catalog["total_modules"] += len(modules)

    # Save catalog
    catalog_path = Path("datasets/oca_modules_catalog.json")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"✅ Catalog generated: {catalog_path}")
    print(f"📊 Total modules: {catalog['total_modules']}")
    print(f"📚 Repositories: {len(catalog['repositories'])}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced OCA Module Management for InsightPulse Odoo"
    )

    parser.add_argument(
        "--setup", action="store_true", help="Clone all OCA repositories"
    )
    parser.add_argument(
        "--update", action="store_true", help="Update all existing repositories"
    )
    parser.add_argument(
        "--list", metavar="REPO", help="List modules (optionally for specific repo)"
    )
    parser.add_argument(
        "--search", metavar="QUERY", help="Search for modules by name or description"
    )
    parser.add_argument(
        "--catalog", action="store_true", help="Generate OCA modules catalog"
    )

    args = parser.parse_args()

    if args.setup:
        setup_all_repos(update=False)
    elif args.update:
        setup_all_repos(update=True)
    elif args.list is not None:
        list_modules(args.list if args.list else None)
    elif args.search:
        search_modules(args.search)
    elif args.catalog:
        generate_catalog()
    else:
        parser.print_help()
        print()
        print("Quick start:")
        print("  python scripts/vendor_oca_enhanced.py --setup     # Clone all repos")
        print("  python scripts/vendor_oca_enhanced.py --list      # List all modules")
        print(
            "  python scripts/vendor_oca_enhanced.py --search accounting  # Search modules"
        )


if __name__ == "__main__":
    main()
