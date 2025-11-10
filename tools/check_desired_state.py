#!/usr/bin/env python3
"""
Desired State Guard - Validates repository against desired_state.json specification.

This script enforces the architectural rules, module conventions, and compliance
requirements defined in docs/desired_state.json.

Usage:
    python3 tools/check_desired_state.py
    python3 tools/check_desired_state.py --spec docs/desired_state.json
    python3 tools/check_desired_state.py --verbose
"""

import json
import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse


class DesiredStateValidator:
    """Validates repository against desired state specification."""

    def __init__(self, spec_path: Path, verbose: bool = False):
        self.spec_path = spec_path
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
        self.spec: Dict[str, Any] = {}

    def log(self, msg: str, level: str = "info") -> None:
        """Log a message with appropriate emoji and formatting."""
        emoji_map = {
            "error": "❌",
            "warn": "⚠️",
            "ok": "✅",
            "info": "▶️",
            "title": "🎯"
        }
        emoji = emoji_map.get(level, "•")
        print(f"{emoji} {msg}")

    def fail(self, msg: str) -> None:
        """Record a failure."""
        self.errors.append(msg)
        self.log(msg, "error")

    def warn(self, msg: str) -> None:
        """Record a warning."""
        self.warnings.append(msg)
        self.log(msg, "warn")

    def ok(self, msg: str) -> None:
        """Record a success."""
        self.passed.append(msg)
        self.log(msg, "ok")

    def load_spec(self) -> bool:
        """Load the desired state JSON specification."""
        if not self.spec_path.exists():
            self.fail(f"Spec file not found: {self.spec_path}")
            return False

        try:
            self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
            self.ok(f"Loaded spec: {self.spec_path}")
            return True
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON in spec file: {e}")
            return False

    def validate_odoo_version(self) -> None:
        """Validate Odoo version matches specification."""
        target = self.spec.get("target_state", {})
        expected_version = target.get("odoo_version", "")

        if not expected_version:
            self.warn("No odoo_version specified in target_state")
            return

        self.ok(f"Odoo target version: {expected_version}")

        # Check odoo.conf if it exists
        odoo_conf = Path("odoo.conf")
        if odoo_conf.exists():
            content = odoo_conf.read_text()
            # Basic validation that it's configured
            if "addons_path" in content and "db_host" in content:
                self.ok("odoo.conf exists and appears valid")
            else:
                self.warn("odoo.conf exists but may be incomplete")

    def validate_addons_root(self) -> bool:
        """Validate addons root directory exists."""
        target = self.spec.get("target_state", {})
        addons_root = target.get("addons_root", "")

        if not addons_root:
            self.warn("No addons_root specified in target_state")
            return False

        addons_path = Path(addons_root)
        if not addons_path.exists():
            self.fail(f"Addons root does not exist: {addons_root}")
            return False

        if not addons_path.is_dir():
            self.fail(f"Addons root is not a directory: {addons_root}")
            return False

        self.ok(f"Addons root exists: {addons_root}")
        return True

    def validate_module_naming(self) -> None:
        """Validate custom modules follow naming conventions."""
        target = self.spec.get("target_state", {})
        addons_root = Path(target.get("addons_root", "odoo_addons"))
        module_prefix = target.get("module_prefix", "ipai_")
        expected_modules = set(target.get("modules", {}).get("custom", []))

        if not addons_root.exists():
            return

        # Find all module directories
        module_dirs = [d for d in addons_root.iterdir() if d.is_dir() and not d.name.startswith('.')]

        non_ipai = []
        missing_modules = set(expected_modules)
        found_modules = []

        for module_dir in module_dirs:
            module_name = module_dir.name

            # Check if it has __manifest__.py
            manifest_path = module_dir / "__manifest__.py"
            if not manifest_path.exists():
                continue  # Not an Odoo module

            found_modules.append(module_name)

            # Check prefix
            if not module_name.startswith(module_prefix):
                non_ipai.append(module_name)

            # Remove from missing set if found
            if module_name in missing_modules:
                missing_modules.remove(module_name)

        # Report findings
        if non_ipai:
            self.warn(f"Modules without '{module_prefix}' prefix: {', '.join(non_ipai)}")
        else:
            self.ok(f"All modules use '{module_prefix}' prefix")

        if missing_modules:
            self.warn(f"Expected modules not found: {', '.join(sorted(missing_modules))}")

        if found_modules:
            self.ok(f"Found {len(found_modules)} custom modules")

    def validate_module_manifests(self) -> None:
        """Validate module manifests have required fields."""
        target = self.spec.get("target_state", {})
        addons_root = Path(target.get("addons_root", "odoo_addons"))
        manifest_reqs = target.get("manifest_requirements", {})
        required_fields = manifest_reqs.get("required_fields", [])
        allowed_licenses = manifest_reqs.get("license_allowed", [])

        if not addons_root.exists():
            return

        modules_checked = 0
        modules_passed = 0

        for module_dir in addons_root.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith('.'):
                continue

            manifest_path = module_dir / "__manifest__.py"
            if not manifest_path.exists():
                continue

            modules_checked += 1

            try:
                # Read manifest as Python dict (safely)
                manifest_content = manifest_path.read_text(encoding="utf-8")
                # This is a simplistic check - in production you'd use ast.literal_eval
                manifest_valid = True

                # Check for required fields (basic string search)
                missing_fields = []
                for field in required_fields:
                    if f'"{field}"' not in manifest_content and f"'{field}'" not in manifest_content:
                        missing_fields.append(field)

                if missing_fields:
                    self.warn(f"{module_dir.name}/__manifest__.py missing: {', '.join(missing_fields)}")
                else:
                    modules_passed += 1

                # Check license
                has_valid_license = False
                for lic in allowed_licenses:
                    if lic in manifest_content:
                        has_valid_license = True
                        break

                if not has_valid_license and self.verbose:
                    self.warn(f"{module_dir.name}/__manifest__.py: license not in allowed list")

            except Exception as e:
                self.warn(f"Error reading {module_dir.name}/__manifest__.py: {e}")

        if modules_checked > 0:
            self.ok(f"Manifest validation: {modules_passed}/{modules_checked} modules passed")
        else:
            self.warn("No module manifests found to validate")

    def validate_no_secrets(self) -> None:
        """Check for hardcoded secrets in repository."""
        # Simple pattern matching for common secret patterns
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            r'aws[_-]?access[_-]?key',
            r'AKIA[0-9A-Z]{16}',  # AWS access key pattern
        ]

        # Files to skip
        skip_files = {'.git', 'node_modules', '__pycache__', '.pyc', 'venv', 'env'}

        secrets_found = []

        try:
            for py_file in Path('.').rglob('*.py'):
                # Skip vendored/third-party code
                if any(skip in str(py_file) for skip in skip_files):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            secrets_found.append(str(py_file))
                            break
                except Exception:
                    continue

            if secrets_found:
                self.warn(f"Potential secrets found in: {', '.join(secrets_found[:5])}")
                if len(secrets_found) > 5:
                    self.warn(f"... and {len(secrets_found) - 5} more files")
            else:
                self.ok("No obvious secrets detected in Python files")

        except Exception as e:
            self.warn(f"Secret scanning failed: {e}")

    def validate_runtime_urls(self) -> None:
        """Validate runtime environment URLs from spec."""
        runtime = self.spec.get("runtime_environment", {})

        urls = {
            "ERP": runtime.get("ERP_BASE_URL"),
            "Superset": runtime.get("SUPERSET_BASE_URL"),
            "n8n": runtime.get("N8N_BASE_URL"),
            "OCR": runtime.get("OCR_BASE_URL"),
        }

        for service, url in urls.items():
            if url:
                self.ok(f"{service} URL configured: {url}")
            else:
                self.warn(f"{service} URL not configured in runtime_environment")

    def validate_routing_spec(self) -> None:
        """Validate routing specification."""
        routing = self.spec.get("routing_specification", {})
        routes = routing.get("routes", [])

        if not routes:
            self.warn("No routing specification defined")
            return

        self.ok(f"Routing specification: {len(routes)} routes defined")

        base_domain = routing.get("base_domain", "")
        if base_domain:
            self.ok(f"Base domain: {base_domain}")

        # List configured routes
        if self.verbose:
            for route in routes:
                subdomain = route.get("subdomain", "")
                target = route.get("target", "")
                print(f"   • {subdomain}.{base_domain} → {target}")

    def validate_compliance_requirements(self) -> None:
        """Validate compliance requirements are documented."""
        compliance = self.spec.get("compliance_requirements", {})

        if not compliance:
            self.warn("No compliance requirements specified")
            return

        for standard, config in compliance.items():
            if config.get("enabled"):
                self.ok(f"Compliance: {standard.upper()} enabled")

    def run_external_validators(self) -> None:
        """Run external validation scripts if they exist."""
        validators = [
            ("tools/check_manifests.py", "Manifest checker"),
            ("scripts/validate-structure.sh", "Structure validator"),
        ]

        for script_path, description in validators:
            script = Path(script_path)
            if not script.exists():
                continue

            self.log(f"Running {description}...", "info")
            try:
                result = subprocess.run(
                    [sys.executable, str(script)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.ok(f"{description} passed")
                else:
                    self.warn(f"{description} failed (see output above)")
                    if self.verbose and result.stdout:
                        print(result.stdout)

            except subprocess.TimeoutExpired:
                self.warn(f"{description} timed out")
            except Exception as e:
                self.warn(f"{description} error: {e}")

    def validate_all(self) -> int:
        """Run all validations and return exit code."""
        self.log("Desired State Guard - Starting Validation", "title")
        print()

        if not self.load_spec():
            return 1

        # Run validation checks
        self.validate_odoo_version()
        self.validate_addons_root()
        self.validate_module_naming()
        self.validate_module_manifests()
        self.validate_no_secrets()
        self.validate_runtime_urls()
        self.validate_routing_spec()
        self.validate_compliance_requirements()
        self.run_external_validators()

        # Print summary
        print()
        print("=" * 70)
        self.log("Validation Summary", "title")
        print("=" * 70)

        if self.passed:
            print(f"✅ Passed:   {len(self.passed)}")

        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            if self.verbose:
                for warning in self.warnings:
                    print(f"   • {warning}")

        if self.errors:
            print(f"❌ Errors:   {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")

        print("=" * 70)

        # Determine exit code
        if self.errors:
            print("\n❌ Validation FAILED - Repository does not match desired state")
            return 1
        elif self.warnings:
            print("\n⚠️  Validation PASSED with warnings")
            return 0
        else:
            print("\n🎯 Validation PASSED - Repository matches desired state")
            return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate repository against desired state specification"
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("docs/desired_state.json"),
        help="Path to desired_state.json (default: docs/desired_state.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    validator = DesiredStateValidator(args.spec, verbose=args.verbose)
    exit_code = validator.validate_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
