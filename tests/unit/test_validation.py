#!/usr/bin/env python3

"""
Unit tests for validation framework.
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestStructureValidator:
    """Test structure validation logic."""

    def test_required_directories_defined(self):
        """Test that required directories are properly defined."""
        from scripts.validate_repo_structure import RepoStructureValidator

        validator = RepoStructureValidator()
        required_dirs = validator.REQUIRED_STRUCTURE['required_dirs']

        assert len(required_dirs) > 0, "Should have required directories"
        assert isinstance(required_dirs, list), "Should be a list"

    def test_required_files_defined(self):
        """Test that required files are properly defined."""
        from scripts.validate_repo_structure import RepoStructureValidator

        validator = RepoStructureValidator()
        required_files = validator.REQUIRED_STRUCTURE['required_files']

        assert len(required_files) > 0, "Should have required files"
        assert isinstance(required_files, list), "Should be a list"

    def test_forbidden_patterns_defined(self):
        """Test that forbidden patterns are defined."""
        from scripts.validate_repo_structure import RepoStructureValidator

        validator = RepoStructureValidator()
        forbidden = validator.REQUIRED_STRUCTURE['forbidden_patterns']

        assert len(forbidden) > 0, "Should have forbidden patterns"
        assert '__pycache__' in str(forbidden), "Should forbid __pycache__"

    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        from scripts.validate_repo_structure import RepoStructureValidator

        validator = RepoStructureValidator()

        assert validator.errors == []
        assert validator.warnings == []
        assert validator.info == []

    def test_validator_tracks_errors(self):
        """Test that validator tracks errors correctly."""
        from scripts.validate_repo_structure import RepoStructureValidator

        validator = RepoStructureValidator()
        validator.errors.append("Test error")

        assert len(validator.errors) == 1
        assert "Test error" in validator.errors


class TestHealthReport:
    """Test health report generation."""

    def test_report_generator_initialization(self):
        """Test report generator initializes."""
        from scripts.generate_structure_report import StructureHealthReport

        reporter = StructureHealthReport()
        assert reporter.repo_path.exists()

    def test_report_has_required_sections(self):
        """Test generated report has required sections."""
        from scripts.generate_structure_report import StructureHealthReport

        reporter = StructureHealthReport()
        report = reporter.generate_report()

        assert 'timestamp' in report
        assert 'metrics' in report
        assert 'repository' in report

    def test_report_metrics_structure(self):
        """Test report metrics have correct structure."""
        from scripts.generate_structure_report import StructureHealthReport

        reporter = StructureHealthReport()
        report = reporter.generate_report()

        metrics = report['metrics']

        assert 'structure_compliance' in metrics
        assert 'documentation_coverage' in metrics
        assert 'test_coverage' in metrics
        assert 'skill_maturity' in metrics
        assert 'automation_level' in metrics

    def test_grade_calculation(self):
        """Test grade calculation logic."""
        from scripts.generate_structure_report import StructureHealthReport

        reporter = StructureHealthReport()

        assert reporter.get_grade(95) == 'A'
        assert reporter.get_grade(85) == 'B'
        assert reporter.get_grade(75) == 'C'
        assert reporter.get_grade(65) == 'D'
        assert reporter.get_grade(55) == 'F'

    def test_structure_compliance_calculation(self):
        """Test structure compliance is calculated correctly."""
        from scripts.generate_structure_report import StructureHealthReport

        reporter = StructureHealthReport()
        compliance = reporter.check_structure_compliance()

        assert 'directories' in compliance
        assert 'files' in compliance
        assert 'overall_percentage' in compliance

        assert compliance['directories']['percentage'] >= 0
        assert compliance['directories']['percentage'] <= 100


class TestFileValidation:
    """Test file validation logic."""

    def test_yaml_validation(self):
        """Test YAML file validation."""
        import yaml
        import tempfile

        # Valid YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("key: value\n")
            f.flush()

            with open(f.name) as test_file:
                data = yaml.safe_load(test_file)
                assert data == {'key': 'value'}

    def test_json_validation(self):
        """Test JSON file validation."""
        import json
        import tempfile

        # Valid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'key': 'value'}, f)
            f.flush()

            with open(f.name) as test_file:
                data = json.load(test_file)
                assert data == {'key': 'value'}

    def test_python_syntax_validation(self):
        """Test Python syntax validation."""
        import ast
        import tempfile

        # Valid Python
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n    pass\n")
            f.flush()

            with open(f.name) as test_file:
                code = test_file.read()
                ast.parse(code)  # Should not raise


# Run tests with pytest if available
if __name__ == '__main__':
    try:
        import pytest
        pytest.main([__file__, '-v'])
    except ImportError:
        print("⚠️  pytest not available, running basic tests...")

        # Run tests manually
        test_validator = TestStructureValidator()
        test_health = TestHealthReport()
        test_files = TestFileValidation()

        tests = [
            ('Required directories defined', test_validator.test_required_directories_defined),
            ('Required files defined', test_validator.test_required_files_defined),
            ('Forbidden patterns defined', test_validator.test_forbidden_patterns_defined),
            ('Validator initialization', test_validator.test_validator_initialization),
            ('Validator tracks errors', test_validator.test_validator_tracks_errors),
            ('Report generator init', test_health.test_report_generator_initialization),
            ('Report structure', test_health.test_report_has_required_sections),
            ('Metrics structure', test_health.test_report_metrics_structure),
            ('Grade calculation', test_health.test_grade_calculation),
            ('Structure compliance', test_health.test_structure_compliance_calculation),
            ('YAML validation', test_files.test_yaml_validation),
            ('JSON validation', test_files.test_json_validation),
            ('Python validation', test_files.test_python_syntax_validation),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                test_func()
                print(f"✅ {name}")
                passed += 1
            except Exception as e:
                print(f"❌ {name}: {e}")
                failed += 1

        print(f"\nResults: {passed} passed, {failed} failed")
        sys.exit(0 if failed == 0 else 1)
