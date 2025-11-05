#!/usr/bin/env python3

"""
End-to-end tests for validation workflow.
"""

import subprocess
from pathlib import Path
import sys


class TestValidationWorkflow:
    """Test complete validation workflow end-to-end."""

    def test_structure_validation_runs(self):
        """Test that structure validation script runs successfully."""
        script = Path('scripts/validate-repo-structure.py')

        if not script.exists():
            print(f"⚠️  Script not found: {script}")
            return

        result = subprocess.run(
            ['python3', str(script)],
            capture_output=True,
            text=True
        )

        # Should execute (may have validation errors, but shouldn't crash)
        assert result.returncode in [0, 1], "Script should execute without crashing"

    def test_makefile_validation_runs(self):
        """Test that Makefile validation runs successfully."""
        script = Path('scripts/validate-makefile.sh')

        if not script.exists():
            print(f"⚠️  Script not found: {script}")
            return

        result = subprocess.run(
            ['bash', str(script)],
            capture_output=True,
            text=True
        )

        # Should execute
        assert result.returncode in [0, 1], "Script should execute without crashing"

    def test_health_report_generation(self):
        """Test that health report generates successfully."""
        script = Path('scripts/generate-structure-report.py')

        if not script.exists():
            print(f"⚠️  Script not found: {script}")
            return

        result = subprocess.run(
            ['python3', str(script)],
            capture_output=True,
            text=True
        )

        # Should execute successfully
        assert result.returncode == 0, f"Health report should generate: {result.stderr}"

        # Should create report file
        report_file = Path('structure-health-report.json')
        assert report_file.exists(), "Report file should be created"

    def test_integration_tests_run(self):
        """Test that integration tests execute."""
        test_file = Path('tests/integration/test_repo_structure.py')

        if not test_file.exists():
            print(f"⚠️  Test file not found: {test_file}")
            return

        result = subprocess.run(
            ['python3', str(test_file)],
            capture_output=True,
            text=True
        )

        # Should execute (may have test failures)
        assert result.returncode in [0, 1], "Tests should execute"

    def test_makefile_validate_target(self):
        """Test that 'make validate' target works."""
        result = subprocess.run(
            ['make', '-n', 'validate'],
            capture_output=True,
            text=True
        )

        # Should be able to dry-run
        assert result.returncode == 0, "make validate should be defined"

    def test_makefile_health_report_target(self):
        """Test that 'make health-report' target works."""
        result = subprocess.run(
            ['make', '-n', 'health-report'],
            capture_output=True,
            text=True
        )

        # Should be able to dry-run
        assert result.returncode == 0, "make health-report should be defined"


class TestCompleteValidationPipeline:
    """Test the complete validation pipeline."""

    def test_full_validation_pipeline(self):
        """Test running complete validation pipeline."""

        steps = [
            ('Structure validation', 'scripts/validate-repo-structure.py'),
            ('Makefile validation', 'scripts/validate-makefile.sh'),
            ('Health report', 'scripts/generate-structure-report.py'),
        ]

        results = []

        for step_name, script_path in steps:
            script = Path(script_path)

            if not script.exists():
                print(f"⚠️  {step_name}: Script not found")
                continue

            if script.suffix == '.py':
                result = subprocess.run(['python3', str(script)], capture_output=True)
            else:
                result = subprocess.run(['bash', str(script)], capture_output=True)

            results.append({
                'step': step_name,
                'success': result.returncode in [0, 1]
            })

        # All steps should execute
        assert all(r['success'] for r in results), \
            f"All pipeline steps should execute: {results}"

    def test_validation_produces_report(self):
        """Test that validation produces a health report."""

        # Run health report generation
        subprocess.run(
            ['python3', 'scripts/generate-structure-report.py'],
            capture_output=True
        )

        # Check report exists
        report = Path('structure-health-report.json')
        assert report.exists(), "Validation should produce health report"

        # Check report has content
        assert report.stat().st_size > 0, "Report should not be empty"


# Run tests
if __name__ == '__main__':
    try:
        import pytest
        pytest.main([__file__, '-v'])
    except ImportError:
        print("⚠️  pytest not available, running basic tests...")

        test_workflow = TestValidationWorkflow()
        test_pipeline = TestCompleteValidationPipeline()

        tests = [
            ('Structure validation runs', test_workflow.test_structure_validation_runs),
            ('Makefile validation runs', test_workflow.test_makefile_validation_runs),
            ('Health report generation', test_workflow.test_health_report_generation),
            ('Integration tests run', test_workflow.test_integration_tests_run),
            ('Make validate target', test_workflow.test_makefile_validate_target),
            ('Make health-report target', test_workflow.test_makefile_health_report_target),
            ('Full validation pipeline', test_pipeline.test_full_validation_pipeline),
            ('Validation produces report', test_pipeline.test_validation_produces_report),
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
