# Claude Auto-Fix Bot - Quick Setup

Get the `@claude` bot running in your repository in 5 minutes.

---

## 🎯 Prerequisites

1. ✅ GitHub repository with Pull Requests enabled
2. ✅ Anthropic API key (get free at https://console.anthropic.com)
3. ✅ Repository admin access (to set secrets)

---

## 📋 Setup Steps

### Step 1: Get Anthropic API Key (2 minutes)

1. Go to https://console.anthropic.com/settings/keys
2. Click **"Create Key"**
3. Copy the key (starts with `sk-ant-`)
4. Keep it safe! You'll need it in Step 2

**Cost:** Free tier includes $5 credits (enough for ~250 PR reviews)

---

### Step 2: Add GitHub Secret (1 minute)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Set:
   - Name: `ANTHROPIC_API_KEY`
   - Secret: `sk-ant-xxx` (paste your key from Step 1)
5. Click **"Add secret"**

**Screenshot:**
```
Settings → Secrets → Actions → New repository secret
┌─────────────────────────────────────────┐
│ Name: ANTHROPIC_API_KEY                 │
│ Secret: sk-ant-api03-xxxxx              │
│                                         │
│          [Add secret]                   │
└─────────────────────────────────────────┘
```

---

### Step 3: Enable Workflow Permissions (1 minute)

1. Still in **Settings**, go to **Actions** → **General**
2. Scroll to **"Workflow permissions"**
3. Select: **"Read and write permissions"** ✅
4. Check: **"Allow GitHub Actions to create and approve pull requests"** ✅
5. Click **"Save"**

**Screenshot:**
```
Settings → Actions → General → Workflow permissions
┌─────────────────────────────────────────┐
│ ○ Read repository contents and packages│
│ ● Read and write permissions           │
│ ✓ Allow GitHub Actions to create PRs   │
│                                         │
│          [Save]                         │
└─────────────────────────────────────────┘
```

---

### Step 4: Verify Workflow Exists (30 seconds)

The workflow file should already be in your repository at:
```
.github/workflows/claude-autofix-bot.yml
```

If not, copy it from this commit!

To verify:
```bash
ls .github/workflows/claude-autofix-bot.yml
# Should output: .github/workflows/claude-autofix-bot.yml
```

---

### Step 5: Test the Bot! (1 minute)

1. Create or open any Pull Request
2. Add a comment:
   ```
   @claude review
   ```
3. Watch for reactions:
   - 👀 = Bot acknowledged your request
   - 🚀 = Bot finished successfully
   - 😕 = Bot encountered an error

4. Wait ~30-60 seconds for Claude's response

---

## ✅ Verification Checklist

- [ ] Anthropic API key created
- [ ] `ANTHROPIC_API_KEY` secret added to GitHub
- [ ] Workflow permissions set to "Read and write"
- [ ] "Allow GitHub Actions to create PRs" checked
- [ ] Workflow file exists: `.github/workflows/claude-autofix-bot.yml`
- [ ] Test comment posted on a PR
- [ ] Bot responded successfully

---

## 🎉 You're Done!

Now you can use `@claude` in any Pull Request!

Try these commands:
```
@claude fix          # Fix bugs
@claude debug        # Debug issues
@claude test         # Generate tests
@claude review       # Code review
@claude security     # Security audit
@claude optimize     # Performance tips
```

---

## 🐛 Troubleshooting

### Problem: Bot doesn't respond

**Check:**
```bash
# Verify secret is set
gh secret list | grep ANTHROPIC_API_KEY

# Check workflow runs
gh run list --workflow=claude-autofix-bot.yml

# View logs
gh run view --log-failed
```

**Common issues:**
1. Secret name typo (must be exactly `ANTHROPIC_API_KEY`)
2. Workflow permissions not enabled
3. Comment on an Issue instead of PR
4. Typo in `@claude` mention

---

### Problem: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Go to Settings → Secrets → Actions
2. Verify `ANTHROPIC_API_KEY` exists
3. If not, add it again
4. Retry by commenting again

---

### Problem: "Workflow permissions error"

**Solution:**
1. Go to Settings → Actions → General
2. Set "Read and write permissions"
3. Check "Allow GitHub Actions to create PRs"
4. Click Save
5. Retry the workflow

---

### Problem: Bot responds but response is empty

**Check API key:**
```bash
# Test API key locally
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

If you get an error, your API key may be invalid or expired.

---

## 💡 Next Steps

### 1. Customize Prompts

Edit `.github/workflows/claude-autofix-bot.yml` to adjust how Claude responds.

### 2. Add Custom Commands

Add your own command patterns in the workflow:
```yaml
elif echo "$COMMENT" | grep -qi "@claude refactor"; then
  echo "command=refactor" >> $GITHUB_OUTPUT
  echo "task=Suggest refactoring improvements..." >> $GITHUB_OUTPUT
```

### 3. Integrate with CI/CD

Trigger Claude automatically after test failures:
```yaml
on:
  workflow_run:
    workflows: ["Tests"]
    types: [completed]
```

---

## 📚 Learn More

- [Full Usage Guide](/docs/CLAUDE_BOT_GUIDE.md) - Complete documentation
- [Prompt Library](/docs/PROMPT_LIBRARY_SYSTEM.md) - Context engineering
- [Anthropic Docs](https://docs.anthropic.com/claude/reference/messages_post) - API reference

---

## 🆘 Still Having Issues?

1. Check workflow logs:
   ```bash
   gh run list --workflow=claude-autofix-bot.yml
   gh run view <run-id> --log
   ```

2. File a bug:
   https://github.com/jgtolentino/insightpulse-odoo/issues

3. Ask Claude for help:
   ```
   @claude help
   ```

---

## 🎊 Success!

You now have an AI pair programmer that reviews code, fixes bugs, and generates tests automatically!

**Time saved per PR:** ~30-60 minutes
**Cost per review:** ~$0.02-0.05
**ROI:** 🚀 Priceless

Enjoy your new AI teammate! 🤖
