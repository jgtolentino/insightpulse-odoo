# Claude Auto-Fix Bot - Troubleshooting Guide

Complete guide to diagnosing and fixing issues with the Claude Auto-Fix Bot.

---

## 🔍 Quick Diagnosis

### Step 1: Check if Bot is Installed

```bash
# Check workflow file exists
ls .github/workflows/claude-autofix-bot.yml

# Expected output: .github/workflows/claude-autofix-bot.yml
# If not found: The workflow is not installed
```

### Step 2: Check if Bot is Running

```bash
# List recent workflow runs
gh run list --workflow=claude-autofix-bot.yml --limit 5

# View specific run details
gh run view <run-id>

# View logs for failed run
gh run view <run-id> --log-failed
```

### Step 3: Check Configuration

```bash
# Verify secret exists
gh secret list | grep ANTHROPIC_API_KEY

# Check repository permissions
gh api repos/{owner}/{repo}/actions/permissions
```

---

## 🚨 Common Errors & Solutions

### Error 1: "Bot doesn't respond at all"

**Symptoms:**
- You comment `@claude fix` but nothing happens
- No reactions (👀) appear
- No workflow run is triggered

**Diagnosis:**
```bash
# Check if workflow is enabled
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml | jq .state

# Check recent runs
gh run list --workflow=claude-autofix-bot.yml
```

**Root Causes & Solutions:**

#### Cause 1.1: Workflow is disabled
```bash
# Enable the workflow
gh workflow enable claude-autofix-bot.yml
```

#### Cause 1.2: Comment not on a Pull Request
**Problem:** You commented on an Issue, not a PR

**Solution:** Only comment on Pull Requests. Issues are not supported.

```bash
# Verify it's a PR
gh pr view 123  # Use PR number, not issue number
```

#### Cause 1.3: Typo in @claude mention
**Problem:** You typed `@cluade` or `@Claude` (case sensitive in some contexts)

**Solution:** Use exactly `@claude` (lowercase)

#### Cause 1.4: Workflow permissions not set
**Problem:** GitHub Actions doesn't have permission to comment

**Solution:**
1. Go to **Settings → Actions → General**
2. Set **"Workflow permissions"** to **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**
4. Click **Save**

**Verify:**
```bash
gh api repos/{owner}/{repo}/actions/permissions | jq
# Look for: "default_workflow_permissions": "write"
```

---

### Error 2: "ANTHROPIC_API_KEY not found"

**Symptoms:**
- Workflow runs but fails with error
- Log shows: `Error: ANTHROPIC_API_KEY is not set`
- Bot reacts with 😕

**Diagnosis:**
```bash
# Check if secret exists
gh secret list

# Expected output should include: ANTHROPIC_API_KEY
```

**Root Causes & Solutions:**

#### Cause 2.1: Secret not added
**Solution:**
```bash
# Add the secret via CLI
gh secret set ANTHROPIC_API_KEY

# Or via web UI:
# Settings → Secrets → Actions → New repository secret
```

#### Cause 2.2: Secret name typo
**Problem:** You named it `ANTHROPIC_KEY` or `CLAUDE_API_KEY`

**Solution:** The name MUST be exactly `ANTHROPIC_API_KEY`

```bash
# Remove wrong secret
gh secret remove WRONG_NAME

# Add correct secret
gh secret set ANTHROPIC_API_KEY
```

#### Cause 2.3: Secret in wrong scope
**Problem:** Secret is in Environment secrets, not Repository secrets

**Solution:** Add to Repository secrets (not Environment or Organization)

**Verify:**
```bash
# List all secrets
gh secret list --repo {owner}/{repo}

# Should show: ANTHROPIC_API_KEY
```

---

### Error 3: "API call failed with 401 Unauthorized"

**Symptoms:**
- Workflow runs but fails at "Call Claude API" step
- Log shows: `401 Unauthorized` or `Invalid API key`
- Bot reacts with 😕

**Diagnosis:**
```bash
# Test API key locally
export ANTHROPIC_API_KEY=sk-ant-xxx
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":1024,"messages":[{"role":"user","content":"test"}]}'
```

**Root Causes & Solutions:**

#### Cause 3.1: Invalid API key
**Problem:** API key is wrong, expired, or malformed

**Solution:**
1. Go to https://console.anthropic.com/settings/keys
2. **Delete** the old key (if exists)
3. **Create** a new key
4. **Update** GitHub secret:
   ```bash
   gh secret set ANTHROPIC_API_KEY
   # Paste new key when prompted
   ```

