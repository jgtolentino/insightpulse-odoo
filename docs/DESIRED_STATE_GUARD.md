# Desired State Guard

**Single Source of Truth for Repository Architecture**

## Overview

The Desired State Guard is an automated system that enforces architectural rules, module conventions, and compliance requirements across the InsightPulse Odoo repository.

**Key Principle**: Define once in JSON, enforce everywhere via CI/CD.

## Components

### 1. Specification (JSON)

**File**: `docs/desired_state.json`

Single source of truth defining:
- ✅ Odoo version (18.0 CE + OCA)
- ✅ Module naming conventions (`ipai_*` prefix)
- ✅ Addons root path (`odoo_addons/`)
- ✅ Runtime environment (URLs, database config)
- ✅ Routing specification (subdomain → service mappings)
- ✅ Compliance requirements (BIR, GDPR, SOC2)
- ✅ Testing requirements (coverage, frameworks)
- ✅ Security rules (no secrets, RLS enforcement)

### 2. Validator (Python)

**File**: `tools/check_desired_state.py`

Automated validator that:
- Reads `desired_state.json`
- Validates repository structure against spec
- Checks module naming, manifests, secrets
- Reports errors, warnings, and successes

**Usage**:
```bash
# Run validator
python3 tools/check_desired_state.py

# Verbose output
python3 tools/check_desired_state.py --verbose

# Custom spec path
python3 tools/check_desired_state.py --spec path/to/spec.json
```

### 3. GitHub Actions Workflow

**File**: `.github/workflows/desired-state-guard.yml`

CI/CD enforcement running on:
- ✅ Every push to `main`, `develop`, `claude/**` branches
- ✅ Every pull request
- ✅ Daily scheduled runs (6 AM UTC) to detect drift
- ✅ Manual trigger via `workflow_dispatch`

**Features**:
- Validates JSON schema
- Runs Python validator
- Posts comments on failed PRs with fix instructions
- Creates issues for scheduled drift detection
- Uploads validation reports as artifacts

## What Gets Validated

### Repository Structure
- ✅ Odoo version matches target (18.0 CE)
- ✅ `odoo_addons/` directory exists
- ✅ All custom modules use `ipai_*` prefix
- ✅ Module manifests have required fields
- ✅ Valid LGPL-3 or AGPL-3 license

### Security
- ✅ No hardcoded secrets or API keys
- ✅ No passwords in code
- ✅ Environment variables for sensitive data

### Runtime Configuration
- ✅ Service URLs defined (ERP, Superset, n8n, etc.)
- ✅ Database configuration present
- ✅ Routing specification complete

### Compliance
- ✅ BIR (Philippines) requirements documented
- ✅ GDPR compliance features listed
- ✅ SOC2 controls mapped

## Exit Codes

- `0` - Validation passed (warnings OK)
- `1` - Validation failed (errors found)

## Example Output

```
🎯 Desired State Guard - Starting Validation

✅ Loaded spec: docs/desired_state.json
✅ Odoo target version: 18.0-ce
✅ odoo.conf exists and appears valid
✅ Addons root exists: odoo_addons
✅ All modules use 'ipai_' prefix
✅ Found 19 custom modules
✅ Manifest validation: 19/19 modules passed
✅ No obvious secrets detected in Python files
✅ ERP URL configured: https://erp.insightpulseai.net
✅ Routing specification: 7 routes defined
✅ Base domain: insightpulseai.net

======================================================================
🎯 Validation Summary
======================================================================
✅ Passed:   16
⚠️  Warnings: 2
======================================================================

⚠️  Validation PASSED with warnings
```

## How It Works

### 1. JSON as Source of Truth

```json
{
  "target_state": {
    "odoo_version": "18.0-ce",
    "addons_root": "odoo_addons",
    "module_prefix": "ipai_"
  },
  "runtime_environment": {
    "ERP_BASE_URL": "https://erp.insightpulseai.net"
  },
  "routing_specification": {
    "routes": [
      {
        "subdomain": "erp",
        "target": "odoo:8069"
      }
    ]
  }
}
```

### 2. Validator Reads JSON

Python script loads JSON and validates:
- File existence checks
- Pattern matching
- Manifest parsing
- Secret scanning

### 3. CI/CD Enforces

GitHub Actions runs validator on:
- Every code push
- Pull requests
- Daily schedule
- Manual trigger

### 4. Automatic Drift Detection

Scheduled daily runs detect configuration drift and create issues if validation fails.

## Benefits

### ✅ Single Source of Truth
- No duplicate specs in YAML
- One place to update architecture rules
- JSON is version-controlled and reviewable

