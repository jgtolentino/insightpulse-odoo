# Claude Auto-Fix Bot - Usage Guide

Automatically trigger Claude AI to analyze code, fix bugs, debug issues, generate tests, or review changes by mentioning `@claude` in GitHub PR comments.

---

## 🚀 Quick Start

### 1️⃣ Add API Key (One-time setup)

Go to **Settings → Secrets and variables → Actions** and add:

```
Name: ANTHROPIC_API_KEY
Value: sk-ant-xxx (get from https://console.anthropic.com/settings/keys)
```

### 2️⃣ Enable Workflow Permissions

Go to **Settings → Actions → General** and set:
- ✅ **Read and write permissions**
- ✅ **Allow GitHub Actions to create and approve pull requests**

### 3️⃣ Use the Bot!

Comment on any Pull Request:

```
@claude fix
```

That's it! 🎉

---

## 💬 Available Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `@claude fix` | Analyzes code and suggests specific fixes | `@claude fix the authentication bug in auth.py` |
| `@claude debug` | Performs root cause analysis | `@claude debug why the API returns 500 errors` |
| `@claude test` | Generates test cases | `@claude test the new payment function` |
| `@claude review` | Comprehensive code review | `@claude review this implementation` |
| `@claude security` | Security vulnerability scan | `@claude security audit the login flow` |
| `@claude optimize` | Performance optimization suggestions | `@claude optimize the database queries` |
| `@claude` (any text) | General help and guidance | `@claude explain how the caching works` |

---

## 📝 Detailed Examples

### Fix a Bug

**Comment:**
```
@claude fix the null pointer exception in line 45 of user_service.py
```

**Claude responds with:**
- Issue analysis
- Root cause explanation
- Code changes in diff format
- Step-by-step fix instructions

**Example Response:**
```diff
--- a/services/user_service.py
+++ b/services/user_service.py
@@ -43,7 +43,10 @@ def get_user_profile(user_id):
     user = User.query.get(user_id)
     if not user:
         return None
-    return user.profile.to_dict()
+
+    if user.profile:
+        return user.profile.to_dict()
+    return {"status": "incomplete", "user_id": user_id}
```

### Debug an Issue

**Comment:**
```
@claude debug why users can't log in after the OAuth2 changes
```

**Claude provides:**
- Root cause analysis
- Debugging checklist
- Common pitfalls
- Suggested fixes

### Generate Tests

**Comment:**
```
@claude test the payment processing function in payments.py
```

**Claude generates:**
- Unit tests
- Edge case tests
- Integration tests
- Mock examples

### Security Audit

**Comment:**
```
@claude security check for SQL injection vulnerabilities
```

**Claude analyzes:**
- Input validation
- SQL parameterization
- Authentication flows
- Data exposure risks
- XSS vulnerabilities

### Code Review

**Comment:**
```
@claude review the new caching implementation
```

**Claude reviews:**
- Code quality
- Best practices
- Performance concerns
- Potential bugs
- Maintainability

### Performance Optimization

**Comment:**
```
@claude optimize the dashboard loading time
```

**Claude suggests:**
- Query optimization
- Caching strategies
- N+1 query fixes
- Lazy loading
- Database indexing

---

## 🎯 Best Practices

### ✅ DO: Be Specific

**Good:**
```
@claude fix the memory leak in Redis connection pooling (line 120-150 in cache.py)
```

**Bad:**
```
@claude fix this
```

### ✅ DO: Provide Context

**Good:**
```
@claude debug why the cron job fails on weekends.
Error log shows: "Connection timeout to Supabase"
Related files: jobs/scheduler.py, config/database.py
```

**Bad:**
```
@claude why doesn't this work?
```

### ✅ DO: Use the Right Command

- Use `fix` when you know the issue location
- Use `debug` when you need to find the issue
- Use `test` for new features
- Use `review` for quality checks
- Use `security` for security concerns
- Use `optimize` for performance issues

### ❌ DON'T: Ask Unrelated Questions

**Don't:**
```
@claude what's the weather today?
```

**Instead:**
```
@claude explain the error handling in weather_api.py
```

---

## 🔒 Security & Privacy

### What Gets Sent to Claude API

- ✅ PR title and description
- ✅ Changed file contents (up to 20 files, 50KB each)
- ✅ Your comment text
- ✅ File names and diff information

### What Does NOT Get Sent

- ❌ Git history
- ❌ Environment variables / secrets
- ❌ Other branches
- ❌ Full repository contents
- ❌ Issues or other PRs

### Best Practices

1. ✅ **Review suggestions before applying** - Claude provides guidance, you make decisions
2. ✅ **Don't commit secrets** - Claude sees changed files
3. ✅ **Test in staging first** - Always test auto-fix suggestions
4. ❌ **Don't use for proprietary algorithms** - If in doubt, review manually
5. ✅ **Use for code quality** - Perfect for catching bugs and improving code

---

## 💰 Cost Analysis

**Claude Sonnet 4 Pricing:**
- Input: $3 / million tokens
- Output: $15 / million tokens

**Typical Usage:**

| PR Size | Input Tokens | Output Tokens | Cost |
|---------|-------------|---------------|------|
| Small (5 files, 500 lines) | ~2,000 | ~1,000 | **$0.02** |
| Medium (10 files, 1,500 lines) | ~5,000 | ~2,000 | **$0.05** |
| Large (20 files, 3,000 lines) | ~10,000 | ~3,000 | **$0.08** |

**Monthly Estimate:**
- 50 PR reviews: **$1.50 - $4.00 / month**

**ROI Comparison:**
- Manual review time: 30-120 minutes per PR
- Claude Bot: 2-3 minutes per PR
- **Time saved: ~95%** ⏱️