#### Cause 3.2: API key doesn't have credits
**Problem:** Free tier credits ($5) are exhausted

**Solution:**
1. Go to https://console.anthropic.com/settings/billing
2. Add payment method
3. Add credits ($10 minimum)

**Check usage:**
```bash
curl https://api.anthropic.com/v1/usage \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

#### Cause 3.3: Secret not properly set
**Problem:** Secret contains extra whitespace or quotes

**Solution:**
```bash
# Remove the secret
gh secret remove ANTHROPIC_API_KEY

# Add it again, ensuring no extra characters
# Copy ONLY the key: sk-ant-api03-xxx (no quotes, no spaces)
gh secret set ANTHROPIC_API_KEY
```

---

### Error 4: "Rate limit exceeded"

**Symptoms:**
- Bot responds with error after several uses
- Log shows: `429 Too Many Requests`
- Multiple PRs reviewed in short time

**Diagnosis:**
```bash
# Check recent workflow runs
gh run list --workflow=claude-autofix-bot.yml --limit 20 | grep "completed"

# Count runs in last hour
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml/runs \
  --jq '.workflow_runs | map(select(.created_at > (now - 3600))) | length'
```

**Root Causes & Solutions:**

#### Cause 4.1: Too many requests in short time
**Problem:** Claude API rate limits (free tier: 50 requests/day)

**Solution:**
1. **Wait 1 hour** and retry
2. **Upgrade to paid tier** for higher limits
3. **Add rate limiting** to workflow:

Edit `.github/workflows/claude-autofix-bot.yml`:
```yaml
- name: Rate limit protection
  run: |
    # Add 5 second delay between requests
    sleep 5
```

#### Cause 4.2: Multiple bots running
**Problem:** Multiple workflows triggering Claude API

**Solution:**
```bash
# List all workflows
gh workflow list

# Disable duplicate workflows
gh workflow disable <workflow-id>
```

---

### Error 5: "Workflow timeout"

**Symptoms:**
- Workflow runs for 6 hours then times out
- Never completes
- Bot never responds

**Diagnosis:**
```bash
# Check workflow duration
gh run view <run-id> --json conclusion,duration

# View logs to see where it's stuck
gh run view <run-id> --log
```

**Root Causes & Solutions:**

#### Cause 5.1: Python script hangs
**Problem:** API call hangs waiting for response

**Solution:** Add timeout to workflow:

Edit `.github/workflows/claude-autofix-bot.yml`:
```yaml
- name: Call Claude API
  timeout-minutes: 5  # Add this line
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python3 << 'PYTHON_SCRIPT'
    # ... rest of script
```

#### Cause 5.2: Large PR with too many files
**Problem:** Trying to analyze 100+ files

**Solution:** The workflow already limits to 20 files. Check if the filter is working:

```bash
# Check how many files changed
gh pr view 123 --json files --jq '.files | length'

# If more than 20, the workflow should handle it
```

---

### Error 6: "Permission denied creating comment"

**Symptoms:**
- Workflow runs successfully
- Claude analyzes code
- But fails to post comment
- Log shows: `403 Forbidden` or `Permission denied`

**Diagnosis:**
```bash
# Check workflow permissions
gh api repos/{owner}/{repo}/actions/permissions/workflow | jq .default_workflow_permissions
```

**Root Causes & Solutions:**

#### Cause 6.1: Workflow permissions not set
**Solution:**
1. Go to **Settings → Actions → General**
2. Under **"Workflow permissions"**, select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**
4. Click **Save**

#### Cause 6.2: Branch protection rules
**Problem:** Branch has restrictions on comments

**Solution:**
1. Go to **Settings → Branches**
2. Edit protection rules for the target branch
3. Add GitHub Actions to **"Restrict who can push to matching branches"**

---

### Error 7: "File not found" or "Empty response"

**Symptoms:**
- Bot responds but says no files found
- Response is empty or generic
- Log shows: `collected=0 files`

**Diagnosis:**
```bash
# Check what files changed in PR
gh pr view 123 --json files --jq '.files[].path'

