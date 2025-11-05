# Repository Validation & Verification Expert

**Skill ID:** `validation-expert`
**Version:** 1.0.0
**Category:** Quality Assurance, Testing, Validation
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables an AI agent to design, implement, and maintain comprehensive repository validation frameworks, including structure validation, code quality checks, automated testing, and health monitoring.

### Key Capabilities
- Multi-level validation pyramids (static, functional, integration, metrics)
- Health scoring and grading systems
- Automated remediation and self-healing
- Continuous validation in CI/CD pipelines
- Metrics-driven quality improvement

---

## 🧠 Core Competencies

### 1. Validation Framework Design

#### Structure Validation
Design validators that check:
- Directory structure compliance
- Required files existence
- Naming conventions
- Forbidden patterns
- File syntax (YAML, JSON, Python)

**Example Implementation:**
```python
class StructureValidator:
    def validate_directories(self):
        """Check required directories exist."""
        for dir_path in self.required_dirs:
            if not Path(dir_path).exists():
                self.errors.append(f"Missing: {dir_path}")

    def validate_syntax(self):
        """Validate file syntax."""
        for yaml_file in self.repo.glob('**/*.yml'):
            try:
                yaml.safe_load(yaml_file.read_text())
            except Exception as e:
                self.errors.append(f"Invalid YAML: {yaml_file}")
```

### 2. Health Metrics & KPIs

#### Scoring System
Calculate health scores across dimensions:
- **Structure Compliance**: Directory/file completeness
- **Documentation Coverage**: README files, code docs
- **Test Coverage**: Unit, integration, E2E tests
- **Skills Maturity**: Complete, well-documented skills
- **Automation Level**: CI/CD workflows, scripts

**Example:**
```python
def calculate_score(metrics):
    weights = {
        'structure': 0.3,
        'documentation': 0.2,
        'testing': 0.2,
        'skills': 0.15,
        'automation': 0.15
    }
    return sum(metrics[k] * weights[k] for k in weights)
```

### 3. Integration Testing

#### End-to-End Validation
Test complete workflows:
```python
def test_full_validation_pipeline(self):
    # Run all validation steps
    structure_valid = run_structure_validation()
    makefile_valid = run_makefile_validation()
    tests_pass = run_integration_tests()
    report_generated = generate_health_report()

    assert all([structure_valid, makefile_valid,
                tests_pass, report_generated])
```

### 4. Automated Reporting

#### Health Report Generation
Generate comprehensive reports with:
- Overall score and grade
- Individual metric scores
- Detailed breakdowns
- Actionable recommendations
- Historical trends

---

## ✅ Validation Criteria

### Framework Quality
- ✅ Detects 95%+ of structure violations
- ✅ Zero false positives
- ✅ Completes in <30 seconds
- ✅ Generates actionable reports
- ✅ Integrates with CI/CD

### Test Coverage
- ✅ Unit tests for validators
- ✅ Integration tests for workflows
- ✅ Performance benchmarks
- ✅ Edge case handling

---

## 🎯 Usage Examples

### Example 1: Validate Repository Structure
```bash
# Run structure validation
python scripts/validate-repo-structure.py

# Output:
📁 Checking required directories...
   Found 13 of 13 required directories

📄 Checking required files...
   Found 11 required files

✅ VALIDATION PASSED
```

### Example 2: Generate Health Report
```bash
# Generate comprehensive health report
python scripts/generate-structure-report.py

# Output:
Overall Score: 92.3% (Grade: A)

Individual Scores:
  Structure       ████████████████████ 100.0%
  Documentation   ████████████████████ 100.0%
  Testing         ████████████████░░░░  85.0%
  Skills          ██████████████░░░░░░  75.0%
  Automation      ████████████████████ 100.0%
```

### Example 3: CI/CD Integration
```yaml
# .github/workflows/validate.yml
name: Validate Structure

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Validation
        run: ./scripts/validate-all.sh
      - name: Generate Report
        run: python scripts/generate-structure-report.py
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: health-report
          path: structure-health-report.json
```

---

## 📊 Success Metrics

### Validation Effectiveness
- **Detection Rate**: 99%+
- **False Positive Rate**: <1%
- **Execution Time**: <30s
- **Report Generation**: <10s

### Quality Improvement
- **Structure Score**: 90%+ target
- **Documentation**: 80%+ coverage
- **Test Coverage**: 80%+ minimum
- **Overall Grade**: A (90%+)

---

## 🔗 Related Skills
- `repo-architect-ai-engineer` - Repository design
- `odoo-agile-scrum-devops` - Development workflows
- `audit-skill` - Comprehensive auditing

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
