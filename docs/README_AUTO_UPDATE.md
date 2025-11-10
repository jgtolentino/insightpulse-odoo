# README.md Auto-Update Mechanism

**Current Status**: ✅ Partially Automated
**Last Review**: 2025-11-10

---

## Auto-Update Components

### 1. GitHub Workflows (2)

**`scheduled.yml`** - Daily at 2 AM UTC
- Checks OCA module updates
- Updates addons/README.md (not root README.md)
- Creates PR if updates found
- Status: ✅ Active

**`doc-automation.yml`** - Daily at 3 AM UTC
- Generates documentation
- Updates doc-related sections
- Status: ⚠️ Redundant (should be deleted per WORKFLOW_CONSOLIDATION.md)

### 2. Auto-Updated Sections

**Automatically Updated**:
- ✅ CI/CD badges (real-time via shields.io)
- ✅ Deploy badges (real-time via GitHub Actions)
- ✅ OCA module updates (daily via scheduled.yml)

**Manually Updated**:
- ❌ Odoo version (currently shows 19.0, should be 18.0) ⚠️ CRITICAL FIX NEEDED
- ❌ SaaS parity percentage (87%)
- ❌ Test method count (134 methods)
- ❌ Cost savings ($58,800/yr)
- ❌ Infrastructure features list

### 3. Dynamic Badges

These update automatically via shields.io:

```markdown
[![CI Status](https://github.com/jgtolentino/insightpulse-odoo/workflows/CI/badge.svg)]
[![Deploy Status](https://github.com/jgtolentino/insightpulse-odoo/workflows/Deploy/badge.svg)]
```

**Status**: ✅ Working

### 4. Scripts (Planned but Not Implemented)

**Missing Scripts**:
- `scripts/update-readme-stats.sh` - Update test count, line count
- `scripts/update-readme-parity.sh` - Calculate SaaS parity percentage
- `scripts/update-readme-version.sh` - Sync Odoo version from package.json

---

## Critical Issue: Version Mismatch ⚠️

**Problem**:
- README.md says: **"Odoo 19.0 CE"** (lines 9, 38)
- CLAUDE.md says: **"Odoo CE 18.0"**
- docs/index.md says: **"Odoo CE 18.0"**
- Docker files use: **FROM odoo:18.0**

**Root Cause**: README.md not updated after Odoo 18.0 CE freeze decision

**Impact**:
- Confuses users and AI agents
- Contradicts canonical architecture documentation
- GitHub description shows wrong version

**Fix Required**: Update README.md to consistently reference Odoo 18.0 CE

---

## Recommended Auto-Update Strategy

### Immediate: Fix Version Mismatch

```bash
# 1. Update README.md
sed -i 's/Odoo 19\.0 CE/Odoo 18.0 CE/g' README.md
sed -i 's/Odoo 19 CE/Odoo 18.0 CE/g' README.md

# 2. Update GitHub repository description
gh repo edit jgtolentino/insightpulse-odoo \
  --description "Enterprise-grade multi-tenant SaaS platform built on Odoo 18.0 CE + OCA modules"

# 3. Commit
git add README.md
git commit -m "fix(docs): correct Odoo version 19.0 → 18.0 CE in README"
```

### Long-Term: Implement Auto-Update Script

Create `scripts/update-readme-stats.sh`:

```bash
#!/bin/bash
# Auto-update README.md with current statistics

# Get Odoo version from docker-compose.yml or Dockerfile
ODOO_VERSION=$(grep "FROM odoo:" Dockerfile.odoo | sed 's/FROM odoo://' | head -1)

# Count test methods
TEST_COUNT=$(grep -r "def test_" odoo/tests addons/*/tests 2>/dev/null | wc -l | tr -d ' ')

# Count Python lines in custom modules
CODE_LINES=$(find addons/custom addons/insightpulse odoo_addons -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')

# Calculate SaaS parity (from spec-kit compliance)
PARITY_SCORE=$(python3 scripts/calculate-parity.py 2>/dev/null || echo "87")

# Update README.md
sed -i "s/Odoo [0-9]\+\.[0-9]\+ CE/Odoo $ODOO_VERSION CE/g" README.md
sed -i "s/[0-9]\+ test methods/$TEST_COUNT test methods/g" README.md
sed -i "s/[0-9]\+,[0-9]\+ lines of tests/$CODE_LINES lines of tests/g" README.md
sed -i "s/Parity-[0-9]\+%/Parity-${PARITY_SCORE}%/g" README.md

echo "✅ README.md updated with current stats"
echo "   - Odoo version: $ODOO_VERSION"
echo "   - Test methods: $TEST_COUNT"
echo "   - Code lines: $CODE_LINES"
echo "   - SaaS parity: ${PARITY_SCORE}%"
```

### Integration with CI

Add to `.github/workflows/scheduled.yml`:

```yaml
- name: Update README Statistics
  run: |
    bash scripts/update-readme-stats.sh

- name: Commit README Updates
  if: github.event_name == 'schedule'
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add README.md
    git commit -m "docs(readme): auto-update statistics [skip ci]" || echo "No changes"
    git push
```

---

## Current README Sections

### Static (Manually Updated)
- Project description
- SaaS replacement matrix
- Features list
- Getting started guide
- License information

### Dynamic (Should Be Auto-Updated)
- ✅ CI/Deploy badges (shields.io)
- ❌ Odoo version ⚠️ NEEDS FIX
- ❌ Test count
- ❌ Line count
- ❌ Parity percentage
- ❌ Cost savings

### Planned (Not Yet Implemented)
- Module count
- OCA module versions
- Deployment targets
- Last update timestamp

---

## Action Items

### High Priority
1. ✅ **Fix Odoo 19 → 18 version mismatch** (immediate)
2. ✅ **Update GitHub repo description** (immediate)
3. ✅ **Create auto-update script** (this week)

### Medium Priority
4. Add test count auto-update
5. Add parity percentage calculation
6. Add last-updated timestamp

### Low Priority
7. Add module version tracking
8. Add deployment status indicators
9. Add contribution statistics

---

## Testing Auto-Updates

```bash
# 1. Run update script locally
bash scripts/update-readme-stats.sh

# 2. Check diff
git diff README.md

# 3. Verify correctness
grep "Odoo.*CE" README.md  # Should show 18.0
grep "test methods" README.md  # Should show current count
grep "Parity" README.md  # Should show current percentage

# 4. If correct, commit
git add README.md
git commit -m "docs(readme): auto-update statistics"
```

---

**Answer to User Question**:

**Does README auto-update?**
- **Badges**: ✅ Yes (real-time via shields.io)
- **OCA Modules**: ✅ Yes (daily via scheduled.yml)
- **Version/Stats**: ❌ No (manual updates only)
- **Critical Issue**: README shows Odoo 19.0 but should be 18.0 ⚠️

**Recommendation**: Implement `scripts/update-readme-stats.sh` and integrate with daily cron.