# Check if files are text files
file path/to/changed/file.py
```

**Root Causes & Solutions:**

#### Cause 7.1: PR has no changes
**Problem:** Draft PR or no commits yet

**Solution:** Push commits to the PR branch first

```bash
git push origin feature-branch
```

#### Cause 7.2: All files are binary or too large
**Problem:** Changed files are images, PDFs, or > 50KB

**Solution:** The bot automatically skips:
- Binary files
- Files larger than 50KB
- Build artifacts

**Workaround:** Add a text file with summary:
```bash
echo "Summary of changes..." > CHANGES.txt
git add CHANGES.txt
git commit -m "Add summary for Claude"
git push
```

#### Cause 7.3: Git fetch failed
**Problem:** Workflow can't access PR branch

**Solution:** Check branch exists:
```bash
gh pr view 123 --json headRefName,baseRefName
```

---

### Error 8: "Python module not found"

**Symptoms:**
- Workflow fails at "Call Claude API" step
- Log shows: `ModuleNotFoundError: No module named 'anthropic'`

**Diagnosis:**
```bash
# Check workflow logs
gh run view <run-id> --log | grep "ModuleNotFoundError"
```

**Root Causes & Solutions:**

#### Cause 8.1: Install step failed
**Problem:** `pip install anthropic` failed silently

**Solution:** Check workflow logs for pip errors:
```bash
gh run view <run-id> --log | grep -A 10 "Install Anthropic SDK"
```

If pip install failed, the workflow needs network access. Check if:
- Organization has network restrictions
- Runner has internet access

#### Cause 8.2: Wrong Python version
**Problem:** Python 2.x instead of 3.x

**Solution:** Workflow already specifies Python 3.11. Verify:
```bash
gh run view <run-id> --log | grep "Setup Python"
```

---

### Error 9: "Response too long / truncated"

**Symptoms:**
- Bot responds but output is cut off
- Response ends mid-sentence
- Log shows: `Response truncated to 4096 tokens`

**Root Causes & Solutions:**

#### Cause 9.1: Large PR needs more detail
**Problem:** Claude's response is longer than 4096 tokens

**Solution:** Be more specific in your request:

Instead of:
```
@claude review
```

Use:
```
@claude review focusing on security issues only
```

Or split into multiple requests:
```
@claude review the authentication module
# Wait for response, then:
@claude review the database module
```

#### Cause 9.2: Max tokens limit
**Problem:** Workflow limits output to 4096 tokens

**Solution:** Edit workflow to increase limit:

```yaml
max_tokens=8192,  # Change from 4096
```

**Note:** Higher token limit = higher cost (~2x)

---

### Error 10: "Reactions not appearing"

**Symptoms:**
- Workflow runs successfully
- Comment is posted
- But no 👀 or 🚀 reactions

**Diagnosis:**
```bash
# Check workflow logs for reaction steps
gh run view <run-id> --log | grep "Add reaction"
```

**Root Causes & Solutions:**

#### Cause 10.1: Permission issues
**Solution:** Same as Error 6 - check workflow permissions

#### Cause 10.2: GitHub API rate limit
**Problem:** Too many API calls in short time

**Solution:** Wait 1 hour and retry

#### Cause 10.3: Reaction step failed silently
**Solution:** Check workflow logs:
```bash
gh run view <run-id> --log | grep -A 5 "reaction"
```

If reaction step failed, the comment will still be posted. This is **cosmetic only** - bot still works.

---

## 🔧 Advanced Diagnostics

### Check Workflow Syntax

```bash
# Validate workflow YAML
yamllint .github/workflows/claude-autofix-bot.yml

# Or use GitHub's API
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml
```

### Test API Key Locally

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-xxx

# Test with curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Expected output: JSON response with Claude's message
# Error output: 401 Unauthorized = invalid key
```

### Test with Python Script

```python
# test_claude.py
import os
from anthropic import Anthropic

api_key = os.environ.get('ANTHROPIC_API_KEY')
print(f"Testing with key: {api_key[:20]}...")

try:
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ API call successful!")
    print(f"Response: {message.content[0].text}")
except Exception as e:
    print(f"❌ API call failed: {e}")
```

```bash
# Run test
python3 test_claude.py
```

### Check GitHub Actions Status

```bash
# Check if Actions are enabled
gh api repos/{owner}/{repo} | jq .has_issues,.has_projects,.has_discussions

# Check Actions permissions
gh api repos/{owner}/{repo}/actions/permissions

# List all secrets (names only, not values)
gh secret list

# Check workflow runs statistics
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml/runs \
  --jq '{total: .total_count, successful: [.workflow_runs[].conclusion] | map(select(. == "success")) | length}'
```

