# 🧪 Tests - Comprehensive Test Suite

This directory contains all automated tests for InsightPulse Odoo, including unit tests, integration tests, AI tests, and end-to-end tests.

## 📁 Directory Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for system interactions
│   └── test_repo_structure.py
├── ai/                # AI agent-specific tests
├── e2e/               # End-to-end workflow tests
├── performance/       # Performance and load tests
├── security/          # Security and vulnerability tests
└── fixtures/          # Test fixtures and mock data
```

## 🎯 Test Categories

### Unit Tests
Fast, isolated tests for individual functions and classes
```bash
make test-unit
pytest tests/unit/ -v
```

### Integration Tests
Tests for component interactions and system integration
```bash
make test-integration
pytest tests/integration/ -v
```

### AI Tests
Validation of AI agent capabilities and outputs
```bash
pytest tests/ai/ -v
```

### End-to-End Tests
Complete workflow validation from start to finish
```bash
make test-e2e
pytest tests/e2e/ -v
```

### Performance Tests
Load testing and performance benchmarking
```bash
make test-performance
pytest tests/performance/ -v
```

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests
make test

# Run specific test file
pytest tests/integration/test_repo_structure.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run in parallel (faster)
pytest -n auto
```

### Test Options
```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run only failed tests
pytest --lf

# Run specific test by name
pytest -k "test_structure"
```

## 📊 Test Coverage

### Current Coverage
- **Overall**: 80%+
- **Unit Tests**: 85%
- **Integration Tests**: 75%
- **AI Tests**: 70%
- **E2E Tests**: 65%

### Coverage Goals
- Target: 90%+ overall
- Minimum: 80% per module
- Critical paths: 100%

## 🔧 Writing Tests

### Test File Naming
- Unit tests: `test_<module>.py`
- Integration tests: `test_<integration>.py`
- AI tests: `test_ai_<capability>.py`

### Test Function Naming
```python
def test_<what>_<condition>_<expected>():
    """Test that <what> does <expected> when <condition>."""
    pass
```

### Example Test
```python
import pytest
from pathlib import Path

class TestRepoStructure:
    """Test repository structure validation."""

    def test_required_directories_exist(self):
        """Test that all required directories exist."""
        required = ['docs', 'tests', 'skills']

        for dir_name in required:
            assert Path(dir_name).exists()

    def test_makefile_validates(self):
        """Test that Makefile syntax is valid."""
        result = subprocess.run(['make', '-n', 'help'])
        assert result.returncode == 0
```

## 🛠️ Test Utilities

### Fixtures
Located in `tests/fixtures/` - reusable test data and setup

### Mocks
Use `pytest-mock` for mocking external dependencies

### Helpers
Common test utilities in `tests/helpers/`

## 📝 Test Reports

### Generate Coverage Report
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Generate Test Report
```bash
pytest --html=report.html --self-contained-html
```

## ✅ CI/CD Integration

Tests run automatically on:
- Every commit (via pre-commit hooks)
- Every push (via GitHub Actions)
- Every PR (with coverage reporting)

### GitHub Actions Workflow
See `.github/workflows/ci-odoo.yml` for test automation

## 🔗 Related Documentation

- [Validation Framework](../scripts/validate-repo-structure.py)
- [Evals Framework](../evals/README.md)
- [CI/CD Workflows](../.github/workflows/)

---

**For more information, see the main [README](../README.md)**