### ✅ Automated Enforcement
- Catches violations before merge
- No manual review needed for basic structure
- Consistent across all branches

### ✅ Self-Documenting
- Spec doubles as architecture documentation
- Always up-to-date (enforced by CI)
- Clear validation messages

### ✅ Drift Detection
- Daily scheduled checks
- Auto-creates issues for drift
- Prevents silent decay

## Extending the System

### Add New Validation Rules

1. **Update JSON spec** (`docs/desired_state.json`):
   ```json
   {
     "validation_rules": {
       "my_new_rule": {
         "description": "Enforce X",
         "enforcement": "strict"
       }
     }
   }
   ```

2. **Add validator method** (`tools/check_desired_state.py`):
   ```python
   def validate_my_new_rule(self) -> None:
       """Validate my new rule."""
       spec = self.spec.get("validation_rules", {})
       rule = spec.get("my_new_rule", {})

       if not rule:
           return

       # Your validation logic
       if condition_passes:
           self.ok("My new rule passed")
       else:
           self.fail("My new rule failed: reason")
   ```

3. **Call in `validate_all()`**:
   ```python
   def validate_all(self) -> int:
       # ... existing validations ...
       self.validate_my_new_rule()
       # ...
   ```

### Add External Validators

Drop scripts in `tools/` and the validator will auto-discover them:
- `tools/check_manifests.py`
- `tools/validate_routing.py`
- `scripts/validate-structure.sh`

They'll be called automatically if they exist.

## Common Issues & Fixes

### ❌ Module without `ipai_` prefix

**Error**: `Modules without 'ipai_' prefix: my_module`

**Fix**: Rename module:
```bash
mv odoo_addons/my_module odoo_addons/ipai_my_module
```

### ❌ Missing manifest fields

**Error**: `my_module/__manifest__.py missing: license, author`

**Fix**: Add fields to `__manifest__.py`:
```python
{
    'name': 'My Module',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    # ... other fields
}
```

### ❌ Hardcoded secrets detected

**Error**: `Potential secrets found in: my_script.py`

**Fix**: Use environment variables:
```python
# ❌ Bad
password = "my_secret_password"

# ✅ Good
import os
password = os.environ.get("DATABASE_PASSWORD")
```

### ⚠️ License not in allowed list

**Warning**: `module/__manifest__.py: license not in allowed list`

**Fix**: Use approved license:
```python
{
    'license': 'LGPL-3',  # or AGPL-3, LGPL-3.0, AGPL-3.0
}
```

## Integration with Other Workflows

The Desired State Guard complements existing workflows:

- **OCA Pre-commit** (`.github/workflows/oca-pre-commit.yml`) - Code style
- **CI Odoo** (`.github/workflows/ci-odoo.yml`) - Module tests
- **Spec Guard** (`.github/workflows/spec-guard.yml`) - API specs
- **Desired State Guard** - Architecture & structure ← YOU ARE HERE

Together, these provide comprehensive quality gates.

## Maintenance

### Updating the Specification

When architecture changes:

1. Update `docs/desired_state.json`
2. Update validator if needed (`tools/check_desired_state.py`)
3. Commit both together
4. CI validates on next push

### Version History

Track changes to the spec via git:
```bash
git log -- docs/desired_state.json
```

### Testing Changes Locally

Before pushing:
```bash
# Test your changes
python3 tools/check_desired_state.py --verbose

# Should pass or have expected warnings
```

## Architecture Decision Record

**Decision**: Use JSON + Python validator + GitHub Actions for desired state enforcement

**Alternatives Considered**:
1. ❌ Encode rules in YAML workflows (hard to maintain)
2. ❌ Manual code review only (not scalable)
3. ❌ Shell scripts (not cross-platform)
4. ✅ JSON spec + Python validator (chosen)

**Rationale**:
- JSON is declarative, readable, and version-controlled
- Python is portable and has good JSON/file handling
- GitHub Actions provides free CI/CD
- Separation of spec from enforcement logic
- Easy to extend and test locally

## References

- 📄 Spec: `docs/desired_state.json`
- 🔧 Validator: `tools/check_desired_state.py`
- ⚙️ Workflow: `.github/workflows/desired-state-guard.yml`
- 📖 Main README: `README.md`

## Support

- **Issues**: File GitHub issue with label `desired-state-guard`
- **Questions**: See GitHub Discussions
- **Local testing**: `python3 tools/check_desired_state.py --verbose`

---

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Maintainer**: InsightPulse AI DevOps Team
