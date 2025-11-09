# CONTRIBUTING.md Guardrails Update

**Date:** 2025-11-09
**Related:** PR #377 Deployment Hardening
**Branch:** `claude/fix-pr377-deployment-hardening-011CUx25DeeRE81kvmGWuEjU`

## Summary

Updated `CONTRIBUTING.md` with comprehensive guardrails and CI/CD architecture documentation to complement PR #377's deployment hardening changes.

## What Changed

### 1. New Section: Platform Spec Validation (Required)

**Location:** After "Development Workflow", before "Code Quality Standards"

**Content:**
- Explanation of `spec/platform_spec.json` as single source of truth
- Validation requirements (`python3 scripts/validate_spec.py`)
- When to update the spec (workflows, docs, services, deployments)
- Spec update process with example commit message
- Troubleshooting validation failures
- Spec-kit architecture benefits

**Why:**
- Enforces platform spec compliance at contribution time
- Prevents spec drift between code and documentation
- Clarifies the role of spec-kit in deployment safety

### 2. New Section: Pre-Commit Guardrails

**Location:** After "Documentation Standards", before "Submitting Changes"

**Content:**
- Pre-commit hook installation instructions
- Local validation script (`scripts/pre-flight-check.sh`)
- Automated check commands (make targets)
- Guardrail checklist (6 items)
- Common gotchas (do's and don'ts)

**Why:**
- Catches issues locally before CI/CD
- Reduces CI/CD failures and iteration cycles
- Improves security awareness (no hardcoded secrets)
- Provides executable script for validation

### 3. New Section: CI/CD Pipeline & Required Checks

**Location:** After "Submitting Changes", before "Review Process"

**Content:**
- Visual ASCII pipeline architecture diagram (6 stages)
- Detailed breakdown of 4 required checks:
  1. **Spec Guard** - Validates `platform_spec.json`
  2. **CI Unified** - Quality + tests + security
  3. **CI - Code Quality & Tests** - Odoo module tests
  4. **Deploy Gates** - Pre-deployment validation
- Supporting checks (informational, non-blocking)
- Branch protection rules
- Workflow documentation references

**Why:**
- Aligns with PR #377 CI/CD architecture
- Clarifies which checks are required vs informational
- Documents the deployment pipeline flow
- Helps contributors understand CI/CD expectations

### 4. Updated: Table of Contents

**Changes:**
- Added "Platform Spec Validation (Required)"
- Added "Pre-Commit Guardrails"
- Added "CI/CD Pipeline & Required Checks"

**Why:**
- Improves navigation to new sections

### 5. Updated: Development Workflow → Make Your Changes

**Changes:**
- Added spec validation reminder with example commands

**Why:**
- Reminds contributors to validate spec early in the process

### 6. Updated: Pull Request Checklist

**Changes:**
- Reorganized into 6 categories (was flat list):
  1. **Platform Spec & Architecture** (3 items)
  2. **Code Quality** (5 items)
  3. **Testing** (4 items)
  4. **Documentation** (5 items)
  5. **Security & Best Practices** (4 items)
  6. **Git Hygiene** (3 items)

**Why:**
- Better organization and clarity
- Easier to scan and verify completion
- Emphasizes platform spec validation

### 7. Updated: Review Process → Automated Checks

**Changes:**
- Split into two categories:
  - **Required (Must Pass):** 4 core checks
  - **Informational (Advisory):** 3 supporting checks

**Why:**
- Clarifies blocking vs non-blocking checks
- Aligns with PR #377 architecture

## New File: scripts/pre-flight-check.sh

**Purpose:** Comprehensive local validation script

**Features:**
- ✅ Platform spec validation
- ✅ Code formatting checks (black, isort)
- ✅ Linting (flake8)
- ✅ Security scans (hardcoded secrets detection)
- ✅ Python module compilation
- ✅ Git status checks (merge conflicts)
- ✅ TODO marker detection in production code
- ✅ Color-coded output with summary
- ✅ Strict mode option (`--strict`)

**Usage:**
```bash
# Normal mode (exit on errors only)
./scripts/pre-flight-check.sh

# Strict mode (exit on warnings too)
./scripts/pre-flight-check.sh --strict
```

**Checks Performed:**

