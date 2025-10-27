# AI Code Review Setup Guide

## 1. Add OpenAI API Key Secret

### Repository Secret (Recommended)
1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Set:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key (starts with `sk-`)

### Organization Secret (Optional)
If you want to use the same key across multiple repositories:
1. Go to your GitHub organization → **Settings** → **Secrets** → **Actions**
2. Click **New organization secret**
3. Set:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key
4. Select this repository in the repository access section

## 2. Workflow Configuration

The AI Code Review workflow (`ai-code-review.yml`) is configured with:

### Security Features
- **Fork Protection**: Only runs on PRs from branches within this repository
- **Safe Checkout**: For fork PRs, only checks out the base branch (no untrusted code execution)
- **Manual Trigger**: Available for fork PRs via workflow dispatch

### Environment Variables
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  LANGUAGE: en
  EXCLUDE: "*.po,*.pot,*.mo,*.pyc,__pycache__/,*.log,*.sql,*.csv,*.xml"
  MODEL: gpt-4
```

## 3. Fork PR Behavior

### Security Approach
GitHub doesn't expose repository secrets to forked PRs for security reasons. Our workflow handles this by:

1. **Same-repo PRs**: Full AI review with OpenAI API
2. **Fork PRs**: Security notice comment + manual review option

### Options for Fork Contributors
1. **Create branch in this repository** (recommended)
2. **Request manual review** from maintainers
3. **Wait for manual security review**

## 4. Manual Trigger

For fork PRs or specific cases, you can manually trigger the AI review:

1. Go to **Actions** → **AI Code Review**
2. Click **Run workflow**
3. Select branch and run

## 5. Verification

### Test the Setup
1. Create a PR from a branch in this repository
2. The AI review should automatically run
3. Check the workflow logs for "OPENAI_API_KEY not set" errors

### Expected Behavior
- ✅ Same-repo PRs: AI review comments appear
- ✅ Fork PRs: Security notice comment appears
- ✅ Manual trigger: AI review runs on demand

## 6. Troubleshooting

### Common Issues

**"OPENAI_API_KEY not set"**
- Check if the secret is properly configured
- Verify the secret name matches exactly: `OPENAI_API_KEY`

**Workflow not running on PRs**
- Check if the PR is from a fork (won't run automatically)
- Verify branch restrictions in workflow configuration

**No AI comments appearing**
- Check OpenAI API key validity
- Verify the model (`gpt-4`) is available in your OpenAI account
- Review workflow logs for errors

## 7. Cost Management

The workflow uses GPT-4 which has associated costs:
- Monitor usage in your OpenAI account dashboard
- Consider setting usage limits
- Use `gpt-3.5-turbo` for lower costs if needed (modify `MODEL` in workflow)

## 8. Customization

### Modify Review Scope
Edit the `EXCLUDE` pattern in the workflow:
```yaml
EXCLUDE: "*.po,*.pot,*.mo,*.pyc,__pycache__/,*.log,*.sql,*.csv,*.xml"
```

### Change AI Model
```yaml
MODEL: gpt-3.5-turbo  # For lower cost
```

### Adjust Review Language
```yaml
LANGUAGE: en  # Options: en, zh, ja, etc.
