# Testing & Quality Assurance Expert

**Skill ID:** `testing-expert`
**Version:** 1.0.0
**Category:** Testing, QA, Quality Assurance
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables an AI agent to design and implement comprehensive testing strategies, including unit tests, integration tests, end-to-end tests, performance benchmarks, and test automation frameworks.

### Key Capabilities
- Multi-layered test pyramid implementation
- Test-driven development (TDD) practices
- Continuous testing in CI/CD
- Performance and load testing
- Test coverage analysis and reporting

---

## 🧠 Core Competencies

### 1. Test Pyramid Architecture

#### Unit Tests (Base Layer)
Fast, isolated tests for individual components:
```python
class TestStructureValidator:
    def test_required_directories_defined(self):
        """Test that required directories are properly defined."""
        validator = RepoStructureValidator()
        required_dirs = validator.REQUIRED_STRUCTURE['required_dirs']

        assert len(required_dirs) > 0
        assert isinstance(required_dirs, list)

    def test_validator_tracks_errors(self):
        """Test that validator tracks errors correctly."""
        validator = RepoStructureValidator()
        validator.errors.append("Test error")

        assert len(validator.errors) == 1
```

#### Integration Tests (Middle Layer)
Test component interactions:
```python
def test_validation_workflow(self):
    """Test complete validation workflow."""
    # Run structure validation
    result = subprocess.run(['python3', 'scripts/validate-repo-structure.py'])
    assert result.returncode in [0, 1]

    # Check report generated
    assert Path('structure-health-report.json').exists()
```

#### End-to-End Tests (Top Layer)
Test complete user journeys:
```python
def test_full_validation_pipeline(self):
    """Test running complete validation pipeline."""
    steps = [
        ('Structure validation', 'scripts/validate-repo-structure.py'),
        ('Makefile validation', 'scripts/validate-makefile.sh'),
        ('Health report', 'scripts/generate-structure-report.py'),
    ]

    for step_name, script_path in steps:
        result = run_script(script_path)
        assert result.success, f"{step_name} failed"
```

### 2. Performance Testing

#### Benchmark Tests
Measure execution time and resource usage:
```python
def test_validation_performance(self):
    """Test that validation completes quickly."""
    start_time = time.time()

    run_validation()

    elapsed_time = time.time() - start_time

    # Should complete within 30 seconds
    assert elapsed_time < 30, f"Too slow: {elapsed_time:.2f}s"
```

#### Load Testing
Test system under stress:
```python
def test_concurrent_validation(self):
    """Test multiple validations run concurrently."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_validation) for _ in range(5)]
        results = [f.result() for f in as_completed(futures)]

    assert all(results), "Concurrent tests should pass"
```

### 3. Test Automation

#### CI/CD Integration
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Unit Tests
        run: pytest tests/unit/ -v
      - name: Run Integration Tests
        run: pytest tests/integration/ -v
      - name: Run E2E Tests
        run: pytest tests/e2e/ -v
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

### 4. Test Coverage Analysis

#### Coverage Reporting
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Generate coverage badge
coverage-badge -o coverage.svg

# Set coverage threshold
pytest --cov=. --cov-fail-under=80
```

---

## ✅ Validation Criteria

### Test Quality Metrics
- ✅ Test coverage >= 80%
- ✅ All tests pass consistently
- ✅ No flaky tests
- ✅ Fast execution (<5 min total)
- ✅ Clear test names and documentation

### Test Pyramid Balance
- ✅ 70% unit tests (fast, numerous)
- ✅ 20% integration tests (medium)
- ✅ 10% E2E tests (slow, critical paths)

---

## 🎯 Usage Examples

### Example 1: Write Unit Test
```python
def test_health_report_structure(self):
    """Test that health report has correct structure."""
    reporter = StructureHealthReport()
    report = reporter.generate_report()

    # Check required fields
    assert 'timestamp' in report
    assert 'metrics' in report
    assert 'scores' in report

    # Check metrics structure
    metrics = report['metrics']
    assert 'structure_compliance' in metrics
    assert 'documentation_coverage' in metrics
```

### Example 2: Integration Test
```python
def test_makefile_validate_target(self):
    """Test that 'make validate' target works."""
    result = subprocess.run(
        ['make', '-n', 'validate'],
        capture_output=True
    )

    assert result.returncode == 0
```

### Example 3: Performance Benchmark
```python
def test_memory_usage_reasonable(self):
    """Test validation doesn't use excessive memory."""
    import psutil

    process = subprocess.Popen(['python3', 'scripts/validate-repo-structure.py'])
    p = psutil.Process(process.pid)

    max_memory = max(p.memory_info().rss / 1024 / 1024
                     for _ in range(10))

    # Should use less than 512 MB
    assert max_memory < 512
```

---

## 📊 Success Metrics

### Test Execution
- **Total Test Count**: 50+ tests
- **Execution Time**: <5 minutes
- **Pass Rate**: 100%
- **Coverage**: 80%+

### Quality Indicators
- **Flaky Test Rate**: 0%
- **Test Maintenance**: <10% of dev time
- **Bug Detection**: 95%+ before production

---

## 🔗 Related Skills
- `validation-expert` - Validation frameworks
- `repo-architect-ai-engineer` - Architecture design
- `audit-skill` - Quality auditing

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
