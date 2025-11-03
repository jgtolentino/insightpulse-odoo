# GitHub Actions Workflows - Setup Guide

This document explains how to set up the AI Auto-Commit workflow with DigitalOcean deployment automation.

---

## 🤖 AI Auto-Commit Workflow

**File**: `.github/workflows/ai-auto-commit.yml`

### What It Does

1. **Auto-commits** any generated artifacts (from AI, builds, etc.)
2. **Creates deployment notifications** as GitHub issues
3. **Triggers automatic deployments** to DigitalOcean App Platform
4. **Monitors deployment status** and reports back

### Workflow Triggers

- **On push to `main` branch**: Automatically runs after any commit
- **Manual trigger**: Via GitHub Actions UI (workflow_dispatch)

---

## 🔐 Required Secrets

You need to configure these secrets in your GitHub repository settings:

### GitHub App Secrets

1. **`APP_ID`** - Your GitHub App ID
2. **`PRIVATE_KEY`** - GitHub App private key (PEM format)
3. **`INSTALLATION_ID`** - Installation ID for your organization/repo

### DigitalOcean Secrets

4. **`DO_API_TOKEN`** - DigitalOcean API token with read/write access
5. **`ODOO_APP_ID`** - Odoo App Platform app ID
6. **`SUPERSET_APP_ID`** - Superset App Platform app ID

---

## 📋 Step-by-Step Setup

### Step 1: Create a GitHub App

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Click **"New GitHub App"**
3. Configure:
   - **Name**: `pulser-hub-bot` (or your choice)
   - **Homepage URL**: `https://insightpulseai.net`
   - **Webhook**: Uncheck "Active"

4. **Permissions** (Repository):
   - Contents: **Read & Write**
   - Issues: **Read & Write**
   - Pull Requests: **Read & Write**
   - Metadata: **Read-only**

5. **Where can this GitHub App be installed?**
   - Select "Only on this account"

6. Click **"Create GitHub App"**

