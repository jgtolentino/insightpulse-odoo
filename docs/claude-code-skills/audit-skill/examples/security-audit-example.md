# Security Audit Example

Complete walkthrough of conducting a security audit on an Odoo module.

## Scenario

Audit the `ipai_expense` module for security vulnerabilities before production deployment.

## Step 1: Initialize Audit

```bash
cd /home/runner/work/insightpulse-odoo/insightpulse-odoo
MODULE_PATH="addons/custom/ipai_expense"
AUDIT_DATE=$(date +%Y-%m-%d)
AUDIT_REPORT="audit-reports/ipai_expense-security-${AUDIT_DATE}.md"
```

## Step 2: Scan for Hardcoded Secrets

```bash
# Search for hardcoded passwords
echo "## Hardcoded Credentials Scan" >> "$AUDIT_REPORT"
grep -rn "password\s*=\s*['\"]" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "✓ No hardcoded passwords found" >> "$AUDIT_REPORT"

# Search for API keys
echo -e "\n## API Keys Scan" >> "$AUDIT_REPORT"
grep -rn "api_key\|API_KEY" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "✓ No hardcoded API keys found" >> "$AUDIT_REPORT"

# Search for tokens
echo -e "\n## Token Scan" >> "$AUDIT_REPORT"
grep -rn "token\s*=\s*['\"]" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "✓ No hardcoded tokens found" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## Hardcoded Credentials Scan
addons/custom/ipai_expense/models/expense_config.py:45:        OCR_API_KEY = "demo-key-12345"

## API Keys Scan
addons/custom/ipai_expense/models/expense_config.py:45:        OCR_API_KEY = "demo-key-12345"
addons/custom/ipai_expense/models/expense_config.py:46:        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'fallback-key')

## Token Scan
✓ No hardcoded tokens found
```

**Findings**:
- 🔴 **Critical**: Hardcoded OCR API key on line 45
- 🟠 **High**: Fallback API key for OpenAI (should fail if not set)

## Step 3: Check Authentication & Authorization

```bash
# Check for missing security rules
echo -e "\n## Security Rules Check" >> "$AUDIT_REPORT"

# Check if security directory exists
if [ ! -d "$MODULE_PATH/security" ]; then
    echo "❌ CRITICAL: No security directory found" >> "$AUDIT_REPORT"
else
    echo "✓ Security directory exists" >> "$AUDIT_REPORT"
    
    # Check for ir.model.access.csv
    if [ ! -f "$MODULE_PATH/security/ir.model.access.csv" ]; then
        echo "❌ CRITICAL: No ir.model.access.csv found" >> "$AUDIT_REPORT"
    else
        echo "✓ ir.model.access.csv exists" >> "$AUDIT_REPORT"
        echo -e "\n### Access Rights:" >> "$AUDIT_REPORT"
        cat "$MODULE_PATH/security/ir.model.access.csv" >> "$AUDIT_REPORT"
    fi
    
    # Check for record rules
    if [ -f "$MODULE_PATH/security/ipai_expense_security.xml" ]; then
        echo -e "\n✓ Record rules file exists" >> "$AUDIT_REPORT"
    else
        echo -e "\n⚠️  WARNING: No record rules file found" >> "$AUDIT_REPORT"
    fi
fi
```

**Example Output**:
```
## Security Rules Check
✓ Security directory exists
✓ ir.model.access.csv exists

### Access Rights:
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_expense_ocr_user,expense.ocr.user,model_expense_ocr,base.group_user,1,1,1,0
access_expense_ocr_manager,expense.ocr.manager,model_expense_ocr,base.group_system,1,1,1,1

✓ Record rules file exists
```

**Findings**:
- ✅ **Pass**: Security directory structure complete
- ✅ **Pass**: Access rights defined for all models
- ✅ **Pass**: Record rules implemented

## Step 4: Check for SQL Injection Vulnerabilities

```bash
# Check for direct SQL execution
echo -e "\n## SQL Injection Check" >> "$AUDIT_REPORT"
grep -rn "self\.env\.cr\.execute\|self\._cr\.execute" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "✓ No direct SQL execution found" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## SQL Injection Check
addons/custom/ipai_expense/models/expense_analytics.py:67:        self.env.cr.execute("""
            SELECT category, SUM(amount) as total
            FROM expense_ocr
            WHERE user_id = %s
            GROUP BY category
        """, (user_id,))
```

**Findings**:
- 🟡 **Medium**: Direct SQL execution found (line 67)
- ✅ **Mitigated**: Uses parameterized queries (not vulnerable to SQL injection)
- 📝 **Recommendation**: Consider using ORM instead for maintainability

