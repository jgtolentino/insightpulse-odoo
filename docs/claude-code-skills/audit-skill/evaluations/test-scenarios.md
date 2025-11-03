# Audit Skill Test Scenarios

Test scenarios to validate the audit skill's effectiveness.

## Scenario 1: Security Audit - Hardcoded Credentials

**Setup**:
```python
# test_module/models/config.py
class Config(models.Model):
    _name = 'test.config'
    
    def connect_to_api(self):
        API_KEY = "sk-1234567890abcdef"  # Hardcoded secret
        response = requests.post(
            "https://api.example.com/data",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()
```

**Expected Findings**:
- 🔴 Critical: Hardcoded API key on line 6
- CVSS: 9.8
- Recommendation: Move to environment variable

**Audit Command**:
```bash
grep -rn "API_KEY\s*=\s*['\"]sk-" test_module/ --include="*.py"
```

**Expected Output**:
```
test_module/models/config.py:6:        API_KEY = "sk-1234567890abcdef"
```

**Pass Criteria**: Audit skill correctly identifies and reports the hardcoded credential with appropriate severity.

---

## Scenario 2: Module Structure - Missing Security Rules

**Setup**:
```
test_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py  # Has model definition
└── views/
    └── my_views.xml
# Note: Missing security/ directory
```

**Expected Findings**:
- ❌ Critical: No security directory found
- ❌ Critical: No ir.model.access.csv file
- Risk: Unrestricted access to model data

**Audit Command**:
```bash
python3 audit-skill/reference/module-audit-validator.py test_module/
```

**Expected Output**:
```
❌ test_module
   ERROR: Has models but missing security/ directory
   ERROR: Missing required file: security/ir.model.access.csv
```

**Pass Criteria**: Audit skill detects missing security configuration and flags as critical.

---

## Scenario 3: SQL Injection Vulnerability

**Setup**:
```python
# test_module/models/report.py
class Report(models.Model):
    _name = 'test.report'
    
    def get_sales_data(self, user_id):
        # Vulnerable to SQL injection
        query = f"SELECT * FROM sales WHERE user_id = {user_id}"
        self.env.cr.execute(query)
        return self.env.cr.fetchall()
```

**Expected Findings**:
- 🔴 Critical: SQL injection vulnerability
- Location: models/report.py:7
- CVSS: 9.1
- Issue: Unsanitized user input in SQL query
- Fix: Use parameterized queries or ORM

**Audit Command**:
```bash
# Check for SQL injection patterns
grep -rn "\.execute.*%\|\.execute.*format\|\.execute.*f\"" test_module/ --include="*.py"
```

**Expected Output**:
```
test_module/models/report.py:7:        self.env.cr.execute(query)
```

**Pass Criteria**: Audit skill identifies SQL injection risk and recommends parameterized queries.

---

## Scenario 4: File Upload Without Validation

**Setup**:
```python
# test_module/models/document.py
class Document(models.Model):
    _name = 'test.document'
    
    file = fields.Binary(string='File', attachment=True)
    # No file type validation
```

**Expected Findings**:
- 🟠 High: File upload without validation
- Location: models/document.py:5
- CVSS: 7.5
- Risk: Malicious file upload, disk space abuse
- Fix: Add MIME type validation and file size limits

**Audit Command**:
```bash
# Check for Binary fields without constraints
grep -A 5 "fields.Binary" test_module/models/*.py | grep -v "@api.constrains"
```

**Expected Output**:
```
test_module/models/document.py:5:    file = fields.Binary(string='File', attachment=True)
```

**Pass Criteria**: Audit skill detects unvalidated file uploads.

---

## Scenario 5: Missing Test Coverage

**Setup**:
```
test_module/
├── __init__.py
├── __manifest__.py
├── models/
│   └── complex_model.py  # 500 lines of business logic
└── views/
    └── views.xml
# Note: No tests/ directory
```

**Expected Findings**:
- ⚠️  Warning: No tests directory
- Recommendation: Add unit tests for business logic
- OCA Requirement: Test coverage for new features

**Audit Command**:
```bash
[ -d "test_module/tests" ] || echo "⚠️  No tests directory found"
```

**Expected Output**:
```
⚠️  No tests directory found
```

**Pass Criteria**: Audit skill recommends adding tests.

---

## Scenario 6: XSS Vulnerability in View

