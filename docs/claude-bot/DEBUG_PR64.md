# Claude Bot Debug - PR #64 Error

## ❌ Error Encountered

You commented `@claude` on PR #64 and got:
```
❌ Claude Auto-Fix Bot encountered an error. Please check the workflow logs.
```

## ✅ Good News

The bot **DID trigger!** The workflow exists in main and is active.

## 🔍 Debugging Steps

### Step 1: Check Workflow Logs

Go to:
1. **Actions tab** → https://github.com/jgtolentino/insightpulse-odoo/actions
2. Find the failed **Claude Auto-Fix Bot** run
3. Click on it to see detailed logs

Or via command line:
```bash
gh run list --workflow=claude-autofix-bot.yml
gh run view <run-id> --log-failed
```

---

### Step 2: Common Issues & Fixes

#### Issue #1: API Key Not Set ⚠️ MOST LIKELY

**Check:**
```bash
gh secret list | grep ANTHROPIC_API_KEY
```

**Fix:**
```bash
# Add the secret
gh secret set ANTHROPIC_API_KEY
# Paste: sk-ant-xxx (from console.anthropic.com)
```

Then retry by commenting `@claude` again on the PR.

---

#### Issue #2: Permissions Not Configured

**Check:** Settings → Actions → General

**Fix:**
1. Workflow permissions: **"Read and write permissions"**
2. ✅ **"Allow GitHub Actions to create and approve pull requests"**
3. Save

---

#### Issue #3: Python Error in Workflow

**Likely error:** Missing `anthropic` module or syntax error

**Check logs for:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Fix:** The workflow already installs it, so this shouldn't happen. But if it does:
```yaml
# In .github/workflows/claude-autofix-bot.yml
- name: Install Anthropic SDK
  run: |
    pip install --upgrade anthropic
```

---

#### Issue #4: Large PR (Too Many Files)

PR #64 has **81 files changed** which might be too large.

**Check logs for:**
```
collected=0 files
```

**Fix:** The workflow limits to 20 files automatically, but might fail with very large PRs.

**Workaround:** Be specific:
```
@claude review the finance automation files only
```

---

### Step 3: Quick Test

Comment on PR #64 again with something simple:
```
@claude help
```

This uses minimal tokens and should work even if the API key has low credits.

---

### Step 4: Check API Key Credits

Go to: https://console.anthropic.com/settings/billing

**Free tier:** $5 credits (should be plenty)

If you're out of credits, add payment method or use a new API key.

---

## 🚀 Most Likely Fix (90% chance)

```bash
# 1. Add API key secret
gh secret set ANTHROPIC_API_KEY
# Paste key from: https://console.anthropic.com/settings/keys

# 2. Retry on PR #64
# Just comment: @claude review
```

---

## 📊 Expected Behavior

When working correctly:
1. You comment: `@claude review`
2. Bot reacts: 👀 (working...)
3. ~30-60 seconds pass
4. Bot posts detailed analysis
5. Bot reacts: 🚀 (done!)

---

## 🐛 Get Detailed Error Info

Run this script to diagnose:

```bash
#!/bin/bash
# Save as: debug_bot.sh

echo "=== Claude Bot Diagnostics ==="

# 1. Check secret
echo "1. API Key Secret:"
gh secret list | grep ANTHROPIC || echo "❌ Not found"

# 2. Check permissions
echo "2. Workflow Permissions:"
gh api repos/jgtolentino/insightpulse-odoo/actions/permissions | jq .default_workflow_permissions

# 3. Check workflow file
echo "3. Workflow File:"
ls -la .github/workflows/claude-autofix-bot.yml

# 4. Check recent runs
echo "4. Recent Runs:"
gh run list --workflow=claude-autofix-bot.yml --limit 3

# 5. Check last failed run logs
echo "5. Last Failed Run:"
LAST_RUN=$(gh run list --workflow=claude-autofix-bot.yml --limit 1 --json databaseId -q '.[0].databaseId')
gh run view $LAST_RUN --log-failed | tail -50
```

```bash
chmod +x debug_bot.sh
./debug_bot.sh
```

---

## ✅ Once Fixed

Comment again on PR #64:
```
@claude review the SuperClaude multi-agent implementation

Focus on:
- Code quality
- Security issues
- Performance concerns
```

---

## 📞 Still Stuck?

Share the error output from:
```bash
gh run view <run-id> --log-failed
```

And I'll help debug further!

---

**My bet:** API key not set. Run `gh secret set ANTHROPIC_API_KEY` and retry! 🎯
