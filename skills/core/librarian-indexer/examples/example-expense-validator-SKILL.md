# Expense Validator Specialist

**Skill ID:** `expense-validator-specialist`
**Version:** 1.0.0
**Category:** Expense Management
**Expertise Level:** Advanced
**Last Updated:** 2025-11-05
**Source Module:** custom/expense_management/expense_validator.py

---

## 🎯 Purpose

This skill was auto-generated from code analysis and provides expertise in expense validator specialist.

This module handles validation of expense claims, policy compliance checking, and approval workflow management. It ensures all expense submissions meet company policy requirements before processing.

---

## 📚 Core Competencies

### Key Capabilities

1. Validate expense claims against company policies
2. Check receipt requirements and documentation
3. Enforce spending limits and approval thresholds
4. Detect duplicate submissions and fraudulent claims
5. Integrate with approval workflow engine
6. Generate validation reports and audit trails

### Technical Skills

**Functions & Methods:**
- `validate_expense_claim(claim_id, policy_id)` - Validates a single expense claim against policy rules
- `check_receipt_requirements(claim)` - Verifies receipt documentation meets requirements
- `detect_duplicates(claim, lookback_days)` - Checks for duplicate expense submissions
- `enforce_spending_limits(employee, amount, category)` - Validates against spending limits
- `calculate_approval_threshold(claim)` - Determines required approval level

**Classes & Components:**
- `ExpenseValidator` - Main validation orchestrator
  Methods:
  - `validate(claim, context)`
  - `run_policy_checks(claim, policy)`
  - `generate_validation_report(results)`

- `PolicyEngine` - Policy rule evaluation engine
  Methods:
  - `load_policies(company_id)`
  - `evaluate_rules(claim, rules)`
  - `check_compliance(claim, policy)`

- `ValidationResult` - Validation result data class
  Methods:
  - `to_dict()`
  - `add_error(code, message)`
  - `add_warning(code, message)`

---

## 🛠️ Tools & Technologies

### Required Libraries

- `odoo` - Odoo framework core
- `datetime` - Date and time operations
- `decimal` - Precise monetary calculations
- `re` - Regular expression matching
- `logging` - Validation logging

### Development Environment

- **Language:** Python 3.9+
- **Framework:** Odoo 19.0
- **Testing:** pytest, unittest
- **Code Quality:** pylint, flake8, black

---

## 🎓 Competency Validation

### Self-Assessment Checklist

**Module Complexity:** 12.4 (High)

#### Function Implementation (5 functions)
- [ ] Can implement `validate_expense_claim()` with complexity 14
- [ ] Can implement `check_receipt_requirements()` with complexity 8
- [ ] Can implement `detect_duplicates()` with complexity 11
- [ ] Can implement `enforce_spending_limits()` with complexity 9
- [ ] Can implement `calculate_approval_threshold()` with complexity 6

#### Class Design (3 classes)
- [ ] Can design and implement `ExpenseValidator` class
- [ ] Can design and implement `PolicyEngine` class
- [ ] Can design and implement `ValidationResult` class

#### Code Quality Standards
- [ ] Can maintain cyclomatic complexity < 10
- [ ] Can write comprehensive docstrings
- [ ] Can implement error handling
- [ ] Can write unit tests with >80% coverage
- [ ] Can follow PEP 8 style guidelines

---

## 💼 Usage Examples

### Example: Using validate_expense_claim

```python
from custom.expense_management.expense_validator import ExpenseValidator

# Initialize
instance = ExpenseValidator()

# Call function
result = validate_expense_claim(claim_id=123, policy_id=456)
print(result)
```

### Example: Complete Validation Workflow

```python
from custom.expense_management.expense_validator import ExpenseValidator, PolicyEngine

# Initialize components
validator = ExpenseValidator(env)
policy_engine = PolicyEngine(env)

# Load company policies
policies = policy_engine.load_policies(company_id=1)

# Validate expense claim
claim = env['expense.claim'].browse(123)
context = {'user_id': env.user.id, 'company_id': 1}

validation_result = validator.validate(claim, context)

if validation_result.is_valid:
    print("✅ Expense claim is valid")
    claim.action_approve()
else:
    print("❌ Validation failed:")
    for error in validation_result.errors:
        print(f"  - {error['message']}")
```

### Example: Duplicate Detection

```python
# Check for duplicate expenses in last 90 days
duplicate_results = validator.detect_duplicates(
    claim=claim,
    lookback_days=90
)

if duplicate_results:
    print(f"⚠️  Found {len(duplicate_results)} potential duplicates")
    for dup in duplicate_results:
        print(f"  - Claim #{dup.id} on {dup.date} for ${dup.amount}")
```

---

## 📖 Learning Resources

### Documentation
- [Python Official Docs](https://docs.python.org/3/)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [OCA Guidelines](https://odoo-community.org/)

### Recommended Reading
- Clean Code by Robert C. Martin
- The Pragmatic Programmer by Hunt & Thomas
- Odoo Development Essentials
- *Domain-Driven Design* by Eric Evans (for validation patterns)

### Online Courses
- Python Best Practices on Pluralsight
- Software Architecture Patterns on Udemy
- Odoo Development Course on Udemy

---

## 📊 Success Metrics

### Code Quality Targets
- **Cyclomatic Complexity:** < 10
- **Maintainability Index:** > 65
- **Test Coverage:** > 80%
- **Documentation Coverage:** 100%

### Performance Targets
- **Validation Time (P95):** < 500ms per claim
- **Throughput:** > 50 validations/sec
- **False Positive Rate:** < 2%
- **False Negative Rate:** < 0.1% (critical)

### Functional Requirements
- All validation rules properly enforced
- Receipt requirements checked accurately
- Duplicate detection with 98%+ accuracy
- Spending limits enforced correctly
- Approval thresholds calculated properly
- Audit trail complete and tamper-proof

---

## 🔗 Related Skills

### Prerequisites
- `python-best-practices` - Python coding standards
- `testing-strategies` - Unit testing and TDD
- `code-review` - Code quality and review practices
- `odoo-module-development` - Odoo module structure
- `oca-compliance` - OCA guidelines adherence

### Related Skills
- `expense-policy-management` - Policy configuration and management
- `expense-approval-workflow` - Approval routing and escalation
- `receipt-ocr-processing` - Automated receipt data extraction
- `expense-fraud-detection` - Advanced fraud detection algorithms
- `expense-reporting-analytics` - Expense reporting and analytics

---

## 📝 Auto-Generation Metadata

**Generated:** 2025-11-05T10:30:00
**Source File:** `custom/expense_management/expense_validator.py`
**Analysis Tool:** librarian-indexer v1.0.0

**Patterns Detected:**
- Validator Pattern
- Strategy Pattern (multiple validation strategies)
- Factory Pattern (validation rule creation)
- Builder Pattern (validation result construction)

**Metrics:**
- Lines of Code: 487
- Functions: 5
- Classes: 3
- Average Complexity: 12.4

---

**Note:** This skill was auto-generated from code analysis. Please review and enhance with domain-specific knowledge and best practices.