**Setup**:
```xml
<!-- test_module/views/form.xml -->
<odoo>
    <record id="view_form" model="ir.ui.view">
        <field name="name">test.form</field>
        <field name="model">test.model</field>
        <field name="arch" type="xml">
            <form>
                <!-- Vulnerable: Using t-raw with user input -->
                <div t-raw="object.user_comment"/>
            </form>
        </field>
    </record>
</odoo>
```

**Expected Findings**:
- 🟠 High: XSS vulnerability via t-raw
- Location: views/form.xml:9
- CVSS: 7.2
- Risk: Script injection through user comments
- Fix: Use t-esc instead of t-raw, or sanitize HTML

**Audit Command**:
```bash
grep -rn "t-raw" test_module/views/ --include="*.xml"
```

**Expected Output**:
```
test_module/views/form.xml:9:                <div t-raw="object.user_comment"/>
```

**Pass Criteria**: Audit skill detects XSS risk from t-raw usage.

---

## Scenario 7: Weak Encryption Implementation

**Setup**:
```python
# test_module/models/encryption.py
from cryptography.fernet import Fernet

class SecureData(models.Model):
    _name = 'test.secure.data'
    
    @staticmethod
    def get_key():
        # Weak: Hardcoded encryption key
        return b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
    
    def encrypt_data(self, data):
        fernet = Fernet(self.get_key())
        return fernet.encrypt(data.encode())
```

**Expected Findings**:
- 🔴 Critical: Hardcoded encryption key
- Location: models/encryption.py:9
- CVSS: 8.8
- Issue: Same key used across all installations
- Fix: Generate unique key per installation, store securely

**Audit Command**:
```bash
grep -rn "Fernet\|AES\|DES" test_module/ --include="*.py" -A 5 | grep "b'"
```

**Expected Output**:
```
test_module/models/encryption.py:9:        return b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
```

**Pass Criteria**: Audit skill identifies weak encryption practices.

---

## Scenario 8: Missing Access Control

**Setup**:
```python
# test_module/models/sensitive.py
class SensitiveData(models.Model):
    _name = 'test.sensitive'
    _description = 'Sensitive Data'
    
    ssn = fields.Char(string='Social Security Number')
    salary = fields.Float(string='Salary')
    # No record rules defined
```

```csv
# test_module/security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sensitive_all,test.sensitive.all,model_test_sensitive,,1,1,1,1
# Everyone has full access!
```

**Expected Findings**:
- 🔴 Critical: Sensitive data accessible to all users
- Location: security/ir.model.access.csv:2
- Issue: No group restriction on sensitive model
- Fix: Restrict access to appropriate groups, add record rules

**Audit Command**:
```bash
# Check for access rules with empty group_id
grep ",,1,1,1,1" test_module/security/ir.model.access.csv
```

**Expected Output**:
```
access_sensitive_all,test.sensitive.all,model_test_sensitive,,1,1,1,1
```

**Pass Criteria**: Audit skill detects overly permissive access rules.

---

## Scenario 9: Performance Issue - Missing Index

**Setup**:
```python
# test_module/models/transaction.py
class Transaction(models.Model):
    _name = 'test.transaction'
    _description = 'Transaction'
    
    reference = fields.Char(string='Reference')  # No index
    date = fields.Date(string='Date')  # No index
    
    def find_by_reference(self, ref):
        # Frequent search without index
        return self.search([('reference', '=', ref)])
```

**Expected Findings**:
- 🟡 Medium: Missing database index on frequently searched field
- Location: models/transaction.py:6
- Impact: Slow queries as data grows
- Fix: Add `index=True` to reference and date fields

**Audit Command**:
```bash
# Find Char fields without index in models with search operations
grep -rn "fields.Char\|fields.Date" test_module/models/ | grep -v "index=True"
```

**Expected Output**:
```
test_module/models/transaction.py:6:    reference = fields.Char(string='Reference')
test_module/models/transaction.py:7:    date = fields.Date(string='Date')
```

**Pass Criteria**: Audit skill recommends adding indexes.

---

## Scenario 10: License Compliance Issue

**Setup**:
```python
# test_module/__manifest__.py
{
    'name': 'Test Module',
    'version': '19.0.1.0.0',
    'license': 'Proprietary',  # Not OCA-compatible
    'depends': ['base'],
}
```

