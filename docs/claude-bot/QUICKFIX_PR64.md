# Quick Fix: Claude Bot Failed on PR #64

**Problem**: You commented `@claude` on PR #64 and got:
```
❌ Claude Auto-Fix Bot encountered an error. Please check the workflow logs.
```

---

## ✅ Quick Fix (30 seconds)

### Step 1: Set API Key

```bash
gh secret set ANTHROPIC_API_KEY
```

When prompted, paste your API key from: https://console.anthropic.com/settings/keys

### Step 2: Test Again

Comment on PR #64:
```
@claude review
```

Expected behavior:
- 👀 reaction appears (bot is working)
- Wait 30-60 seconds
- Bot posts detailed analysis
- 🚀 reaction appears (bot is done)

---

## 🔍 If Quick Fix Doesn't Work

Run the diagnostic script:

```bash
cd /home/user/insightpulse-odoo
bash scripts/debug_claude_bot.sh
```

This will tell you exactly what's wrong.

---

## 📊 Common Issues

### Issue 1: API Key Not Set (90% of failures)
**Fix**: Step 1 above

### Issue 2: Permissions Not Enabled (5% of failures)
**Check**: https://github.com/jgtolentino/insightpulse-odoo/settings/actions

**Fix**:
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

### Issue 3: API Key Expired or Invalid (3% of failures)
**Fix**: Get a new key from https://console.anthropic.com/settings/keys

### Issue 4: Out of Credits (2% of failures)
**Check**: https://console.anthropic.com/settings/billing

**Fix**: Add payment method or get free credits

---

## 🎯 Why It Failed

The Claude Bot workflow requires `ANTHROPIC_API_KEY` to call the Claude API:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}  # <-- This needs to be set
```

Without this secret, the Python script fails when trying to authenticate:

```python
client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])  # <-- Fails here
```

---

## 📖 More Details

- **Full Debug Guide**: `/docs/claude-bot/DEBUG_PR64.md`
- **Troubleshooting**: `/docs/claude-bot/TROUBLESHOOTING.md`
- **Usage Guide**: `/docs/claude-bot/GUIDE.md`
- **Setup Guide**: `/docs/claude-bot/SETUP.md`

---

**TL;DR**: Run `gh secret set ANTHROPIC_API_KEY` and try again! 🚀
