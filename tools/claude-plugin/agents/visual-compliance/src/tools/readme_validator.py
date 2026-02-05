#!/usr/bin/env python3
"""
README Validator for OCA Standards

This tool validates and generates README.rst files to ensure compliance with:
- OCA documentation standards
- Required sections (Description, Usage, Configuration, etc.)
- Proper reStructuredText format
- Complete module documentation

Addresses issue #396: Add README.rst to all custom modules
"""

import ast
import json
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Set, Optional


# Configuration
ADDONS_ROOT = Path("odoo_addons")
MANIFEST_FILES = ["__manifest__.py", "__openerp__.py"]
README_FILENAME = "README.rst"

# OCA Required Sections
REQUIRED_SECTIONS = [
    "Description",
    "Installation",
    "Configuration",
    "Usage",
    "Bug Tracker",
    "Credits",
]

OPTIONAL_SECTIONS = [
    "Known issues / Roadmap",
    "Changelog",
    "Contributors",
    "Maintainer",
]


class ViolationType(str, Enum):
    """Types of README violations"""
    MISSING_README = "missing_readme"
    EMPTY_README = "empty_readme"
    MISSING_SECTION = "missing_section"
    INVALID_FORMAT = "invalid_format"
    NO_DESCRIPTION = "no_description"
    NO_USAGE = "no_usage"


class Severity(str, Enum):
    """Violation severity levels"""
    CRITICAL = "critical"  # Blocks OCA submission
    HIGH = "high"          # Major compliance issue
    MEDIUM = "medium"      # Should be fixed
    LOW = "low"            # Nice to have


@dataclass
class ReadmeViolation:
    """Represents a single README compliance violation"""
    module_name: str
    module_path: str
    violation_type: ViolationType
    severity: Severity
    description: str
    missing_sections: List[str] = None
    auto_fixable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        if self.missing_sections is None:
            result['missing_sections'] = []
        return result


@dataclass
class ReadmeCheckResult:
    """Result of README validation"""
    is_compliant: bool
    violations: List[ReadmeViolation]
    total_modules: int
    modules_with_readme: int
    modules_missing_readme: int
    fixes_applied: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "is_compliant": self.is_compliant,
            "violations": [v.to_dict() for v in self.violations],
            "total_modules": self.total_modules,
            "modules_with_readme": self.modules_with_readme,
            "modules_missing_readme": self.modules_missing_readme,
            "fixes_applied": self.fixes_applied or [],
        }