```python
# test_module/models/borrowed_code.py
# Code copied from GPL-3 licensed project without attribution
```

**Expected Findings**:
- ⚠️  Warning: Non-standard license (Proprietary)
- ⚠️  Warning: Potential license incompatibility with OCA
- Recommendation: Change to LGPL-3 or AGPL-3 for OCA submission

**Audit Command**:
```bash
grep -rn "'license':" test_module/__manifest__.py
```

**Expected Output**:
```
test_module/__manifest__.py:4:    'license': 'Proprietary',
```

**Pass Criteria**: Audit skill identifies license compatibility issues.

---

## Scenario 11: Insecure External API Call

**Setup**:
```python
# test_module/models/api_client.py
import requests

class APIClient(models.Model):
    _name = 'test.api.client'
    
    def call_external_api(self, data):
        response = requests.post(
            "https://api.example.com/data",
            json=data,
            verify=False,  # Disables SSL verification!
            timeout=None   # No timeout!
        )
        return response.json()
```

**Expected Findings**:
- 🔴 Critical: SSL verification disabled
- Location: models/api_client.py:10
- CVSS: 8.1
- Issue: Man-in-the-middle attack possible
- Fix: Remove `verify=False`, enable SSL verification

- 🟡 Medium: No timeout configured
- Issue: Request can hang indefinitely
- Fix: Add reasonable timeout (e.g., 30 seconds)

**Audit Command**:
```bash
grep -rn "verify=False\|timeout=None" test_module/ --include="*.py"
```

**Expected Output**:
```
test_module/models/api_client.py:10:            verify=False,
test_module/models/api_client.py:11:            timeout=None
```

**Pass Criteria**: Audit skill detects insecure API configurations.

---

## Scenario 12: Insufficient Error Handling

**Setup**:
```python
# test_module/models/processor.py
class Processor(models.Model):
    _name = 'test.processor'
    
    def process_payment(self, amount):
        # No try-except block
        payment_api.charge(amount)
        self.write({'state': 'paid'})
        return True
```

**Expected Findings**:
- 🟡 Medium: No error handling for external API call
- Location: models/processor.py:6
- Risk: Unhandled exceptions, inconsistent state
- Fix: Add try-except with proper logging and rollback

**Recommended Fix**:
```python
def process_payment(self, amount):
    try:
        payment_api.charge(amount)
        self.write({'state': 'paid'})
        return True
    except PaymentError as e:
        _logger.error(f"Payment failed: {e}")
        self.write({'state': 'failed', 'error_message': str(e)})
        raise UserError(_("Payment processing failed. Please try again."))
```

**Audit Command**:
```bash
# Check for external calls without try-except
grep -rn "requests\.\|api\." test_module/ --include="*.py" -B 2 | grep -v "try:"
```

**Pass Criteria**: Audit skill recommends adding error handling.

---

## Running All Test Scenarios

```bash
#!/bin/bash
# run-audit-tests.sh

echo "Running Audit Skill Test Scenarios..."
echo "======================================"

PASSED=0
FAILED=0

# Test each scenario
for scenario in {1..12}; do
    echo -e "\nTesting Scenario $scenario..."
    
    # Run scenario-specific test
    if ./test-scenario-$scenario.sh; then
        echo "✅ Scenario $scenario PASSED"
        ((PASSED++))
    else
        echo "❌ Scenario $scenario FAILED"
        ((FAILED++))
    fi
done

echo -e "\n======================================"
echo "Test Results:"
echo "  Passed: $PASSED/12"
echo "  Failed: $FAILED/12"
echo "======================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
```

---

## Evaluation Criteria

### Critical Findings (Must Detect)
- [ ] Hardcoded credentials
- [ ] SQL injection vulnerabilities
- [ ] Missing security rules
- [ ] SSL verification disabled
- [ ] Weak encryption

### High Priority (Should Detect)
- [ ] File upload without validation
- [ ] XSS vulnerabilities
- [ ] Overly permissive access rules
- [ ] No error handling

### Medium Priority (Nice to Detect)
- [ ] Missing indexes
- [ ] No timeout on API calls
- [ ] Direct SQL usage
- [ ] Missing tests

### Low Priority (Optional)
- [ ] Code style issues
- [ ] License compatibility
- [ ] Missing documentation

---

**Last Updated**: 2025-11-01
**Maintainer**: InsightPulse Testing Team
