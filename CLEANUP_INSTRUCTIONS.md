# Health Check Issues Cleanup Instructions

## What Was Done

### 1. Fixed Health Monitor Workflow Bug ✅

**Problem:**
- 229 open issues (21+ were duplicate health-check issues)
- Auto-close mechanism was not working reliably

**Root Cause:**
The `close-resolved-issues` job in `.github/workflows/health-monitor.yml` was configured with:
```yaml
needs: [public-health, origin-health]
```

However, `origin-health` is optional and only runs on scheduled runs (not manual dispatch by default). When `origin-health` is skipped, the `close-resolved-issues` job doesn't run, leaving health check issues open indefinitely.

**Solution:**
Changed the workflow to:
```yaml
needs: [public-health]
if: needs.public-health.result == 'success'
```

This makes the auto-close mechanism work every time the public health checks pass, regardless of whether origin health checks run.

### 2. Created Cleanup Scripts ✅

Two scripts were created to close all existing health check issues:

1. **Python script:** `scripts/close_health_issues.py` (recommended)
2. **Bash script:** `scripts/close-health-check-issues.sh`

## How to Close All Existing Health Check Issues

You have **3 options**:

### Option 1: Wait for Automatic Closure (Recommended)

The next time the health monitor runs successfully (every 5 minutes), it will automatically close all open health check issues. Just wait a few minutes and they should close automatically.

### Option 2: Trigger the Close Workflow Manually

1. Go to: https://github.com/jgtolentino/insightpulse-odoo/actions/workflows/close-duplicate-health-issues.yml
2. Click "Run workflow" button
3. Select branch: `main`
4. Click "Run workflow"

This will close all health check issues immediately.

### Option 3: Run the Cleanup Script Locally

If you have GitHub authentication set up:

```bash
# Using Python (requires: pip install requests)
python3 scripts/close_health_issues.py

# Or using bash (requires: gh CLI installed)
./scripts/close-health-check-issues.sh
```

## What Happens Next

- ✅ Health monitor will now automatically close issues when health is restored
- ✅ Only one health check issue will be created per incident (instead of duplicates)
- ✅ Existing issues will auto-close on next successful health check

## Verify Everything is Green

After the issues are closed, verify all workflows are passing:

```bash
# Check recent workflow runs
open https://github.com/jgtolentino/insightpulse-odoo/actions

# Or view from CLI
gh run list --limit 20
```

## Summary

| Item | Status |
|------|--------|
| Health monitor auto-close bug | ✅ **FIXED** |
| Cleanup scripts created | ✅ **DONE** |
| Changes committed and pushed | ✅ **DONE** |
| Close existing issues | 🟡 **PENDING** (auto or manual) |

---

**Next Steps:**
1. Wait 5 minutes for automatic closure, OR
2. Manually trigger the close workflow, OR
3. Run the cleanup script locally

All future health check issues will be automatically managed! 🎉
