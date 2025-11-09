# Audit Skill Usage Guide

Complete guide for using the newly implemented Audit Skill to perform comprehensive security, quality, and compliance audits on Odoo modules.

## Overview

The Audit Skill is a comprehensive capability set that enables agents to perform multi-dimensional audits on Odoo codebases. It follows the Anthropic Agent Skills Spec and integrates with existing audit tools.

**Skill Location**: `docs/claude-code-skills/audit-skill/`

**Total Size**: 98.4KB of documentation, examples, and evaluations

## Quick Start

### 1. Run Demo Audit

The fastest way to see the audit skill in action:

```bash
cd /home/runner/work/insightpulse-odoo/insightpulse-odoo

# Audit a specific module
./scripts/demo-audit-skill.sh addons/custom/ipai_expense

# Audit another module
./scripts/demo-audit-skill.sh addons/insightpulse/finance/ipai_rate_policy
```

This will perform:
- Security vulnerability scanning
- Module structure validation
- Manifest compliance checking
- Performance issue detection

### 2. Read the Main Skill Documentation

```bash
# View the main skill file
cat docs/claude-code-skills/audit-skill/SKILL.md
```

Or use the `view` tool if you're an agent:
```
view /home/runner/work/insightpulse-odoo/insightpulse-odoo/docs/claude-code-skills/audit-skill/SKILL.md
```

### 3. Follow a Complete Example

For a step-by-step walkthrough:

**Security Audit**:
```bash
cat docs/claude-code-skills/audit-skill/examples/security-audit-example.md
```

**Module Structure Audit**:
```bash
cat docs/claude-code-skills/audit-skill/examples/module-audit-example.md
```

## Skill Contents

### Core Documentation

**SKILL.md** (12.6KB)
- Main entry point for the audit skill
- Overview of all audit capabilities
- When to use each audit type
- Quick reference commands
- Integration with existing tools

### Reference Guides

**security-audit-guide.md** (19.7KB)
- Credential management and secret detection
- Authentication and authorization validation
- Data protection and encryption
- API security best practices
- Configuration security checklists
- Dependency vulnerability scanning
- CI/CD security gates

**module-audit-guide.md** (22.9KB)
- OCA module structure validation
- Manifest file requirements
- Security rules auditing
- View structure compliance
- Model validation
- Performance optimization checks

### Examples

**security-audit-example.md** (13.2KB)
- Complete security audit workflow
- Real-world module audit (ipai_expense)
- Automated scanning commands
- Finding classification (Critical/High/Medium/Low)
- Remediation tracking
- Report generation

**module-audit-example.md** (17.2KB)
- OCA compliance validation workflow
- Directory structure verification
- Required files checklist
- Manifest validation
- Security configuration checks
- Code quality assessment

### Evaluations

**test-scenarios.md** (12.9KB)
- 12 comprehensive test scenarios
- Hardcoded credentials detection
- SQL injection identification
- XSS vulnerability checks
- File upload validation
- Access control verification
- Performance issue detection

## Common Use Cases

### Use Case 1: Pre-Production Security Audit

**Scenario**: You need to audit a module before deploying to production.

**Steps**:
1. Read the skill documentation:
   ```bash
   view docs/claude-code-skills/audit-skill/SKILL.md
   view docs/claude-code-skills/audit-skill/reference/security-audit-guide.md
   ```

2. Run security scans:
   ```bash
   # Hardcoded credentials
   grep -rn "password\s*=\s*['\"]" addons/my_module/ --include="*.py"
   
   # API keys
   grep -rn "api_key\|API_KEY" addons/my_module/ --include="*.py"
   
   # SQL injection risks
   grep -rn "self\.env\.cr\.execute" addons/my_module/ --include="*.py"
   ```

3. Generate report following the template in `security-audit-example.md`

4. Track findings as GitHub issues

### Use Case 2: OCA Submission Validation

**Scenario**: You want to submit a module to OCA and need to ensure compliance.

**Steps**:
1. Read the module audit guide:
   ```bash
   view docs/claude-code-skills/audit-skill/reference/module-audit-guide.md
   ```

2. Validate structure:
   ```bash
   # Check required directories
   ls -la addons/my_module/
   
   # Validate manifest
   python3 -c "import ast; print(ast.literal_eval(open('addons/my_module/__manifest__.py').read()))"
   ```