## Step 5: Check for XSS Vulnerabilities

```bash
# Check for unescaped user input in views
echo -e "\n## XSS Vulnerability Check" >> "$AUDIT_REPORT"

# Find fields with t-raw or t-esc
grep -rn "t-raw\|t-esc" "$MODULE_PATH/views" --include="*.xml" >> "$AUDIT_REPORT" || echo "No JavaScript templates found" >> "$AUDIT_REPORT"

# Check for user input sanitization
grep -rn "html_sanitize\|plaintext2html" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "⚠️  WARNING: No explicit sanitization found" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## XSS Vulnerability Check
No JavaScript templates found
⚠️  WARNING: No explicit sanitization found
```

**Findings**:
- ✅ **Pass**: No t-raw usage (QWeb templates safe)
- 🟡 **Medium**: No explicit HTML sanitization in Python code
- 📝 **Recommendation**: Add html_sanitize() for user-generated content fields

## Step 6: Check File Upload Security

```bash
# Check file upload handling
echo -e "\n## File Upload Security" >> "$AUDIT_REPORT"

# Find file upload fields
grep -rn "Binary\|Image" "$MODULE_PATH/models" --include="*.py" | grep "fields\." >> "$AUDIT_REPORT" || echo "No file upload fields found" >> "$AUDIT_REPORT"

# Check for file type validation
grep -rn "mimetype\|file_extension\|allowed_extensions" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "⚠️  WARNING: No file type validation found" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## File Upload Security
addons/custom/ipai_expense/models/expense_ocr.py:23:    receipt_image = fields.Binary(string='Receipt Image', attachment=True)

⚠️  WARNING: No file type validation found
```

**Findings**:
- 🟠 **High**: File upload without type validation
- 📝 **Recommendation**: Add MIME type validation
- 📝 **Recommendation**: Limit file size (max 5MB)
- 📝 **Recommendation**: Scan uploads for malware

**Remediation**:
```python
# Add to expense_ocr.py
@api.constrains('receipt_image')
def _check_receipt_image(self):
    """Validate uploaded receipt image"""
    for record in self:
        if record.receipt_image:
            # Check file size (5MB limit)
            import base64
            file_size = len(base64.b64decode(record.receipt_image))
            if file_size > 5 * 1024 * 1024:
                raise ValidationError(_("File size must not exceed 5MB"))
            
            # Check MIME type
            import magic
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(base64.b64decode(record.receipt_image))
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
            if file_type not in allowed_types:
                raise ValidationError(_(
                    "Only images (JPEG, PNG, GIF) and PDF files are allowed"
                ))
```

## Step 7: Check Data Encryption

```bash
# Check for sensitive data fields
echo -e "\n## Data Encryption Check" >> "$AUDIT_REPORT"

# Find potentially sensitive fields
grep -rn "ssn\|social_security\|bank_account\|credit_card\|salary" "$MODULE_PATH/models" --include="*.py" -i >> "$AUDIT_REPORT" || echo "No obvious sensitive fields found" >> "$AUDIT_REPORT"

# Check for encryption implementation
grep -rn "encrypt\|cipher\|fernet" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "⚠️  WARNING: No encryption implementation found" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## Data Encryption Check
No obvious sensitive fields found
⚠️  WARNING: No encryption implementation found
```

**Findings**:
- ✅ **Pass**: No sensitive PII fields detected
- ℹ️  **Info**: Consider encryption for expense amounts if handling sensitive financial data

## Step 8: Check External API Security

```bash
# Check for external API calls
echo -e "\n## External API Security" >> "$AUDIT_REPORT"

# Find API calls
grep -rn "requests\.\|urllib\.\|httplib" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "No external API calls found" >> "$AUDIT_REPORT"

# Check for SSL verification
grep -rn "verify=False" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" && echo "❌ CRITICAL: SSL verification disabled" >> "$AUDIT_REPORT" || echo "✓ SSL verification enabled" >> "$AUDIT_REPORT"

# Check for timeout configuration
grep -rn "timeout=" "$MODULE_PATH" --include="*.py" >> "$AUDIT_REPORT" || echo "⚠️  WARNING: No timeout configuration found" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## External API Security
addons/custom/ipai_expense/models/expense_ocr.py:89:            response = requests.post(
addons/custom/ipai_expense/models/expense_ocr.py:92:                timeout=30

✓ SSL verification enabled
addons/custom/ipai_expense/models/expense_ocr.py:92:                timeout=30
```