---

## 🐛 Debugging Workflow Locally

You can't run GitHub Actions locally, but you can test the Python script:

### Extract and Test Python Code

1. Copy the Python script from `.github/workflows/claude-autofix-bot.yml`
2. Save to `test_claude_bot.py`
3. Run locally:

```python
# test_claude_bot.py
import os
from anthropic import Anthropic

# Mock data
file_contents = """
### File: test.py

```python
def hello():
    print("Hello")
```
"""

client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Review this code:\n\n{file_contents}"
    }]
)

print(message.content[0].text)
```

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
python3 test_claude_bot.py
```

---

## 📊 Monitoring & Metrics

### Track Success Rate

```bash
# Get last 50 runs
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml/runs?per_page=50 \
  | jq '[.workflow_runs[].conclusion] | group_by(.) | map({(.[0]): length}) | add'

# Output example:
# {
#   "success": 45,
#   "failure": 3,
#   "cancelled": 2
# }
```

### Track Usage Costs

```bash
# Count API calls this month
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml/runs \
  | jq '.workflow_runs | map(select(.created_at | startswith("2025-11"))) | length'

# Estimate cost (multiply by ~$0.03 per run)
echo "$(gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml/runs | jq '.workflow_runs | map(select(.created_at | startswith("2025-11"))) | length') * 0.03" | bc
```

### Monitor Response Times

```bash
# Average workflow duration
gh api repos/{owner}/{repo}/actions/workflows/claude-autofix-bot.yml/runs \
  | jq '[.workflow_runs[].run_duration_ms] | add / length / 1000'

# Output: Average seconds per run
```

---

## 🆘 Still Stuck?

### Step 1: Collect Debug Info

Run this script to gather diagnostic information:

```bash
#!/bin/bash
# debug_claude_bot.sh

echo "=== Claude Bot Diagnostics ==="
echo ""

echo "1. Workflow file exists:"
ls -la .github/workflows/claude-autofix-bot.yml || echo "❌ NOT FOUND"
echo ""

echo "2. Recent workflow runs:"
gh run list --workflow=claude-autofix-bot.yml --limit 5
echo ""

echo "3. Secrets configured:"
gh secret list | grep ANTHROPIC || echo "❌ ANTHROPIC_API_KEY not found"
echo ""

echo "4. Repository permissions:"
gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/permissions | jq .default_workflow_permissions
echo ""

echo "5. Test API key:"
if [ -n "$ANTHROPIC_API_KEY" ]; then
  curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"test"}]}' \
    | jq .type
else
  echo "❌ ANTHROPIC_API_KEY not set"
fi
echo ""

echo "6. Last workflow run logs:"
LAST_RUN=$(gh run list --workflow=claude-autofix-bot.yml --limit 1 --json databaseId -q '.[0].databaseId')
if [ -n "$LAST_RUN" ]; then
  gh run view $LAST_RUN --log-failed | tail -50
else
  echo "❌ No runs found"
fi
```

```bash
chmod +x debug_claude_bot.sh
./debug_claude_bot.sh > debug_output.txt
```

### Step 2: Share Debug Info

Create a GitHub issue with the debug output:

```bash
gh issue create --title "Claude Bot not working" --body "$(cat debug_output.txt)"
```

### Step 3: Check GitHub Status

```bash
# Check if GitHub Actions is having issues
curl -s https://www.githubstatus.com/api/v2/status.json | jq .status.description
```

---

## 📞 Get Help

1. **GitHub Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
2. **Workflow Logs:** Actions tab → Claude Auto-Fix Bot → View logs
3. **Anthropic Status:** https://status.anthropic.com
4. **GitHub Actions Status:** https://www.githubstatus.com

---

## ✅ Prevention Checklist

Before using the bot, verify:

- [ ] `ANTHROPIC_API_KEY` is set in GitHub Secrets
- [ ] API key has credits remaining
- [ ] Workflow permissions are "Read and write"
- [ ] "Allow GitHub Actions to create PRs" is checked
- [ ] Workflow file exists: `.github/workflows/claude-autofix-bot.yml`
- [ ] You're commenting on a **Pull Request** (not Issue)
- [ ] You're using `@claude` (correct spelling, lowercase)
- [ ] PR has actual code changes (not empty)

---

**Last Updated:** 2025-11-04
**Version:** 1.0.0
