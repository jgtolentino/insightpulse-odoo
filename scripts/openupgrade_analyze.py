#!/usr/bin/env python3
"""
OpenUpgrade Module Analysis Script

Analyzes Odoo modules for upgrade compatibility and generates migration reports.

Usage:
    python3 scripts/openupgrade_analyze.py --module my_custom_module
    python3 scripts/openupgrade_analyze.py --all  # Analyze all custom modules
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    pass
except ImportError:
    print("ERROR: openupgradelib not installed. Run: pip install openupgradelib")
    sys.exit(1)


CUSTOM_ADDONS_PATH = Path(__file__).parent.parent / "odoo" / "custom-addons"
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "openupgrade"


def analyze_module(module_path: Path) -> Dict[str, Any]:
    """
    Analyze a single module for upgrade compatibility.

    Returns:
        {
            "module_name": "my_module",
            "has_migrations": True,
            "versions": ["19.0.1.0.0", "19.0.2.0.0"],
            "migration_scripts": {
                "19.0.1.0.0": ["pre-migration.py", "post-migration.py"]
            },
            "dependencies": ["base", "account"],
            "issues": []
        }
    """
    module_name = module_path.name
    migrations_path = module_path / "migrations"
    manifest_path = module_path / "__manifest__.py"

    result = {
        "module_name": module_name,
        "has_migrations": migrations_path.exists(),
        "versions": [],
        "migration_scripts": {},
        "dependencies": [],
        "issues": [],
    }

    # Read manifest
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = eval(f.read())

            result["dependencies"] = manifest.get("depends", [])
            result["version"] = manifest.get("version", "unknown")
        except Exception as e:
            result["issues"].append(f"Failed to parse manifest: {e}")

    # Check migrations
    if migrations_path.exists():
        for version_dir in migrations_path.iterdir():
            if version_dir.is_dir():
                version = version_dir.name
                result["versions"].append(version)

                scripts = []
                for script in [
                    "pre-migration.py",
                    "post-migration.py",
                    "end-migration.py",
                ]:
                    if (version_dir / script).exists():
                        scripts.append(script)

                result["migration_scripts"][version] = scripts

                # Check for common issues
                if not scripts:
                    result["issues"].append(
                        f"Version {version} directory exists but no migration scripts found"
                    )

    return result


def analyze_oca_compatibility(
    module_name: str, dependencies: List[str]
) -> Dict[str, Any]:
    """
    Check if OCA dependencies have migration scripts available.

    Returns:
        {
            "module_name": "account",
            "has_oca_migrations": True,
            "migration_url": "https://github.com/OCA/OpenUpgrade/tree/19.0/..."
        }
    """
    # Common OCA modules
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
    }

    compatibility = {}

    for dep in dependencies:
        if dep in oca_modules:
            # Check if OCA migration exists
            github_url = f"https://github.com/OCA/OpenUpgrade/tree/19.0/openupgrade_scripts/scripts/{dep}"
            compatibility[dep] = {
                "is_oca_module": True,
                "migration_url": github_url,
                "recommendation": f"Check {github_url} for migration scripts",
            }

    return compatibility


def generate_report(analyses: List[Dict[str, Any]], output_path: Path):
    """
    Generate HTML report of analysis results.
    """
    html = (
        """
<!DOCTYPE html>
<html>
<head>
    <title>OpenUpgrade Module Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .module { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .module-name { font-size: 1.2em; font-weight: bold; color: #007bff; }
        .has-migrations { background-color: #d4edda; }
        .no-migrations { background-color: #fff3cd; }
        .issues { background-color: #f8d7da; }
        .migration-version { margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 3px solid #007bff; }
        .issue { color: #721c24; margin: 5px 0; }
        .dependency { display: inline-block; margin: 3px; padding: 3px 8px; background: #e9ecef; border-radius: 3px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>OpenUpgrade Module Analysis Report</h1>
    <p>Generated: """
        + str(Path.cwd())
        + """</p>
"""
    )

    for analysis in analyses:
        module_name = analysis["module_name"]
        has_migrations = analysis["has_migrations"]
        issues = analysis.get("issues", [])

        css_class = "module "
        if issues:
            css_class += "issues"
        elif has_migrations:
            css_class += "has-migrations"
        else:
            css_class += "no-migrations"

        html += f"""
    <div class="{css_class}">
        <div class="module-name">{module_name}</div>
        <p><strong>Version:</strong> {analysis.get('version', 'unknown')}</p>
        <p><strong>Has Migrations:</strong> {'Yes' if has_migrations else 'No'}</p>
"""

        if analysis.get("dependencies"):
            html += "<p><strong>Dependencies:</strong><br>"
            for dep in analysis["dependencies"]:
                html += f'<span class="dependency">{dep}</span>'
            html += "</p>"

        if analysis.get("migration_scripts"):
            html += "<p><strong>Migration Scripts:</strong></p>"
            for version, scripts in analysis["migration_scripts"].items():
                html += f"""
        <div class="migration-version">
            <strong>{version}:</strong><br>
            {', '.join(scripts)}
        </div>
"""

        if issues:
            html += "<p><strong>Issues:</strong></p>"
            for issue in issues:
                html += f'<div class="issue">⚠️ {issue}</div>'

        html += "    </div>\n"

    html += """
</body>
</html>
"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"✅ HTML report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Odoo modules for OpenUpgrade compatibility"
    )
    parser.add_argument("--module", help="Specific module to analyze")
    parser.add_argument("--all", action="store_true", help="Analyze all custom modules")
    parser.add_argument("--output", help="Output file path", default=None)
    args = parser.parse_args()

    if not args.module and not args.all:
        parser.error("Specify --module MODULE or --all")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    analyses = []

    if args.all:
        print("Analyzing all custom modules...")
        for module_path in CUSTOM_ADDONS_PATH.iterdir():
            if module_path.is_dir() and not module_path.name.startswith("."):
                if module_path.name.startswith("__"):
                    continue  # Skip template modules

                print(f"  Analyzing {module_path.name}...")
                analysis = analyze_module(module_path)
                analyses.append(analysis)
    else:
        module_path = CUSTOM_ADDONS_PATH / args.module
        if not module_path.exists():
            print(f"ERROR: Module not found: {module_path}")
            sys.exit(1)

        print(f"Analyzing {args.module}...")
        analysis = analyze_module(module_path)
        analyses.append(analysis)

    # Generate reports
    json_output = OUTPUT_DIR / "analysis.json"
    with open(json_output, "w") as f:
        json.dump(analyses, f, indent=2)
    print(f"✅ JSON report generated: {json_output}")

    html_output = args.output or OUTPUT_DIR / "analysis.html"
    generate_report(analyses, Path(html_output))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total = len(analyses)
    with_migrations = sum(1 for a in analyses if a["has_migrations"])
    with_issues = sum(1 for a in analyses if a["issues"])

    print(f"Total modules analyzed: {total}")
    print(f"Modules with migrations: {with_migrations}")
    print(f"Modules with issues: {with_issues}")

    if with_issues > 0:
        print("\nModules with issues:")
        for analysis in analyses:
            if analysis["issues"]:
                print(f"  ⚠️  {analysis['module_name']}")
                for issue in analysis["issues"]:
                    print(f"     - {issue}")

    return 0 if with_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