**Findings**:
- ✅ **Pass**: SSL verification enabled (default)
- ✅ **Pass**: Timeout configured (30 seconds)
- 📝 **Recommendation**: Add retry logic with exponential backoff

## Step 9: Generate Summary Report

```python
#!/usr/bin/env python3
"""Generate security audit summary"""

findings = {
    'critical': [
        {
            'id': 'SEC-001',
            'title': 'Hardcoded API Key',
            'location': 'models/expense_config.py:45',
            'cvss': 9.8,
            'description': 'OCR API key hardcoded in source code',
            'remediation': 'Move to environment variable: OCR_API_KEY = os.environ.get("OCR_API_KEY")'
        }
    ],
    'high': [
        {
            'id': 'SEC-002',
            'title': 'Unvalidated File Upload',
            'location': 'models/expense_ocr.py:23',
            'cvss': 7.5,
            'description': 'Receipt image upload without MIME type validation',
            'remediation': 'Add file type validation and size limits'
        },
        {
            'id': 'SEC-003',
            'title': 'Fallback API Key',
            'location': 'models/expense_config.py:46',
            'cvss': 7.0,
            'description': 'OpenAI API key has fallback value instead of raising error',
            'remediation': 'Remove fallback, raise error if environment variable not set'
        }
    ],
    'medium': [
        {
            'id': 'SEC-004',
            'title': 'Direct SQL Execution',
            'location': 'models/expense_analytics.py:67',
            'cvss': 5.3,
            'description': 'Using direct SQL instead of ORM',
            'remediation': 'Refactor to use ORM for better maintainability'
        },
        {
            'id': 'SEC-005',
            'title': 'No HTML Sanitization',
            'location': 'models/*.py',
            'cvss': 4.7,
            'description': 'No explicit HTML sanitization for user content',
            'remediation': 'Add html_sanitize() for user-generated content fields'
        }
    ],
    'low': []
}

# Calculate risk score
risk_score = (
    len(findings['critical']) * 10 +
    len(findings['high']) * 7 +
    len(findings['medium']) * 4 +
    len(findings['low']) * 1
) / 10

print(f"""
# Security Audit Summary Report
**Module**: ipai_expense
**Date**: {date.today()}
**Risk Score**: {risk_score}/10 ({"Critical" if risk_score >= 8 else "High" if risk_score >= 6 else "Medium"})

## Overview
- Critical: {len(findings['critical'])} vulnerabilities
- High: {len(findings['high'])} vulnerabilities
- Medium: {len(findings['medium'])} vulnerabilities
- Low: {len(findings['low'])} vulnerabilities

## Immediate Actions Required
""")

for finding in findings['critical']:
    print(f"""
### {finding['id']}: {finding['title']}
**CVSS**: {finding['cvss']} (Critical)
**Location**: `{finding['location']}`
**Issue**: {finding['description']}
**Fix**: {finding['remediation']}
""")

print("""
## Remediation Timeline
- **Critical issues**: Within 24 hours
- **High issues**: Within 1 week
- **Medium issues**: Within 1 month
- **Low issues**: Next maintenance cycle

## Re-audit Required
After remediation of Critical and High issues.
""")
```

## Step 10: Track Remediation

Create tracking issues:

```bash
# Create GitHub issues for each finding
gh issue create \
    --title "SEC-001: Hardcoded API Key in expense_config.py" \
    --body "$(cat <<EOF
**Severity**: Critical (CVSS 9.8)
**Location**: models/expense_config.py:45

**Issue**: OCR API key hardcoded in source code

**Remediation**:
\`\`\`python
# Remove this
OCR_API_KEY = "demo-key-12345"

# Replace with
OCR_API_KEY = os.environ.get('OCR_API_KEY')
if not OCR_API_KEY:
    raise ValueError("OCR_API_KEY environment variable not set")
\`\`\`

**Timeline**: Fix within 24 hours
EOF
)" \
    --label "security,critical,expense-module"
```

## Result

**Security Audit Complete**:
- ✅ Automated scans completed
- ✅ Manual review completed
- ✅ Report generated
- ✅ Issues tracked in GitHub
- ⏳ Awaiting remediation

**Next Steps**:
1. Fix critical issues (SEC-001)
2. Fix high priority issues (SEC-002, SEC-003)
3. Schedule medium priority fixes
4. Re-audit after remediation
5. Document security improvements

---

**Audit Completed**: 2025-11-01
**Auditor**: Security Agent
**Status**: Requires remediation before production deployment