3. Check security files:
   ```bash
   # Verify access rights
   cat addons/my_module/security/ir.model.access.csv
   ```

4. Follow the example in `module-audit-example.md`

### Use Case 3: Continuous Security Monitoring

**Scenario**: You want to add automated security checks to CI/CD.

**Steps**:
1. Review CI/CD integration patterns in `security-audit-guide.md`:
   ```bash
   view docs/claude-code-skills/audit-skill/reference/security-audit-guide.md
   ```
   (See "Continuous Security Monitoring" section)

2. Add security scanning to GitHub Actions:
   ```yaml
   # .github/workflows/security.yml
   - name: Run Security Audit
     run: |
       grep -r "password\s*=\s*['\"]" addons/ --include="*.py" && exit 1 || true
       bandit -r addons/ -ll
       safety check
   ```

3. Configure automated reporting

### Use Case 4: Performance Optimization

**Scenario**: You need to identify and fix performance bottlenecks.

**Steps**:
1. Read performance sections:
   ```bash
   view docs/claude-code-skills/audit-skill/SKILL.md
   # Navigate to "### 4. Database Audits" section
   ```

2. Check for missing indexes:
   ```bash
   # Find fields that should be indexed
   grep -rn "fields\.Char\|fields\.Date" addons/my_module/models/ --include="*.py" | grep -v "index=True"
   ```

3. Identify N+1 queries:
   ```python
   # Look for patterns like:
   for record in records:
       print(record.related_field.name)  # N+1 query
   ```

4. Apply fixes from the reference guide

## Integration with Existing Tools

### Scripts Integration

The audit skill works alongside existing scripts:

**Module Audit Script**:
```bash
./scripts/audit-modules.sh odoo_db --output table
```

This script:
- Checks filesystem vs database module state
- Identifies orphaned modules
- Validates installation status
- Complements the audit skill's module structure validation

**Deployment Check**:
```bash
./scripts/deploy-check.sh --full
```

### Security Report Integration

The skill follows the same format as:
```bash
cat SECURITY_AUDIT_REPORT.md
```

This allows for consistent reporting and tracking.

## Audit Types

### 1. Security Audit

**Focus**: Vulnerability detection and remediation

**What it checks**:
- ✅ Hardcoded credentials (passwords, API keys, tokens)
- ✅ SQL injection vulnerabilities
- ✅ XSS (Cross-Site Scripting) risks
- ✅ Weak encryption implementations
- ✅ Missing authentication/authorization
- ✅ Insecure file uploads
- ✅ Exposed sensitive data

**Command reference**:
```bash
view docs/claude-code-skills/audit-skill/reference/security-audit-guide.md
```

### 2. Module Structure Audit

**Focus**: OCA compliance and best practices

**What it checks**:
- ✅ Required directory structure
- ✅ Manifest completeness and format
- ✅ Security rules presence
- ✅ View structure compliance
- ✅ Model naming conventions
- ✅ Documentation completeness

**Command reference**:
```bash
view docs/claude-code-skills/audit-skill/reference/module-audit-guide.md
```

### 3. Code Quality Audit

**Focus**: Code standards and maintainability

**What it checks**:
- ✅ PEP 8 compliance
- ✅ Docstring completeness
- ✅ Code smells (duplicate code, long methods)
- ✅ Anti-patterns (direct SQL, no error handling)
- ✅ Import organization
- ✅ Type hints

**Tools**:
```bash
flake8 addons/my_module/ --config=.flake8
pylint addons/my_module/ --rcfile=.pylintrc-mandatory
```

### 4. Performance Audit

**Focus**: Query optimization and efficiency

**What it checks**:
- ✅ Missing database indexes
- ✅ N+1 query patterns
- ✅ Inefficient search domains
- ✅ Unoptimized computed fields
- ✅ Large table scans

**Example check**:
```python
# Check for computed fields without store
grep -rn "compute=" addons/my_module/models/ --include="*.py" | grep -v "store=True"
```

### 5. Compliance Audit

**Focus**: License and regulatory compliance

**What it checks**:
- ✅ LGPL-3.0 license compliance
- ✅ GDPR requirements
- ✅ Third-party license compatibility
- ✅ Data privacy policies

## Agent Usage Patterns

For agents using this skill:

