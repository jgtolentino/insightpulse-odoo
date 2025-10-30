# Testing Parity Live Sync Workflow

This document explains how to test the Parity Live Sync workflow both locally and via GitHub Actions.

## Local Testing

### Test 1: Without Secrets (Graceful Failure)

This tests the workflow behavior when Odoo secrets are not configured.

```bash
./scripts/test-parity-live-sync.sh
```

**Expected Result:**
- ✅ Workflow completes successfully (exit code 0)
- ⚠️ Shows helpful message about configuring secrets
- ⚠️ Export step skipped
- ⚠️ Sync step skipped
- ⚠️ Commit step skipped
- ✅ Summary displays setup instructions

### Test 2: With Secrets (Full Export)

This tests the complete workflow with valid Odoo credentials.

```bash
# Set environment variables
export ODOO_URL="https://your-odoo-instance.com"
export ODOO_DB="odoo_prod"
export ODOO_LOGIN="admin@example.com"
export ODOO_PASSWORD="password"

# Run test
./scripts/test-parity-live-sync.sh --with-secrets
```

**Expected Result:**
- ✅ Export step succeeds
- ✅ Creates snapshot files in `reports/`
- ✅ Syncs to `docs/ENTERPRISE_PARITY.md`
- ✅ Detects changes
- ✅ Would commit and push (dry run in test mode)
- ✅ Summary displays snapshot data

## GitHub Actions Testing

### Option 1: Manual Trigger (Recommended)

1. Go to: https://github.com/jgtolentino/insightpulse-odoo/actions/workflows/parity-live-sync.yml

2. Click **"Run workflow"** button (top right)

3. Select branch: `claude/add-oca-fetch-script-011CUdg4RZ5thYCwopLXbgCE` or `main`

4. Click **"Run workflow"** to start

**Without Secrets Configured:**
- ✅ Workflow will show **green checkmark** (success)
- ✅ Summary will display setup instructions
- ⚠️ No export or sync performed

**With Secrets Configured:**
- ✅ Exports live module inventory
- ✅ Creates snapshot files
- ✅ Syncs to documentation
- ✅ Commits and pushes changes
- ✅ Summary displays full snapshot

### Option 2: Push to Main

The workflow automatically triggers on push to `main` branch when these files change:
- `scripts/export-live-modules.py`
- `scripts/sync-live-to-docs.sh`
- `.github/workflows/parity-live-sync.yml`

```bash
# Merge feature branch to main
git checkout main
git merge claude/add-oca-fetch-script-011CUdg4RZ5thYCwopLXbgCE
git push origin main
```

### Option 3: Scheduled Trigger

The workflow runs automatically **daily at 18:00 UTC (02:00 PH time)**.

No action needed - just wait for the scheduled run.

## Configuring Secrets (Optional)

To enable live Odoo exports, add secrets in GitHub:

1. Go to: https://github.com/jgtolentino/insightpulse-odoo/settings/secrets/actions

2. Click **"New repository secret"**

3. Add the following secrets:

| Secret Name | Example Value | Description |
|-------------|---------------|-------------|
| `ODOO_URL` | `https://insightpulseai.net/odoo` | Your Odoo instance URL |
| `ODOO_DB` | `odoo_prod` | Database name |
| `ODOO_LOGIN` | `admin@example.com` | Admin user login |
| `ODOO_PASSWORD` | `your-secure-password` | Admin user password |

**Security Notes:**
- Never commit secrets to the repository
- Use read-only database user if possible
- Rotate passwords regularly
- Monitor audit logs for suspicious activity

## Workflow Behavior Summary

### When Secrets NOT Configured:
```
✅ Checkout code
✅ Set up Python 3.12
✅ Install dependencies (requests)
⚠️ Export step: Skipped (no ODOO_URL)
   → export_success=false
⚠️ Sync step: Skipped (conditional check)
⚠️ Git diff: Skipped (no changes)
⚠️ Commit: Skipped (conditional check)
✅ Upload artifacts: No files to upload
✅ Summary: Shows setup instructions
```

**Result:** Green checkmark ✅ (success)

### When Secrets ARE Configured:
```
✅ Checkout code
✅ Set up Python 3.12
✅ Install dependencies (requests)
✅ Export step: Connects to Odoo, exports modules
   → export_success=true
   → Creates reports/live_modules_2025-10-30T1730Z.csv
   → Creates reports/live_modules_2025-10-30T1730Z.md
✅ Sync step: Appends snapshot to docs/ENTERPRISE_PARITY.md
✅ Git diff: Detects changes
   → changed=true
✅ Commit: Creates commit with snapshot
✅ Push: Pushes to origin
✅ Upload artifacts: Uploads CSV and MD files
✅ Summary: Shows full snapshot data
```

**Result:** Green checkmark ✅ (success with artifacts)

## Troubleshooting

### Workflow Fails at Export Step

**Problem:** `ERROR: Authentication failed`

**Solution:**
- Verify `ODOO_URL` is correct and accessible
- Verify `ODOO_DB` database name exists
- Verify `ODOO_LOGIN` and `ODOO_PASSWORD` are correct
- Check Odoo instance is running and accessible

### Workflow Fails at Sync Step

**Problem:** `ERROR: No live module snapshots found`

**Solution:**
- This should never happen if export succeeds
- Check export step logs for errors
- Verify `reports/` directory permissions

### Workflow Fails at Commit Step

**Problem:** `Git push failed`

**Solution:**
- Verify GitHub Actions has write permissions
- Check branch protection rules
- Ensure no merge conflicts

### Summary Shows No Data

**Problem:** Summary is empty or shows placeholder

**Solution:**
- This is expected when secrets are not configured
- Follow setup instructions in summary to configure secrets

## Verification

After running the workflow, verify:

1. **Workflow Status:** Green checkmark at https://github.com/jgtolentino/insightpulse-odoo/actions

2. **Artifacts:** Check for uploaded artifacts (if secrets configured)
   - `live_modules_YYYY-MM-DDTHHMMZ.csv`
   - `live_modules_YYYY-MM-DDTHHMMZ.md`

3. **Documentation:** Check `docs/ENTERPRISE_PARITY.md` was updated (if secrets configured)

4. **Commits:** Check for new commit by `github-actions[bot]` (if secrets configured)

5. **Summary:** Check workflow summary shows expected output

## Next Steps

1. ✅ Local test passed: `./scripts/test-parity-live-sync.sh`
2. ⏳ Manual trigger test: Run workflow from GitHub UI
3. ⏳ Verify green checkmark without secrets
4. ⏳ (Optional) Configure secrets and test full export
5. ⏳ (Optional) Merge to main to enable automatic daily sync

---

**Last Updated:** 2025-10-30
**Workflow File:** `.github/workflows/parity-live-sync.yml`
**Test Script:** `scripts/test-parity-live-sync.sh`