7. **Note the App ID** (you'll see it at the top of the page)

8. **Generate a private key**:
   - Scroll down to "Private keys"
   - Click "Generate a private key"
   - Save the downloaded `.pem` file securely

### Step 2: Install the GitHub App

1. Go to your GitHub App settings
2. Click **"Install App"** in the left sidebar
3. Select your organization/account
4. Choose **"Only select repositories"** → Select `insightpulse-odoo`
5. Click **"Install"**
6. **Note the Installation ID** from the URL:
   ```
   https://github.com/settings/installations/12345678
   #                                          ^^^^^^^^
   #                                          This is your INSTALLATION_ID
   ```

### Step 3: Get DigitalOcean Credentials

#### DigitalOcean API Token

1. Go to [DigitalOcean API Tokens](https://cloud.digitalocean.com/account/api/tokens)
2. Click **"Generate New Token"**
3. Name: `GitHub Actions - InsightPulse`
4. Scopes: **Read & Write**
5. Click **"Generate Token"**
6. **Copy the token** (you won't see it again!)

#### Get App IDs

```bash
# Install doctl if not already installed
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate
doctl auth init

# List your apps
doctl apps list

# Get Odoo app ID
doctl apps list --format ID,Spec.Name | grep odoo-saas-platform
# Example output: abc123def456    odoo-saas-platform

# Get Superset app ID
doctl apps list --format ID,Spec.Name | grep superset-analytics
# Example output: ghi789jkl012    superset-analytics
```

### Step 4: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each:

#### Add GitHub App Secrets

**APP_ID**:
```
123456
```

**INSTALLATION_ID**:
```
12345678
```

**PRIVATE_KEY**:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
... (paste entire contents of .pem file)
...
-----END RSA PRIVATE KEY-----
```

#### Add DigitalOcean Secrets

**DO_API_TOKEN**:
```
dop_v1_abc123def456...
```

**ODOO_APP_ID**:
```
abc123def456
```

**SUPERSET_APP_ID**:
```
ghi789jkl012
```

---

## 🧪 Testing the Workflow

### Test 1: Manual Trigger

1. Go to **Actions** tab in your repository
2. Select **"AI Auto Commit & Deploy"** workflow
3. Click **"Run workflow"** → Select `main` branch → **"Run workflow"**
4. Watch the workflow run in real-time

### Test 2: Automatic Trigger

1. Make a small change to any file
2. Commit and push to `main` branch
3. The workflow will run automatically
4. Check the **Actions** tab for status

### Expected Results

✅ **Success indicators**:
- Workflow completes without errors
- GitHub issue created with deployment notification
- DigitalOcean deployments triggered
- Deployment status monitored and reported

❌ **Common issues**:
- **403 Forbidden**: Check GitHub App permissions
- **401 Unauthorized**: Verify API tokens
- **App ID not found**: Double-check app IDs
- **Deployment already in progress**: Wait for previous deployment to finish

---

## 📊 Workflow Outputs

### GitHub Issue Format

When the workflow runs, it creates an issue like this:

```markdown
## 🤖 AI Auto Commit - 2025-11-02 14:30 UTC

**Commit**: a1b2c3d
**Author**: pulser-hub-bot
**Message**: AI: sync generated artifacts - 2025-11-02 14:30:00 UTC
**Time**: 2025-11-02 14:30:00 UTC

### Changes
3 files changed
- 45 additions
- 12 deletions

### Deployment Status
Deployments triggered automatically for:
- Odoo ERP
- Superset Analytics
- PaddleOCR Service

[View Commit](https://github.com/...)
```

Then adds a comment with deployment results:

```markdown
✅ **Deployment Complete**

### Deployment Summary
- **Odoo ERP**: Deployment triggered
- **Superset Analytics**: Deployment triggered
- **Workflow**: success

Check the Actions tab for detailed logs.
```

---

## 🔄 Deployment Flow

```
┌─────────────────┐
│ Push to main    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detect changes  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Auto-commit     │
│ (if needed)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create issue    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trigger DO      │
│ deployments     │
└────────┬────────┘
         │
         ├─► Odoo ERP
         ├─► Superset
         └─► (Future: PaddleOCR)
         │
         ▼
┌─────────────────┐
│ Monitor status  │
│ (up to 10 min)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Report results  │
│ & close issue   │
└─────────────────┘
```

---

## 🛠️ Customization

### Change Commit Message Format

Edit the workflow file:

```yaml
- name: Commit & Push via pulser-hub
  run: |
    # Change this line:
    git commit -m "AI: sync generated artifacts - ${TIMESTAMP}"

    # To your preferred format:
    git commit -m "chore: automated sync [skip ci]"
```

### Add More Deployments

Add a new step after the existing deployment steps:

```yaml
- name: Trigger PaddleOCR Deployment
  if: steps.changes.outputs.has_changes == 'true' && success()
  env:
    DO_API_TOKEN: ${{ secrets.DO_API_TOKEN }}
  run: |
    # SSH into PaddleOCR droplet and pull latest changes
    ssh root@ocr.insightpulseai.net "cd /opt/paddleocr && git pull && docker-compose up -d"
```

### Disable Automatic Deployments

Comment out or remove the deployment steps:

```yaml
# - name: Trigger Odoo Deployment
#   if: steps.changes.outputs.has_changes == 'true' && success()
#   ...
```

### Add Slack Notifications

Add a step at the end:

```yaml
- name: Send Slack notification
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Deployment ${{ job.status }}: ${{ github.event.head_commit.message }}"
      }
```

---

## 📈 Monitoring & Logs

### View Workflow Runs

1. Go to **Actions** tab
2. Select **"AI Auto Commit & Deploy"**
3. Click on any run to see detailed logs

### View Deployment Status

**DigitalOcean Dashboard**:
1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click on your app (Odoo or Superset)
3. View **Deployments** tab

**Via CLI**:
```bash
# List recent deployments
doctl apps list-deployments <APP_ID>

# Get deployment details
doctl apps get-deployment <APP_ID> <DEPLOYMENT_ID>

# View logs
doctl apps logs <APP_ID> --type deploy
```

---

## 🔒 Security Best Practices

1. **Never commit secrets** to the repository
2. **Rotate API tokens** regularly (every 90 days)
3. **Use least-privilege permissions** for GitHub App
4. **Enable branch protection** for `main` branch
5. **Review workflow changes** in PRs before merging
6. **Monitor workflow runs** for suspicious activity
7. **Use secret scanning** (enabled by default on GitHub)

---

## 🐛 Troubleshooting

### Workflow Fails with "GitHub App authentication failed"

**Solution**:
1. Verify `APP_ID`, `INSTALLATION_ID`, and `PRIVATE_KEY` are correct
2. Check GitHub App has correct permissions
3. Ensure GitHub App is installed on the repository

### Deployment Triggers but Fails

**Solution**:
1. Check DigitalOcean deployment logs
2. Verify app IDs are correct: `doctl apps list`
3. Ensure API token has write permissions
4. Check if deployment is already in progress

### "No changes to commit"

**Expected behavior**: Workflow runs but skips commit if no changes detected.

### Deployment Takes Too Long

**Normal**: Deployments can take 5-10 minutes for DigitalOcean App Platform.

If it times out after 10 minutes:
1. Check DO dashboard for deployment status
2. Review build logs for errors
3. Consider increasing timeout in workflow

---

## 📚 Additional Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DigitalOcean API Documentation](https://docs.digitalocean.com/reference/api/)
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)

---

## 🆘 Support

If you encounter issues:

1. **Check workflow logs** in Actions tab
2. **Review this documentation** for setup steps
3. **Create an issue** in the repository
4. **Contact DevOps team**: devops@insightpulseai.net

---

**Last Updated**: 2025-11-02
**Version**: 1.0.0
**Maintained By**: InsightPulse DevOps Team
