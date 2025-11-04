# Claude Bot - Common Errors Reference

Quick reference for all error messages and their fixes.

---

## 🚨 Error Quick Index

| Error Code | Error Message | Quick Fix |
|------------|---------------|-----------|
| E001 | ANTHROPIC_API_KEY not found | [Add secret](#e001) |
| E002 | 401 Unauthorized | [Invalid API key](#e002) |
| E003 | 429 Too Many Requests | [Rate limit](#e003) |
| E004 | 403 Forbidden (comment) | [Permissions](#e004) |
| E005 | Workflow timeout | [Add timeout](#e005) |
| E006 | ModuleNotFoundError | [Install failed](#e006) |
| E007 | No files found | [Empty PR](#e007) |
| E008 | Bot doesn't respond | [Check trigger](#e008) |
| E009 | Response truncated | [Reduce scope](#e009) |
| E010 | Reactions missing | [Cosmetic only](#e010) |

---

## E001: ANTHROPIC_API_KEY not found

**Error Message:**
```
Error: The secret `ANTHROPIC_API_KEY` was not found
```

**Quick Fix:**
```bash
gh secret set ANTHROPIC_API_KEY
# Paste your key: sk-ant-xxx
```

**Web UI Fix:**
1. Settings → Secrets → Actions
2. New repository secret
3. Name: `ANTHROPIC_API_KEY`
4. Value: `sk-ant-xxx`

---

## E002: 401 Unauthorized

**Error Message:**
```
Error: 401 Unauthorized
Invalid API key provided
```

**Quick Fix:**
1. Get new key: https://console.anthropic.com/settings/keys
2. Update secret:
   ```bash
   gh secret set ANTHROPIC_API_KEY
   ```

**Test key:**
```bash
curl -H "x-api-key: sk-ant-xxx" \
  https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

---

## E003: 429 Too Many Requests

**Error Message:**
```
Error: 429 Too Many Requests
Rate limit exceeded
```

**Quick Fix:**
- Wait 1 hour
- Upgrade to paid tier

**Prevention:**
Add rate limiting to workflow:
```yaml
- name: Rate limit
  run: sleep 5
```

---

## E004: 403 Forbidden (creating comment)

**Error Message:**
```
Error: Resource not accessible by integration
403 Forbidden
```

**Quick Fix:**
1. Settings → Actions → General
2. ✅ Read and write permissions
3. ✅ Allow GitHub Actions to create PRs
4. Save

**Verify:**
```bash
gh api repos/{owner}/{repo}/actions/permissions | jq .default_workflow_permissions
# Should be: "write"
```

---

## E005: Workflow timeout

**Error Message:**
```
The job running on runner has exceeded the maximum execution time of 360 minutes
```

**Quick Fix:**
Add timeout to workflow step:
```yaml
- name: Call Claude API
  timeout-minutes: 5
```

---

## E006: ModuleNotFoundError

**Error Message:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Quick Fix:**
Check workflow logs:
```bash
gh run view <run-id> --log | grep "Install Anthropic"
```

If pip install failed, check:
- Network connectivity
- PyPI access
- Python version (must be 3.7+)

---

## E007: No files found / collected=0

**Error Message:**
```
collected=0 files
No code changes detected
```

**Quick Fix:**
1. Push commits to PR:
   ```bash
   git push origin feature-branch
   ```
2. Verify PR has changes:
   ```bash
   gh pr view 123 --json files
   ```

**Common causes:**
- Draft PR with no commits
- All files are binary/images
- All files > 50KB

---

## E008: Bot doesn't respond

**Symptoms:**
- No reaction (👀)
- No workflow run
- Complete silence

**Quick Diagnosis:**
```bash
# Check workflow is enabled
gh workflow list | grep claude

# Check recent runs
gh run list --workflow=claude-autofix-bot.yml
```

**Common causes:**
1. Commented on Issue (not PR)
2. Typo: `@cluade` instead of `@claude`
3. Workflow disabled
4. Permissions not set

**Quick Fix:**
```bash
# Enable workflow
gh workflow enable claude-autofix-bot.yml

# Verify permissions
gh api repos/{owner}/{repo}/actions/permissions
```

---

## E009: Response truncated

**Error Message:**
```
[Response truncated to 4096 tokens]
```

**Not really an error** - just a limit.

**Quick Fix:**
Be more specific:
```
# Instead of:
@claude review

# Use:
@claude review focusing on security issues
```

**Or split requests:**
```
@claude review auth.py
# Then in next comment:
@claude review database.py
```

---

## E010: Reactions missing

**Symptoms:**
- Bot posts comment successfully
- But no 👀 or 🚀 reactions

**This is cosmetic** - bot still works!

**Causes:**
- Permission issues (rare)
- GitHub API rate limit
- Reaction step failed silently

**Check logs:**
```bash
gh run view <run-id> --log | grep "reaction"
```

**Fix (optional):**
Same as E004 - check permissions

---

## 🔧 Workflow-Specific Errors

### Parse Error: YAML syntax

**Error Message:**
```
Invalid workflow file
Error parsing .github/workflows/claude-autofix-bot.yml
```

**Quick Fix:**
```bash
# Validate YAML
yamllint .github/workflows/claude-autofix-bot.yml

# Or use online validator
# Copy file content to: https://www.yamllint.com/
```

### Git Checkout Failed

**Error Message:**
```
Error: fatal: couldn't find remote ref
```

**Quick Fix:**
Branch doesn't exist or was deleted.

```bash
# Check branch exists
gh pr view 123 --json headRefName
```

### Python Script Syntax Error

**Error Message:**
```
SyntaxError: invalid syntax
  File "<stdin>", line X
```

**Quick Fix:**
Python syntax error in workflow script. Check:
- Quotes properly closed
- Indentation correct
- No special characters

View workflow around that line:
```bash
sed -n 'X,Y p' .github/workflows/claude-autofix-bot.yml
```

---

## 🐛 Debugging Commands

### Check Everything
```bash
# 1. Workflow exists
ls .github/workflows/claude-autofix-bot.yml

# 2. Secret exists
gh secret list | grep ANTHROPIC

# 3. Permissions
gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/permissions

# 4. Recent runs
gh run list --workflow=claude-autofix-bot.yml --limit 5

# 5. Last run logs
gh run view --log-failed
```

### Test API Key
```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"test"}]}' \
  | jq
```

### Full Diagnostic Script
```bash
# Save as: debug.sh
#!/bin/bash
echo "1. Workflow:" && ls -l .github/workflows/claude-autofix-bot.yml
echo "2. Secrets:" && gh secret list | grep ANTHROPIC
echo "3. Permissions:" && gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/permissions | jq .default_workflow_permissions
echo "4. Recent runs:" && gh run list --workflow=claude-autofix-bot.yml --limit 3
echo "5. Last error:" && gh run view --log-failed | tail -20
```

---

## 📋 Pre-Flight Checklist

Before asking "why doesn't it work?", verify:

- [ ] Secret `ANTHROPIC_API_KEY` is set
- [ ] API key is valid and has credits
- [ ] Workflow permissions = "Read and write"
- [ ] "Allow Actions to create PRs" = checked
- [ ] Commenting on a **Pull Request** (not Issue)
- [ ] Using `@claude` (not @Claude, @cluade)
- [ ] PR has actual file changes
- [ ] Workflow file exists and is valid YAML

---

## 🆘 Emergency Fixes

### Nuclear Option: Reset Everything

```bash
# 1. Remove secret
gh secret remove ANTHROPIC_API_KEY

# 2. Disable workflow
gh workflow disable claude-autofix-bot.yml

# 3. Wait 5 minutes

# 4. Add secret again
gh secret set ANTHROPIC_API_KEY

# 5. Enable workflow
gh workflow enable claude-autofix-bot.yml

# 6. Test on a PR
# Comment: @claude help
```

### Verify Installation

```bash
# Check workflow is correctly installed
cat .github/workflows/claude-autofix-bot.yml | head -20

# Should show:
# name: Claude Auto-Fix Bot
# on:
#   issue_comment:
```

---

## 📊 Status Checks

### GitHub Actions Status
```bash
curl -s https://www.githubstatus.com/api/v2/status.json | jq
```

### Anthropic API Status
```bash
curl -s https://status.anthropic.com/api/v2/status.json | jq
```

### Repository Actions Enabled
```bash
gh api repos/{owner}/{repo} | jq '.has_issues, .has_projects, .has_discussions, .disabled'
```

---

## 💡 Pro Tips

### Enable Debug Logging

Add to workflow:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### Test Locally

Extract Python code and run:
```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "test"}]
)
print(response.content[0].text)
```

---

**Quick Links:**
- [Full Troubleshooting Guide](TROUBLESHOOTING.md)
- [Setup Guide](SETUP.md)
- [Usage Guide](GUIDE.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Anthropic API Docs](https://docs.anthropic.com)
