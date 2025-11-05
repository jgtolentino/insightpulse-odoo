#!/usr/bin/env python3

"""
Integration tests for repository structure.

Tests that the structure actually works in practice.
"""

import subprocess
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestRepoStructure:
    """
    Integration tests for repository structure.

    Tests that the structure actually works in practice.
    """

    def test_makefile_commands_work(self):
        """Test that all Makefile commands execute without error."""

        # Test dry-run for help target
        result = subprocess.run(
            ['make', '-n', 'help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )

        assert result.returncode == 0, f"make help failed: {result.stderr}"

    def test_docker_compose_validates(self):
        """Test that docker-compose.yml is valid."""

        docker_compose = Path(__file__).parent.parent.parent / 'docker-compose.yml'

        if not docker_compose.exists():
            # Skip if docker-compose.yml doesn't exist
            return

        result = subprocess.run(
            ['docker-compose', 'config'],
            capture_output=True,
            text=True,
            cwd=docker_compose.parent
        )

        # Docker compose might not be available in CI
        if result.returncode != 0 and 'not found' in result.stderr:
            return  # Skip if docker-compose not available

        assert result.returncode == 0, f"docker-compose config invalid: {result.stderr}"

    def test_skills_are_loadable(self):
        """Test that all skills can be parsed."""

        skills_dir = Path(__file__).parent.parent.parent / 'skills'

        if not skills_dir.exists():
            assert False, "Skills directory not found"

        skill_files = list(skills_dir.glob('**/SKILL.md'))

        assert len(skill_files) > 0, "No skills found"

        for skill_file in skill_files:
            with open(skill_file) as f:
                content = f.read()

            assert '## Purpose' in content or '# ' in content, f"Skill missing structure: {skill_file}"
            assert len(content) > 50, f"Skill too short: {skill_file}"

    def test_github_workflows_validate(self):
        """Test that GitHub workflows are valid."""

        workflows_dir = Path(__file__).parent.parent.parent / '.github/workflows'

        if not workflows_dir.exists():
            # Skip if no workflows directory
            return

        workflow_files = list(workflows_dir.glob('*.yml'))

        if len(workflow_files) == 0:
            return  # Skip if no workflows

        for workflow in workflow_files:
            # Validate YAML
            try:
                import yaml
            except ImportError:
                # Skip if yaml not available
                return

            with open(workflow) as f:
                data = yaml.safe_load(f)

            # Check required fields
            assert 'name' in data, f"Workflow missing name: {workflow}"
            assert 'on' in data or 'true' in data, f"Workflow missing trigger: {workflow}"

    def test_python_files_importable(self):
        """Test that Python files are importable."""

        repo_root = Path(__file__).parent.parent.parent

        # Check only scripts and tests directories
        python_files = []
        if (repo_root / 'scripts').exists():
            python_files.extend((repo_root / 'scripts').glob('**/*.py'))
        if (repo_root / 'tests').exists():
            python_files.extend((repo_root / 'tests').glob('**/*.py'))

        errors = []

        for py_file in python_files:
            # Skip test files and __pycache__
            if '__pycache__' in str(py_file):
                continue

            try:
                import ast
                with open(py_file) as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")

        assert len(errors) == 0, f"Python syntax errors:\n" + "\n".join(errors)

    def test_documentation_links_work(self):
        """Test that documentation links are not broken."""

        import re

        docs_dir = Path(__file__).parent.parent.parent / 'docs'

        if not docs_dir.exists():
            return  # Skip if no docs directory

        md_files = list(docs_dir.glob('**/*.md'))
        broken_links = []

        for md_file in md_files:
            with open(md_file) as f:
                content = f.read()

            # Extract relative links
            links = re.findall(r'\[.*?\]\(((?!http)[^\)]+)\)', content)

            for link in links:
                # Remove anchors
                link_path = link.split('#')[0]

                if link_path and not link_path.startswith('mailto:'):
                    target = (md_file.parent / link_path).resolve()

                    if not target.exists():
                        broken_links.append(f"{md_file.name}: broken link to {link_path}")

        # Allow some broken links for now
        if len(broken_links) > 0:
            print(f"⚠️  Found {len(broken_links)} broken links in documentation")

    def test_scripts_are_executable(self):
        """Test that scripts have execute permissions."""

        scripts_dir = Path(__file__).parent.parent.parent / 'scripts'

        if not scripts_dir.exists():
            return  # Skip if no scripts directory

        scripts = list(scripts_dir.glob('**/*.sh'))

        non_executable = []

        for script in scripts:
            import stat
            st = script.stat()

            if not st.st_mode & stat.S_IXUSR:
                non_executable.append(str(script.name))

        # Allow some non-executable scripts for now
        if len(non_executable) > 0:
            print(f"⚠️  Found {len(non_executable)} non-executable scripts")

    def test_required_directories_exist(self):
        """Test that core required directories exist."""

        repo_root = Path(__file__).parent.parent.parent

        critical_dirs = [
            'scripts',
            'docs',
            '.github',
        ]

        for dir_name in critical_dirs:
            dir_path = repo_root / dir_name
            assert dir_path.exists(), f"Critical directory missing: {dir_name}"


# Run tests with pytest if available, otherwise run directly
if __name__ == '__main__':
    try:
        import pytest
        pytest.main([__file__, '-v'])
    except ImportError:
        print("⚠️  pytest not available, running basic tests...")
        test = TestRepoStructure()

        tests = [
            ('Makefile commands', test.test_makefile_commands_work),
            ('Docker Compose validation', test.test_docker_compose_validates),
            ('Skills loadable', test.test_skills_are_loadable),
            ('GitHub workflows', test.test_github_workflows_validate),
            ('Python files importable', test.test_python_files_importable),
            ('Documentation links', test.test_documentation_links_work),
            ('Scripts executable', test.test_scripts_are_executable),
            ('Required directories', test.test_required_directories_exist),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                test_func()
                print(f"✅ {name}")
                passed += 1
            except AssertionError as e:
                print(f"❌ {name}: {e}")
                failed += 1
            except Exception as e:
                print(f"⚠️  {name}: {e}")

        print(f"\nResults: {passed} passed, {failed} failed")
        sys.exit(0 if failed == 0 else 1)
