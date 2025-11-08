# Branch Protection Setup - PR #326

## Overview
Configure branch protection on `main` to enforce deployment gates and review requirements before merging PR #326 (T&E MVP Bundle).

---

## 🔒 1. Required Status Checks

**Path:** Settings → Branches → `main` → Edit branch protection rule

### Check Configuration

✅ **Require status checks to pass before merging** (enabled)

✅ **Require branches to be up to date before merging** (enabled)

### Required Checks (add these):

- `gates` (from `.github/workflows/deploy-gates.yml`)
- `evals` (from `.github/workflows/tee-mvp-ci.yml`) — if you want blocking OCR/warehouse tests
- Any other critical workflows (e.g., `Claude Config — Validate & Sync`, `Supabase Edge — CI/CD`)

**Note:** The check name must match the **job name** in the workflow file, not the workflow name.

---

## 👥 2. Pull Request Reviews

✅ **Require pull request reviews before merging** (enabled)

**Settings:**
- Required approving reviews: **1** (minimum)
- Recommended reviewers: **Owner** (required) + **Ops** (optional)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (if `CODEOWNERS` file exists)

---

## 🔐 3. Conversation Resolution

⚠️ **Do NOT enable** "Require conversation resolution before merging" if:
- Your CI posts informational comments
- Auto-fix workflows comment on PRs
- The secrets verifier posts non-blocking summaries

**Why:** These comments create "unresolved" threads that block merge unnecessarily.

**Alternative:** Use "Request changes" review status for blocking issues instead of comments.

---

## 🛡️ 4. Additional Protections (Recommended)

### Force Push Prevention
✅ **Do not allow force pushes** (enabled)

Protects against accidental history rewrites on `main`.

### Deletion Prevention
✅ **Do not allow deletions** (enabled)

Prevents accidental branch deletion.

### Admin Enforcement
☐ **Include administrators** (optional)

If enabled, even admins must follow branch protection rules. Recommended for production environments.

### Linear History
☐ **Require linear history** (optional)

Enforces "Squash and merge" or "Rebase and merge" only. **Not recommended** if you use "Merge commits" to preserve PR history.

---

## ⚙️ 5. CI Permissions (Workflows)

Ensure workflows that need to push commits or comment on PRs have appropriate permissions.

### For `deploy-gates.yml`
Already added in latest version:
```yaml
permissions:
  contents: write       # allow auto-fix commits
  pull-requests: write  # allow PR comments
  actions: read         # read other workflow statuses
```

### For `tee-mvp-ci.yml`
If it needs to comment results:
```yaml
permissions:
  contents: read
  pull-requests: write
```

---

## 📋 6. Quick Verification

After configuring branch protection:

```bash
# 1. Check PR #326 status
gh pr view 326 --web

# 2. Verify required checks appear
gh pr checks 326

# 3. Expected output:
# ✓ gates    Deploy Gates
# ✓ evals    tee-mvp-ci (optional)
# - Any other required checks

# 4. If checks are missing:
gh workflow list  # verify workflow exists
gh workflow run deploy-gates.yml  # trigger manually
```

---

## 🚀 7. Test Configuration

### Before Merging PR #326

1. **Push a test commit** to the PR branch
2. **Verify deploy-gates workflow runs** automatically
3. **Check secrets verifier output** in workflow logs
4. **Ensure required checks block merge** if they fail
5. **Get required reviews** (at least 1 approval)
6. **Merge button should be green** when all conditions met

### Test Commands

```bash
# Locally simulate CI
make pr-clear

# Check what GitHub sees
gh pr view 326 --json statusCheckRollup --jq '.statusCheckRollup'

# Manually trigger deploy-gates (if workflow_dispatch enabled)
gh workflow run deploy-gates.yml
```

---

## ❗ Troubleshooting

### "Required status check not found"

**Cause:** Job name mismatch or workflow hasn't run yet.

**Fix:**
```bash
# 1. Check actual job name in workflow file
grep -A 5 "^jobs:" .github/workflows/deploy-gates.yml

# 2. Trigger workflow to create the check
git commit --allow-empty -m "trigger: deploy gates"
git push

# 3. Wait for workflow to complete
gh run watch
```

### "Checks have failed"

**Expected behavior.** Fix the issues reported in workflow logs before merging.

```bash
# View failure details
gh run view --log-failed

# Re-run after fixes
git commit -m "fix: address deployment gate issues"
git push
```

### "Secrets not showing in verifier"

**Cause:** Secrets not configured in repository settings.

**Fix:**
```bash
# Set required secrets
gh secret set SUPABASE_DB_HOST -b "your-host"
gh secret set SUPABASE_DB_PORT -b "5432"
gh secret set SUPABASE_DB_NAME -b "postgres"
gh secret set SUPABASE_DB_USER -b "your-user"
gh secret set SUPABASE_DB_PASSWORD -b "your-password"

# Set required variables
gh variable set ODOO_HOST -b "erp.insightpulseai.net"
gh variable set OCR_HOST -b "ocr.insightpulseai.net"

# Verify
gh secret list
gh variable list
```

---

## 📚 References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [Workflow Permissions](https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs)

---

**Last Updated:** 2025-11-07
**For PR:** #326 (InsightPulse T&E MVP Bundle)
**Status:** Ready for configuration ✅