class ReadmeValidator:
    """Validates and generates README.rst files"""

    def __init__(self, addons_root: Path = ADDONS_ROOT):
        self.addons_root = addons_root
        self.results: Optional[ReadmeCheckResult] = None

    def is_odoo_module(self, path: Path) -> bool:
        """Check if directory is an Odoo module"""
        if not path.is_dir():
            return False
        return any((path / manifest).exists() for manifest in MANIFEST_FILES)

    def get_module_manifest(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """Load module manifest"""
        for manifest_file in MANIFEST_FILES:
            manifest_path = module_path / manifest_file
            if manifest_path.exists():
                try:
                    text = manifest_path.read_text(encoding="utf-8")
                    tree = ast.parse(text, filename=str(manifest_path))

                    for node in tree.body:
                        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
                            return ast.literal_eval(ast.Expression(node.value))
                        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                            return ast.literal_eval(ast.Expression(node.value))
                except (SyntaxError, ValueError):
                    pass

        return None

    def parse_readme_sections(self, readme_content: str) -> Set[str]:
        """
        Extract section titles from README.rst content.

        Args:
            readme_content: Content of README.rst file

        Returns:
            Set of section titles found
        """
        sections = set()

        # Match reStructuredText section headers (underlined with =, -, ~, etc.)
        lines = readme_content.split("\n")
        for i, line in enumerate(lines):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Check if next line is a section underline
                if next_line and all(c in "=-~`#*^+" for c in next_line) and len(next_line) >= len(line.strip()):
                    sections.add(line.strip())

        return sections

    def check_readme(self, module_path: Path) -> List[ReadmeViolation]:
        """
        Validate README.rst for a single module.

        Args:
            module_path: Path to module directory

        Returns:
            List of violations found
        """
        violations = []
        module_name = module_path.name
        readme_path = module_path / README_FILENAME

        # Violation 1: Missing README
        if not readme_path.exists():
            violations.append(
                ReadmeViolation(
                    module_name=module_name,
                    module_path=str(module_path),
                    violation_type=ViolationType.MISSING_README,
                    severity=Severity.HIGH,
                    description=f"Module '{module_name}' is missing README.rst file",
                    auto_fixable=True,
                )
            )
            return violations

        # Read README content
        try:
            readme_content = readme_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            violations.append(
                ReadmeViolation(
                    module_name=module_name,
                    module_path=str(module_path),
                    violation_type=ViolationType.INVALID_FORMAT,
                    severity=Severity.HIGH,
                    description=f"README.rst has encoding issues (not UTF-8)",
                    auto_fixable=False,
                )
            )
            return violations

        # Violation 2: Empty README
        if not readme_content.strip():
            violations.append(
                ReadmeViolation(
                    module_name=module_name,
                    module_path=str(module_path),
                    violation_type=ViolationType.EMPTY_README,
                    severity=Severity.HIGH,
                    description=f"README.rst is empty",
                    auto_fixable=True,
                )
            )
            return violations

        # Parse sections
        found_sections = self.parse_readme_sections(readme_content)

        # Violation 3: Missing required sections
        missing_sections = []
        for required in REQUIRED_SECTIONS:
            if not any(required.lower() in section.lower() for section in found_sections):
                missing_sections.append(required)

        if missing_sections:
            violations.append(
                ReadmeViolation(
                    module_name=module_name,
                    module_path=str(module_path),
                    violation_type=ViolationType.MISSING_SECTION,
                    severity=Severity.MEDIUM,
                    description=f"README.rst missing required sections: {', '.join(missing_sections)}",
                    missing_sections=missing_sections,
                    auto_fixable=True,
                )
            )

        # Violation 4: No meaningful description
        if len(readme_content.strip()) < 100:  # Arbitrary threshold
            violations.append(
                ReadmeViolation(
                    module_name=module_name,
                    module_path=str(module_path),
                    violation_type=ViolationType.NO_DESCRIPTION,
                    severity=Severity.LOW,
                    description=f"README.rst has minimal content (< 100 characters)",
                    auto_fixable=True,
                )
            )

        return violations

    def check_all(self) -> ReadmeCheckResult:
        """
        Validate README.rst for all modules.

        Returns:
            ReadmeCheckResult with all violations found
        """
        all_violations = []
        total_modules = 0
        modules_with_readme = 0

        if not self.addons_root.exists():
            return ReadmeCheckResult(
                is_compliant=True,
                violations=[],
                total_modules=0,
                modules_with_readme=0,
                modules_missing_readme=0,
            )

        for module_path in self.addons_root.iterdir():
            if not self.is_odoo_module(module_path):
                continue

            total_modules += 1

            # Check if README exists
            if (module_path / README_FILENAME).exists():
                modules_with_readme += 1

            # Validate README
            violations = self.check_readme(module_path)
            all_violations.extend(violations)

        self.results = ReadmeCheckResult(
            is_compliant=len(all_violations) == 0,
            violations=all_violations,
            total_modules=total_modules,
            modules_with_readme=modules_with_readme,
            modules_missing_readme=total_modules - modules_with_readme,
        )

        return self.results

    def generate_readme_template(self, module_path: Path) -> str:
        """
        Generate a basic README.rst template for a module.

        Args:
            module_path: Path to module directory

        Returns:
            Generated README.rst content
        """
        module_name = module_path.name
        manifest = self.get_module_manifest(module_path)

        # Extract info from manifest
        display_name = manifest.get("name", module_name) if manifest else module_name
        summary = manifest.get("summary", "TODO: Add module summary") if manifest else "TODO: Add module summary"
        author = manifest.get("author", "InsightPulseAI") if manifest else "InsightPulseAI"
        website = manifest.get("website", "https://insightpulseai.net") if manifest else "https://insightpulseai.net"

        template = f"""{'=' * len(display_name)}
{display_name}
{'=' * len(display_name)}

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by agents/visual-compliance !!
   !! Please customize before committing                 !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

{summary}

**Table of contents**

.. contents::
   :local:

Description
===========

TODO: Add detailed description of what this module does.

This module provides:

* Feature 1
* Feature 2
* Feature 3

Installation
============

To install this module, you need to:

#. Install dependencies (if any)
#. Update the module list
#. Install the module from Apps menu

Configuration
=============

To configure this module, you need to:

#. Go to Settings > Technical > Parameters > System Parameters
#. Configure parameters as needed

Usage
=====

To use this module, you need to:

#. Navigate to the relevant menu
#. Perform the desired operation

Example usage:

* Step 1
* Step 2
* Step 3

Known issues / Roadmap
======================

* TODO: List known issues
* TODO: List planned features

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/jgtolentino/insightpulse-odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Authors
~~~~~~~

* {author}

Contributors
~~~~~~~~~~~~

* TODO: Add contributors

Maintainers
~~~~~~~~~~~

This module is maintained by {author}.

.. image:: https://insightpulseai.net/logo.png
   :alt: {author}
   :target: {website}

This module is part of the `insightpulse-odoo <https://github.com/jgtolentino/insightpulse-odoo>`_ project.
"""

        return template

    def fix_readmes(self) -> List[str]:
        """
        Automatically fix README violations.

        Returns:
            List of changes made
        """
        if not self.results:
            self.check_all()

        changes = []

        for violation in self.results.violations:
            if not violation.auto_fixable:
                continue

            module_path = Path(violation.module_path)
            readme_path = module_path / README_FILENAME

            # Fix: Generate missing README
            if violation.violation_type in [ViolationType.MISSING_README, ViolationType.EMPTY_README]:
                template = self.generate_readme_template(module_path)
                readme_path.write_text(template, encoding="utf-8")
                changes.append(f"Generated README.rst for {violation.module_name}")

            # Fix: Add missing sections
            elif violation.violation_type == ViolationType.MISSING_SECTION:
                # For now, just report - full section injection requires parsing RST
                changes.append(f"⚠️  {violation.module_name}: Missing sections {violation.missing_sections}")
                changes.append(f"   Manual action required: Add sections to README.rst")

        self.results.fixes_applied = changes
        return changes

    def get_report(self) -> Dict[str, Any]:
        """
        Get structured README validation report.

        Returns:
            Dictionary with summary and detailed results
        """
        if not self.results:
            self.check_all()

        violations_by_type = {}
        violations_by_severity = {}

        for violation in self.results.violations:
            vtype = violation.violation_type.value
            violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1

            sev = violation.severity.value
            violations_by_severity[sev] = violations_by_severity.get(sev, 0) + 1

        coverage_pct = (
            self.results.modules_with_readme / self.results.total_modules * 100
        ) if self.results.total_modules > 0 else 0

        return {
            "summary": {
                "total_modules": self.results.total_modules,
                "modules_with_readme": self.results.modules_with_readme,
                "modules_missing_readme": self.results.modules_missing_readme,
                "readme_coverage": round(coverage_pct, 1),
            },
            "violations_by_type": violations_by_type,
            "violations_by_severity": violations_by_severity,
            "violations": [v.to_dict() for v in self.results.violations],
            "fixes_applied": self.results.fixes_applied or [],
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check (and optionally generate) README.rst files for OCA compliance."
    )
    parser.add_argument("--fix", action="store_true", help="Auto-generate missing README.rst files")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--addons-root", type=Path, default=ADDONS_ROOT, help="Path to addons directory")
    args = parser.parse_args()

    validator = ReadmeValidator(addons_root=args.addons_root)
    result = validator.check_all()

    if args.json:
        report = validator.get_report()
        print(json.dumps(report, indent=2))
    else:
        print(f"📚 README Validation\n")
        print(f"Addons directory: {validator.addons_root}")
        print(f"Required file: {README_FILENAME}\n")

        coverage_pct = (result.modules_with_readme / result.total_modules * 100) if result.total_modules > 0 else 0
        print(f"Coverage: {result.modules_with_readme}/{result.total_modules} modules ({coverage_pct:.1f}%)\n")

        if result.is_compliant:
            print(f"✅ All modules have compliant README.rst files!")
        else:
            print(f"❌ Found {len(result.violations)} README violations:\n")
            for violation in result.violations:
                severity_emoji = {
                    Severity.CRITICAL: "🔴",
                    Severity.HIGH: "🟠",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🔵",
                }[violation.severity]
                print(f"{severity_emoji} [{violation.severity.value}] {violation.module_name}")
                print(f"   {violation.description}")

                if violation.missing_sections:
                    print(f"   Missing: {', '.join(violation.missing_sections)}")
                print()

            # Apply fixes if requested
            if args.fix:
                print("🔧 Applying fixes...\n")
                changes = validator.fix_readmes()
                if changes:
                    for change in changes:
                        print(f"   • {change}")
                else:
                    print("   No auto-fixable violations found")
                print()

        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total modules: {result.total_modules}")
        print(f"   With README: {result.modules_with_readme}")
        print(f"   Missing README: {result.modules_missing_readme}")
        print(f"   Status: {'✅ Compliant' if result.is_compliant else '❌ Non-compliant'}")

    # Exit code: 0 if compliant, 1 otherwise
    return 0 if result.is_compliant else 1


if __name__ == "__main__":
    sys.exit(main())