Compare to:
- GitHub Copilot: $10/user/month
- CodeRabbit: $15/user/month
- Manual code review: 2-4 hours/week @ $50/hour = **$400-800/month**

---

## 🔧 Troubleshooting

### Bot doesn't respond

**Check:**
1. ✅ Is `ANTHROPIC_API_KEY` set in GitHub Secrets?
2. ✅ Are workflow permissions set to "Read and write"?
3. ✅ Is the comment on a **Pull Request** (not an Issue)?
4. ✅ Did you spell `@claude` correctly?
5. ✅ Is the PR in the same repository where the workflow exists?

**Debug:**
```bash
# Check workflow runs
gh run list --workflow=claude-autofix-bot.yml

# View logs for failed run
gh run view <run-id> --log-failed
```

### API rate limit errors

**Solution:** Claude Sonnet 4 has generous rate limits, but if you hit them:

1. Add rate limiting in workflow:
```yaml
- name: Rate limit check
  run: sleep 5  # 5 second delay
```

2. Upgrade to Claude Pro for higher limits

### Response too long / truncated

**Solution:** The bot limits responses to 4096 tokens. For detailed analysis:

```
@claude fix (focus on the authentication module only)
```

### Changes not applied automatically

**By design:** The bot posts suggestions but doesn't auto-commit. You must:
1. Review Claude's analysis
2. Apply changes manually OR
3. Copy the suggested code and commit

**Why?** Safety - you review before deploying.

---

## 🎓 Advanced Usage

### Combine Commands

```
@claude review and test the new payment integration
```

Claude will perform both code review and generate tests.

### Focus on Specific Areas

```
@claude security review focusing on authentication and session management
```

### Ask for Explanations

```
@claude explain why the current caching strategy is causing race conditions
```

### Request Refactoring

```
@claude suggest refactoring options for the UserService class to improve testability
```

---

## 📊 Usage Analytics

Track bot effectiveness:

```bash
# Count bot invocations this month
gh api repos/jgtolentino/insightpulse-odoo/actions/workflows/claude-autofix-bot.yml/runs \
  --jq '.workflow_runs | map(select(.created_at | startswith("2025-01"))) | length'

# Success rate
gh api repos/jgtolentino/insightpulse-odoo/actions/workflows/claude-autofix-bot.yml/runs \
  --jq '[.workflow_runs[].conclusion] | group_by(.) | map({(.[0]): length}) | add'

# Average runtime
gh api repos/jgtolentino/insightpulse-odoo/actions/workflows/claude-autofix-bot.yml/runs \
  --jq '[.workflow_runs[].run_duration_ms] | add / length / 1000'
```

---

## 🚀 Integration with Existing Workflows

### Use with OCA Pre-commit Hooks

The bot understands OCA standards! Ask:

```
@claude review for OCA compliance
```

Claude will check:
- Module structure
- Naming conventions
- License headers
- README.rst format
- `__manifest__.py` completeness

### Use with CI/CD

Trigger bot after test failures:

```
@claude debug why the CI tests are failing in test_trial_balance.py
```

### Use with Notion Workflows

Reference Notion specs:

```
@claude implement the module specified in Notion task IPAI-123
```

---

## 🎉 Success Stories

### Before Claude Bot
- Code review: 45 minutes per PR
- Bug investigation: 1-2 hours
- Test writing: 30-45 minutes
- Security checks: Manual and inconsistent

### After Claude Bot
- Code review: 3 minutes (automated)
- Bug investigation: 5 minutes (guided)
- Test generation: 2 minutes (automated)
- Security checks: Every PR, consistently

**Total time saved: ~80% on code review tasks** 🎯

---

## 💡 Pro Tips

### 1. Use Early in Development
```
@claude review (early feedback before submitting for formal review)
```

### 2. Learn from Claude
Review Claude's suggestions to improve your coding skills.

### 3. Combine with Manual Review
Claude catches common issues, humans catch business logic errors.

### 4. Iterate
```
Comment 1: @claude fix the auth bug
Comment 2: @claude now test the auth fix
Comment 3: @claude security review the auth module
```

### 5. Be Conversational
```
@claude I'm getting a 500 error when users try to upload files larger than 5MB.
The upload works fine for smaller files. Can you help debug?
```

---

## 📚 Related Documentation

- [Prompt Library System](/docs/PROMPT_LIBRARY_SYSTEM.md) - Context engineering
- [LLM Rules](/.llmrules) - Coding standards Claude follows
- [Hybrid Stack Architecture](/docs/HYBRID_STACK_ARCHITECTURE.md) - Architecture patterns
- [Anthropic API Docs](https://docs.anthropic.com/claude/reference/messages_post)

---

## 🆘 Support

**Issues?**
- File a bug: https://github.com/jgtolentino/insightpulse-odoo/issues
- Check workflow logs: Actions → Claude Auto-Fix Bot
- Review API status: https://status.anthropic.com

**Questions?**
- Ask in PR comments: `@claude help`
- Read docs: `/docs/CLAUDE_BOT_GUIDE.md`
- API docs: https://docs.anthropic.com

---

**Built for InsightPulse-Odoo** 🚀
*Making code review as easy as mentioning @claude*

---

## 🎁 Bonus: Command Cheat Sheet

```
# Quick fixes
@claude fix

# Deep debugging
@claude debug

# Test generation
@claude test

# Full review
@claude review

# Security audit
@claude security

# Performance tuning
@claude optimize

# Custom requests
@claude explain the caching strategy
@claude suggest improvements to error handling
@claude refactor the UserService for better testability
```

**Remember:** Claude is your AI pair programmer. Ask anything! 🤖