### Pattern 1: Security Audit Request

**User says**: "Audit the security of the ipai_expense module"

**Agent should**:
1. Read `audit-skill/SKILL.md` to understand capabilities
2. Read `audit-skill/reference/security-audit-guide.md` for detailed procedures
3. Follow `audit-skill/examples/security-audit-example.md` workflow
4. Execute automated scans using bash tool
5. Generate comprehensive report
6. Create GitHub issues for findings

### Pattern 2: OCA Submission Validation

**User says**: "Validate this module for OCA submission"

**Agent should**:
1. Read `audit-skill/reference/module-audit-guide.md`
2. Follow `audit-skill/examples/module-audit-example.md`
3. Check directory structure, manifest, security files
4. Validate naming conventions and documentation
5. Generate compliance report
6. List required fixes

### Pattern 3: Performance Review

**User says**: "Find performance issues in this module"

**Agent should**:
1. Read performance sections in `audit-skill/SKILL.md`
2. Check for missing indexes
3. Identify N+1 query patterns
4. Review computed fields
5. Suggest optimizations

## Severity Classification

The audit skill uses standardized severity levels:

### Critical (9.0-10.0 CVSS)
- Remote code execution
- Authentication bypass
- Exposed credentials
- Data breach potential

**Response**: Fix within 24 hours

### High (7.0-8.9 CVSS)
- SQL injection
- XSS vulnerabilities
- Privilege escalation
- Missing authentication

**Response**: Fix within 1 week

### Medium (4.0-6.9 CVSS)
- Information disclosure
- CSRF vulnerabilities
- Insecure configurations
- Missing input validation

**Response**: Fix within 1 month

### Low (0.1-3.9 CVSS)
- Code quality issues
- Missing documentation
- Performance concerns
- Minor security hardening

**Response**: Next maintenance cycle

## Output Formats

### Console Output

The demo script provides colorized, human-readable output:
```bash
./scripts/demo-audit-skill.sh addons/my_module/
```

### Markdown Reports

Generate detailed markdown reports:
```bash
# Example from security-audit-example.md
echo "# Security Audit Report" > audit-report.md
echo "**Date**: $(date)" >> audit-report.md
# ... add findings
```

### JSON Output

For CI/CD integration:
```bash
# Using bandit
bandit -r addons/ -f json -o security-audit.json

# Using safety
safety check --json > dependencies-audit.json
```

### CSV Output

For spreadsheet analysis:
```bash
./scripts/audit-modules.sh odoo_db --output csv > module-audit.csv
```

## Troubleshooting

### Issue: No findings detected but issues exist

**Solution**: Ensure you're searching the correct directory and file types:
```bash
# Verify you're in the right location
pwd

# Check file exists
ls -la addons/my_module/

# Use correct patterns
grep -rn "pattern" addons/my_module/ --include="*.py" --include="*.xml"
```

### Issue: False positives in scans

**Solution**: Review findings manually and document false positives:
```markdown
## False Positives
- Finding: API key in test file
- Reason: Test fixture, not real credential
- Action: Document in security exceptions
```

### Issue: Overwhelming number of findings

**Solution**: Prioritize by severity:
1. Fix all Critical issues first
2. Then High priority
3. Schedule Medium for next sprint
4. Low priority as time permits

## Best Practices

1. **Run audits regularly**: Before each deployment, weekly in development

2. **Track findings**: Create GitHub issues for all Critical and High findings

3. **Automate in CI/CD**: Add security scans to GitHub Actions

4. **Document exceptions**: Maintain a list of known false positives

5. **Follow up**: Re-audit after fixes to verify remediation

6. **Share reports**: Keep stakeholders informed with regular audit reports

7. **Update skill**: As new vulnerability patterns emerge, update the skill documentation

## Related Documentation

- [Main README](../README.md) - Project overview
- [Security Audit Report](../SECURITY_AUDIT_REPORT.md) - Existing security findings
- [Module Documentation](../MODULES.md) - Module reference
- [Deployment Checklist](../DEPLOYMENT_CHECKLIST.md) - Pre-deployment validation

## Support

For questions or issues with the audit skill:

1. Check the skill documentation
2. Review examples for similar use cases
3. Consult the reference guides
4. Open a GitHub issue if needed

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-11-01
**Maintainer**: InsightPulse Team
