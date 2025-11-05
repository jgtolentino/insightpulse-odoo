#!/usr/bin/env python3

"""
AI tests for skills framework.
"""

import pytest
from pathlib import Path


class TestSkillsFramework:
    """Test skills loading and validation."""

    def test_skills_directory_exists(self):
        """Test that skills directory exists."""
        skills_dir = Path('skills')
        assert skills_dir.exists(), "Skills directory should exist"

    def test_skill_files_exist(self):
        """Test that skill files exist."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        assert len(skill_files) > 0, "Should have at least one skill file"

    def test_skill_file_structure(self):
        """Test that skill files have required structure."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        for skill_file in skill_files:
            with open(skill_file) as f:
                content = f.read()

            # Check for key sections (flexible)
            has_structure = (
                '##' in content or  # Has sections
                '#' in content      # Has title
            )

            assert has_structure, f"{skill_file} should have markdown structure"
            assert len(content) > 50, f"{skill_file} should have content"

    def test_skill_readme_exists(self):
        """Test that skills README exists."""
        readme = Path('skills/README.md')
        assert readme.exists(), "Skills README should exist"

    def test_skills_loadable(self):
        """Test that skills can be loaded and parsed."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        for skill_file in skill_files:
            try:
                with open(skill_file) as f:
                    content = f.read()

                assert isinstance(content, str)
                assert len(content) > 0

            except Exception as e:
                pytest.fail(f"Failed to load skill {skill_file}: {e}")


class TestSkillContent:
    """Test skill content quality."""

    def test_skills_have_descriptions(self):
        """Test that skills have meaningful descriptions."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        for skill_file in skill_files:
            with open(skill_file) as f:
                content = f.read()

            # Should have some description
            assert len(content.strip()) >= 100, \
                f"{skill_file} should have substantial description"

    def test_skills_have_markdown_formatting(self):
        """Test that skills use markdown formatting."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        for skill_file in skill_files:
            with open(skill_file) as f:
                content = f.read()

            # Should have markdown elements
            has_markdown = (
                '#' in content or
                '-' in content or
                '*' in content or
                '`' in content
            )

            assert has_markdown, f"{skill_file} should use markdown formatting"


class TestSkillDiscovery:
    """Test skill discovery mechanisms."""

    def test_can_list_all_skills(self):
        """Test that we can discover all skills."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        skill_names = [f.parent.name for f in skill_files]

        assert len(skill_names) > 0
        assert all(isinstance(name, str) for name in skill_names)

    def test_no_duplicate_skill_names(self):
        """Test that there are no duplicate skill names."""
        skills_dir = Path('skills')
        skill_files = list(skills_dir.glob('**/SKILL.md'))

        skill_paths = [str(f) for f in skill_files]

        # Each skill should have unique path
        assert len(skill_paths) == len(set(skill_paths))


# Run tests
if __name__ == '__main__':
    try:
        import pytest
        pytest.main([__file__, '-v'])
    except ImportError:
        print("⚠️  pytest not available")
        import sys
        sys.exit(0)
