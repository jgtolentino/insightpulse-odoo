#!/usr/bin/env python3

"""
Performance benchmarks for validation framework.
"""

import time
import subprocess
from pathlib import Path


class TestValidationPerformance:
    """Test performance of validation scripts."""

    def test_structure_validation_performance(self):
        """Test that structure validation completes in reasonable time."""
        script = Path('scripts/validate-repo-structure.py')

        if not script.exists():
            print("⚠️  Script not found, skipping")
            return

        start_time = time.time()

        result = subprocess.run(
            ['python3', str(script)],
            capture_output=True,
            timeout=60  # 60 second timeout
        )

        elapsed_time = time.time() - start_time

        print(f"Structure validation took {elapsed_time:.2f}s")

        # Should complete within 30 seconds
        assert elapsed_time < 30, f"Validation too slow: {elapsed_time:.2f}s"

    def test_health_report_performance(self):
        """Test that health report generates quickly."""
        script = Path('scripts/generate-structure-report.py')

        if not script.exists():
            print("⚠️  Script not found, skipping")
            return

        start_time = time.time()

        result = subprocess.run(
            ['python3', str(script)],
            capture_output=True,
            timeout=30  # 30 second timeout
        )

        elapsed_time = time.time() - start_time

        print(f"Health report generation took {elapsed_time:.2f}s")

        # Should complete within 15 seconds
        assert elapsed_time < 15, f"Report generation too slow: {elapsed_time:.2f}s"

    def test_makefile_validation_performance(self):
        """Test that Makefile validation is fast."""
        script = Path('scripts/validate-makefile.sh')

        if not script.exists():
            print("⚠️  Script not found, skipping")
            return

        start_time = time.time()

        result = subprocess.run(
            ['bash', str(script)],
            capture_output=True,
            timeout=10  # 10 second timeout
        )

        elapsed_time = time.time() - start_time

        print(f"Makefile validation took {elapsed_time:.2f}s")

        # Should complete within 5 seconds
        assert elapsed_time < 5, f"Makefile validation too slow: {elapsed_time:.2f}s"


class TestResourceUsage:
    """Test resource usage of validation scripts."""

    def test_memory_usage_reasonable(self):
        """Test that validation doesn't use excessive memory."""
        import psutil
        import os

        script = Path('scripts/validate-repo-structure.py')

        if not script.exists():
            print("⚠️  Script not found, skipping")
            return

        process = subprocess.Popen(
            ['python3', str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            # Monitor memory usage
            p = psutil.Process(process.pid)
            max_memory = 0

            while process.poll() is None:
                try:
                    mem_info = p.memory_info()
                    memory_mb = mem_info.rss / 1024 / 1024
                    max_memory = max(max_memory, memory_mb)
                except:
                    pass
                time.sleep(0.1)

            process.wait(timeout=30)

            print(f"Max memory usage: {max_memory:.2f} MB")

            # Should use less than 512 MB
            assert max_memory < 512, f"Memory usage too high: {max_memory:.2f} MB"

        except subprocess.TimeoutExpired:
            process.kill()
            raise


class TestScalability:
    """Test scalability of validation framework."""

    def test_handles_large_repository(self):
        """Test that validation handles large repositories."""
        # This is a placeholder - in reality would test with large repo
        script = Path('scripts/validate-repo-structure.py')

        if not script.exists():
            return

        # Just ensure it completes
        result = subprocess.run(
            ['python3', str(script)],
            capture_output=True,
            timeout=60
        )

        # Should complete
        assert result.returncode in [0, 1]

    def test_concurrent_validation(self):
        """Test that multiple validations can run concurrently."""
        import concurrent.futures

        script = Path('scripts/generate-structure-report.py')

        if not script.exists():
            return

        def run_validation():
            result = subprocess.run(
                ['python3', str(script)],
                capture_output=True,
                timeout=30
            )
            return result.returncode in [0, 1]

        # Run 3 validations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_validation) for _ in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(results), "Concurrent validations should succeed"


# Run tests
if __name__ == '__main__':
    try:
        import pytest
        pytest.main([__file__, '-v'])
    except ImportError:
        print("⚠️  pytest not available, running basic tests...")
        import sys

        test_perf = TestValidationPerformance()
        test_resource = TestResourceUsage()
        test_scale = TestScalability()

        tests = [
            ('Structure validation performance', test_perf.test_structure_validation_performance),
            ('Health report performance', test_perf.test_health_report_performance),
            ('Makefile validation performance', test_perf.test_makefile_validation_performance),
            ('Memory usage', test_resource.test_memory_usage_reasonable),
            ('Large repository handling', test_scale.test_handles_large_repository),
            ('Concurrent validation', test_scale.test_concurrent_validation),
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