| Check | Tool | Exit on Failure |
|-------|------|----------------|
| Platform spec validation | `validate_spec.py` | Yes |
| Code formatting | `black`, `isort` | Warning only |
| Linting | `flake8` | Warning only |
| Secrets detection | `grep` patterns | Yes |
| Module compilation | `python -m compileall` | Warning only |
| Merge conflicts | `grep` | Yes |
| TODO markers | `grep` | Warning only |

## Benefits

### For Contributors:

1. **Clear Expectations**
   - Know exactly what checks are required
   - Understand the spec-kit architecture
   - Have local validation tools

2. **Faster Iteration**
   - Catch issues before CI/CD
   - Reduce push/fail/fix cycles
   - Get immediate feedback locally

3. **Better Security**
   - Pre-flight script detects hardcoded secrets
   - Security awareness baked into process
   - Prevents accidental exposure

4. **Spec Compliance**
   - Understand when to update the spec
   - Validation script ensures compliance
   - No spec drift

### For Maintainers:

1. **Automated Enforcement**
   - Spec Guard workflow enforces compliance
   - CI/CD catches issues automatically
   - Reduced manual review burden

2. **Standardized Process**
   - All contributors follow same workflow
   - Consistent code quality baseline
   - Clear required vs optional checks

3. **Documentation Accuracy**
   - Spec-kit ensures docs match code
   - Platform spec is always current
   - No drift between implementation and documentation

4. **Deployment Safety**
   - Pre-deployment gates validate quality
   - Spec validation guards production
   - Triple smoke tests after deployment

## Integration with PR #377

This documentation update directly supports the deployment hardening work:

| PR #377 Change | CONTRIBUTING.md Update |
|----------------|------------------------|
| Spec Guard workflow | Platform Spec Validation section |
| CI Unified workflow | CI/CD Pipeline section |
| Dependency scanning resilience | Supporting Checks documentation |
| Automation health non-blocking | Required vs Informational split |
| cd-odoo-prod.yml deployment | Pipeline architecture diagram |

## Validation

Tested locally:
```bash
# Spec validation passes
python3 scripts/validate_spec.py
# ✅ Spec validation complete – all guardrails passed

# Pre-flight script runs
./scripts/pre-flight-check.sh
# ✅ Platform spec validation passed
# (other checks run based on local environment)
```

## Files Modified

```
CONTRIBUTING.md                  (+628 lines)
scripts/pre-flight-check.sh      (new file, +258 lines)
docs/contributing-guardrails-update.md  (this file)
```

## Commits

1. **1b5fd68** - `fix(ci): harden PR #377 deployment workflows for production readiness`
2. **518c3f1** - `docs: update CONTRIBUTING.md with spec validation guardrails and CI/CD architecture`

## Next Steps for Contributors

When contributing, follow this workflow:

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes

# 3. Validate spec (if changed)
python3 scripts/validate_spec.py

# 4. Run pre-flight checks
./scripts/pre-flight-check.sh

# 5. Commit
git commit -m "feat: my feature description"

# 6. Push
git push origin feature/my-feature

# 7. Create PR
# 8. Wait for required checks to pass
# 9. Address review feedback
# 10. Merge when approved
```

## Migration Notes

**For existing contributors:**
- Review the new "Platform Spec Validation" section
- Install pre-commit hooks: `pip install pre-commit && pre-commit install`
- Run `./scripts/pre-flight-check.sh` before committing
- When adding workflows/docs, update `spec/platform_spec.json`

**For new contributors:**
- Start with "Getting Started" section
- Read "Platform Spec Validation" section carefully
- Use `./scripts/pre-flight-check.sh` for local validation
- Follow the updated Pull Request Checklist

## References

- **CONTRIBUTING.md** - Updated contribution guide
- **spec/platform_spec.json** - Platform specification
- **scripts/validate_spec.py** - Spec validation script
- **scripts/pre-flight-check.sh** - Pre-commit validation script
- **.github/workflows/spec-guard.yml** - Spec Guard workflow
- **.github/workflows/README.md** - Workflow documentation
- **docs/pr-377-fixes.md** - PR #377 fixes summary

---

**Author:** Claude
**Date:** 2025-11-09
**PR:** #377 - Production Deployment Hardening
