#!/usr/bin/env python3

"""
Validate that the repository structure matches specification.
Returns exit code 0 if valid, 1 if invalid.
"""

import json
import re
from pathlib import Path


class RepoStructureValidator:
    """
    Validate repository structure against specification.

    Checks:
    - Required directories exist
    - Required files exist
    - File formats are valid
    - Naming conventions followed
    - No forbidden patterns
    """

    REQUIRED_STRUCTURE = {
        # Core directories (MUST exist)
        "required_dirs": [
            ".github/workflows",
            "docs/architecture",
            "docs/knowledge-base",
            "docs/runbooks",
            "skills/core",
            "custom",
            "addons",
            "infrastructure/docker",
            "infrastructure/terraform",
            "tests/ai",
            "tests/integration",
            "prompts/templates",
            "context-engineering/rag",
            "evals/datasets",
            "monitoring/prometheus",
            "monitoring/grafana/dashboards",
            "auto-healing/health-checks",
            "scripts/setup",
            "scripts/deployment",
        ],
        # Core files (MUST exist)
        "required_files": [
            "README.md",
            "Makefile",
            "docker-compose.yml",
            ".gitignore",
            "requirements.txt",
            "docs/ROADMAP.md",
            "docs/STATUS.md",
            "docs/architecture/README.md",
            "skills/README.md",
            "prompts/README.md",
            ".github/workflows/ci-odoo.yml",
        ],
        # Forbidden patterns (MUST NOT exist)
        "forbidden_patterns": [
            "**/node_modules",
            "**/__pycache__",
            "**/.DS_Store",
            "**/secrets.yml",
            "**/credentials.json",
            "**/*.pyc",
        ],
        # Naming conventions
        "naming_rules": {
            "skill_files": r"^SKILL\.md$",
            "workflow_files": r"^\d{2}-[a-z-]+\.yml$",
            "test_files": r"^test_.*\.py$",
        },
        # File content validations
        "content_checks": {
            "yaml_files": ["*.yml", "*.yaml"],
            "json_files": ["*.json"],
            "python_files": ["*.py"],
            "markdown_files": ["*.md"],
        },
    }

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.errors = []
        self.warnings = []
        self.info = []

    def validate_all(self) -> bool:
        """Run all validation checks."""

        print("🔍 Validating repository structure...\n")

        # 1. Check required directories
        self.check_required_directories()

        # 2. Check required files
        self.check_required_files()

        # 3. Check forbidden patterns
        self.check_forbidden_patterns()

        # 4. Validate naming conventions
        self.validate_naming_conventions()

        # 5. Validate file contents
        self.validate_file_contents()

        # 6. Check cross-references
        self.check_cross_references()

        # 7. Validate skills
        self.validate_skills()

        # 8. Check documentation completeness
        self.check_documentation()

        # Print results
        self.print_results()

        return len(self.errors) == 0

    def check_required_directories(self):
        """Check that all required directories exist."""

        print("📁 Checking required directories...")

        found_count = 0
        for dir_path in self.REQUIRED_STRUCTURE["required_dirs"]:
            full_path = self.repo_path / dir_path

            if not full_path.exists():
                self.errors.append(f"Missing required directory: {dir_path}")
            else:
                self.info.append(f"✓ {dir_path}")
                found_count += 1

        total = len(self.REQUIRED_STRUCTURE["required_dirs"])
        print(f"   Found {found_count} of {total} required directories\n")

    def check_required_files(self):
        """Check that all required files exist."""

        print("📄 Checking required files...")

        found_count = 0
        for file_path in self.REQUIRED_STRUCTURE["required_files"]:
            full_path = self.repo_path / file_path

            if not full_path.exists():
                self.errors.append(f"Missing required file: {file_path}")
            else:
                # Check file is not empty
                if full_path.stat().st_size == 0:
                    self.warnings.append(f"File is empty: {file_path}")
                else:
                    self.info.append(f"✓ {file_path}")
                    found_count += 1

        total = len(self.REQUIRED_STRUCTURE["required_files"])
        print(f"   Found {found_count} required files\n")

    def check_forbidden_patterns(self):
        """Check for forbidden files/directories."""

        print("🚫 Checking for forbidden patterns...")

        found_forbidden = []

        for pattern in self.REQUIRED_STRUCTURE["forbidden_patterns"]:
            matches = list(self.repo_path.glob(pattern))
            if matches:
                found_forbidden.extend(matches)
                self.errors.append(
                    f"Found forbidden pattern: {pattern} ({len(matches)} matches)"
                )

        if not found_forbidden:
            print("   ✓ No forbidden patterns found\n")
        else:
            print(f"   ✗ Found {len(found_forbidden)} forbidden files/directories\n")

    def validate_naming_conventions(self):
        """Validate naming conventions."""

        print("📝 Validating naming conventions...")

        # Check skill files
        skill_files = list(self.repo_path.glob("skills/**/SKILL.md"))
        print(f"   Found {len(skill_files)} skill files")

        # Check workflow files
        workflow_files = list(self.repo_path.glob(".github/workflows/*.yml"))
        print(f"   Found {len(workflow_files)} workflow files")

        # Check test files
        test_files = list(self.repo_path.glob("tests/**/test_*.py"))
        print(f"   Found {len(test_files)} test files\n")

    def validate_file_contents(self):
        """Validate that files have correct syntax."""

        print("🔬 Validating file contents...")

        # YAML files
        yaml_files = list(self.repo_path.glob("**/*.yml")) + list(
            self.repo_path.glob("**/*.yaml")
        )
        # Filter out submodules and virtual environments
        yaml_files = [
            f
            for f in yaml_files
            if not any(p in str(f) for p in ["addons/", "venv/", ".venv/"])
        ]
        yaml_valid = 0

        for yaml_file in yaml_files[:50]:  # Limit to first 50 to avoid slowdown
            try:
                import yaml

                with open(yaml_file) as f:
                    yaml.safe_load(f)
                yaml_valid += 1
            except Exception as e:
                self.errors.append(
                    f"Invalid YAML: {yaml_file.relative_to(self.repo_path)} - {str(e)}"
                )

        print(f"   YAML: {yaml_valid}/{len(yaml_files[:50])} valid")

        # JSON files
        json_files = list(self.repo_path.glob("**/*.json"))
        json_files = [
            f
            for f in json_files
            if not any(
                p in str(f) for p in ["addons/", "venv/", ".venv/", "node_modules/"]
            )
        ]
        json_valid = 0

        for json_file in json_files[:50]:  # Limit to first 50
            try:
                with open(json_file) as f:
                    json.load(f)
                json_valid += 1
            except Exception as e:
                self.errors.append(
                    f"Invalid JSON: {json_file.relative_to(self.repo_path)} - {str(e)}"
                )

        print(f"   JSON: {json_valid}/{len(json_files[:50])} valid")

        # Python files (in scripts/ and tests/ only)
        python_files = list(self.repo_path.glob("scripts/**/*.py")) + list(
            self.repo_path.glob("tests/**/*.py")
        )
        python_valid = 0

        for py_file in python_files:
            try:
                import ast

                with open(py_file) as f:
                    ast.parse(f.read())
                python_valid += 1
            except Exception as e:
                self.errors.append(
                    f"Invalid Python: {py_file.relative_to(self.repo_path)} - {str(e)}"
                )

        print(f"   Python: {python_valid}/{len(python_files)} valid\n")

    def validate_skills(self):
        """Validate skills structure and content."""

        print("🎓 Validating skills...")

        skills_dir = self.repo_path / "skills"

        if not skills_dir.exists():
            self.errors.append("Skills directory missing")
            return

        skill_files = list(skills_dir.glob("**/SKILL.md"))

        valid_skills = 0

        for skill_file in skill_files:
            if self.validate_skill_file(skill_file):
                valid_skills += 1

        print(f"   Found {valid_skills}/{len(skill_files)} valid skills\n")

    def validate_skill_file(self, skill_file: Path) -> bool:
        """Validate a single SKILL.md file."""

        required_sections = [
            "## Purpose",
            "## Core Competencies",
        ]

        try:
            with open(skill_file) as f:
                content = f.read()

            # Check for required sections
            for section in required_sections:
                if section not in content:
                    self.warnings.append(
                        f"Skill missing section '{section}': {skill_file.relative_to(self.repo_path)}"
                    )
                    return False

            # Check for YAML frontmatter or title
            if not content.startswith("---") and not content.startswith("# "):
                self.warnings.append(
                    f"Skill has no frontmatter or title: {skill_file.relative_to(self.repo_path)}"
                )
                return False

            return True

        except Exception as e:
            self.errors.append(f"Error reading skill file {skill_file}: {str(e)}")
            return False

    def check_documentation(self):
        """Check documentation completeness."""

        print("📚 Checking documentation completeness...")

        # Check that each major directory has README
        major_dirs = [
            "skills",
            "prompts",
            "evals",
            "tests",
            "monitoring",
            "custom",
            "infrastructure",
        ]

        missing_readmes = []

        for dir_name in major_dirs:
            dir_path = self.repo_path / dir_name
            if dir_path.exists():
                readme = dir_path / "README.md"
                if not readme.exists():
                    missing_readmes.append(dir_name)
                    self.warnings.append(f"Missing README.md in {dir_name}/")

        if not missing_readmes:
            print("   ✓ All major directories have README\n")
        else:
            print(f"   ⚠️  {len(missing_readmes)} directories missing README\n")

    def check_cross_references(self):
        """Check that cross-references are valid."""

        print("🔗 Checking cross-references...")

        # Check Makefile targets reference actual scripts
        makefile = self.repo_path / "Makefile"

        if makefile.exists():
            with open(makefile) as f:
                content = f.read()

            # Extract script references
            scripts = re.findall(
                r"(?:bash|sh|python3?|\./)?\s*scripts/([a-z0-9_/-]+\.(?:sh|py))",
                content,
                re.IGNORECASE,
            )

            missing_scripts = []
            for script in scripts:
                if not (self.repo_path / "scripts" / script).exists():
                    missing_scripts.append(script)
                    self.warnings.append(
                        f"Makefile references missing script: scripts/{script}"
                    )

            if not missing_scripts:
                print("   ✓ All Makefile scripts exist\n")
            else:
                print(f"   ⚠️  {len(missing_scripts)} referenced scripts missing\n")
        else:
            self.warnings.append("Makefile not found")

    def print_results(self):
        """Print validation results."""

        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60 + "\n")

        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:20]:  # Show first 20
                print(f"   • {error}")
            if len(self.errors) > 20:
                print(f"   ... and {len(self.errors) - 20} more errors")
            print()

        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
            print()

        if not self.errors and not self.warnings:
            print("✅ ALL CHECKS PASSED!")
            print()

        # Summary
        print("SUMMARY:")
        print(f"   Errors:   {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Info:     {len(self.info)}")
        print()

        if self.errors:
            print("❌ VALIDATION FAILED")
            return False
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            return True
        else:
            print("✅ VALIDATION PASSED")
            return True


if __name__ == "__main__":
    import sys

    validator = RepoStructureValidator()
    success = validator.validate_all()

    sys.exit(0 if success else 1)
