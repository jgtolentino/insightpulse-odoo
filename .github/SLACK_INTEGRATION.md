# GitHub Slack Integration for InsightPulse

**Version**: 1.0.0
**Date**: 2025-11-03
**Status**: Ready for Setup

---

## 🎯 Overview

This guide shows how to integrate GitHub with Slack for the InsightPulse platform, enabling real-time notifications for deployments, pull requests, issues, and commits directly in your Slack workspace.

---

## ✨ Key Features

### What You Can Do

1. **Repository Notifications**
   - Get notified about commits, PRs, issues, deployments
   - Customizable notification filters
   - Multiple channels for different teams

2. **Interactive Commands**
   - `/github subscribe owner/repo` - Subscribe to notifications
   - `/github unsubscribe owner/repo` - Unsubscribe
   - `/github open [issue|pr]` - Open issues/PRs from Slack
   - `/github close [issue|pr]` - Close from Slack

3. **Link Unfurling**
   - Automatically expand GitHub URLs with preview
   - See PR/issue details without leaving Slack

4. **Scheduled Reminders**
   - Get reminded about pending PR reviews
   - Daily/weekly summaries

5. **Deployment Notifications**
   - Real-time deployment status
   - Success/failure alerts
   - Direct links to logs

---

## 📋 Setup Steps

### Step 1: Install GitHub App in Slack

1. **Go to Slack App Directory**
   - Visit: https://slack.com/apps/A01BP7R4KNY-github
   - Or search for "GitHub" in Slack App Directory

2. **Add to Slack**
   - Click "Add to Slack"
   - Select your workspace
   - Authorize the app

3. **Authenticate**
   - The GitHub bot will send you a DM
   - Click "Connect GitHub account"
   - Sign in to GitHub
   - Authorize the Slack integration

### Step 2: Subscribe to Repository

In your Slack channel:

```
/github subscribe jgtolentino/insightpulse-odoo
```

**Choose Features**:
```
/github subscribe jgtolentino/insightpulse-odoo issues pulls commits releases deployments
```

**Recommended for DevOps Channel**:
```
/github subscribe jgtolentino/insightpulse-odoo deployments releases workflows
```

**Recommended for Dev Channel**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls commits reviews
```

### Step 3: Configure Notifications

**Filter by Labels**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls +label:"urgent"
```

**Filter by Branch**:
```
/github subscribe jgtolentino/insightpulse-odoo commits:main
```

**Exclude Bot Activity**:
```
/github subscribe jgtolentino/insightpulse-odoo -author:"dependabot"
```

---

## 🎨 Recommended Channel Setup

### #deployment-alerts

**Purpose**: Real-time deployment notifications

**Subscription**:
```
/github subscribe jgtolentino/insightpulse-odoo deployments workflows releases
```

**What You'll See**:
- ✅ Deployment started
- ✅ Deployment successful
- ❌ Deployment failed
- 📦 New releases
- 🔄 Workflow runs

### #pull-requests

**Purpose**: Code review notifications

**Subscription**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls reviews commits:main
```

**What You'll See**:
- 🔔 New PRs opened
- 💬 PR comments
- ✅ PR approvals
- 🚀 PR merged
- 📝 PR reviews requested

### #issues

**Purpose**: Bug reports and feature requests

**Subscription**:
```
/github subscribe jgtolentino/insightpulse-odoo issues +label:"bug" +label:"enhancement"
```

**What You'll See**:
- 🐛 New bugs reported
- ✨ Feature requests
- 💬 Issue comments
- ✅ Issues closed

### #github-feed (Optional)

**Purpose**: All repository activity

**Subscription**:
```
/github subscribe jgtolentino/insightpulse-odoo
```

---

## 🤖 Advanced: Custom Slack Notifications via Workflows

For more control, add custom Slack notifications to your GitHub Actions workflows.

### Update AI Auto-Commit Workflow

Edit `.github/workflows/ai-auto-commit.yml`:

```yaml
name: AI Auto Commit & Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  ai_ops:
    runs-on: ubuntu-latest
    # ... existing steps ...

    # Add at the beginning
    - name: Notify Slack - Deployment Started
      if: success()
      uses: slackapi/slack-github-action@v1.25.0
      with:
        payload: |
          {
            "text": "🚀 Deployment Started",
            "blocks": [
              {
                "type": "header",
                "text": {
                  "type": "plain_text",
                  "text": "🚀 InsightPulse Deployment Started"
                }
              },
              {
                "type": "section",
                "fields": [
                  {
                    "type": "mrkdwn",
                    "text": "*Commit:*\n${{ github.sha }}"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Branch:*\n${{ github.ref_name }}"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Author:*\n${{ github.actor }}"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Workflow:*\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Logs>"
                  }
                ]
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

    # ... existing deployment steps ...

    # Add after successful deployment
    - name: Notify Slack - Deployment Success
      if: success()
      uses: slackapi/slack-github-action@v1.25.0
      with:
        payload: |
          {
            "text": "✅ Deployment Successful",
            "blocks": [
              {
                "type": "header",
                "text": {
                  "type": "plain_text",
                  "text": "✅ InsightPulse Deployment Successful"
                }
              },
              {
                "type": "section",
                "fields": [
                  {
                    "type": "mrkdwn",
                    "text": "*Services Deployed:*\n• Odoo ERP\n• Superset Analytics"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Duration:*\n${{ job.duration }} minutes"
                  }
                ]
              },
              {
                "type": "actions",
                "elements": [
                  {
                    "type": "button",
                    "text": {
                      "type": "plain_text",
                      "text": "View Odoo"
                    },
                    "url": "https://insightpulseai.net/odoo"
                  },
                  {
                    "type": "button",
                    "text": {
                      "type": "plain_text",
                      "text": "View Superset"
                    },
                    "url": "https://insightpulseai.net/superset"
                  }
                ]
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

    # Add on failure
    - name: Notify Slack - Deployment Failed
      if: failure()
      uses: slackapi/slack-github-action@v1.25.0
      with:
        payload: |
          {
            "text": "❌ Deployment Failed",
            "blocks": [
              {
                "type": "header",
                "text": {
                  "type": "plain_text",
                  "text": "❌ InsightPulse Deployment Failed"
                }
              },
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "Deployment failed for commit ${{ github.sha }}"
                }
              },
              {
                "type": "section",
                "fields": [
                  {
                    "type": "mrkdwn",
                    "text": "*Branch:*\n${{ github.ref_name }}"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Author:*\n${{ github.actor }}"
                  }
                ]
              },
              {
                "type": "actions",
                "elements": [
                  {
                    "type": "button",
                    "text": {
                      "type": "plain_text",
                      "text": "View Logs"
                    },
                    "url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}",
                    "style": "danger"
                  }
                ]
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 🔑 Setup Slack Webhook

### Step 1: Create Incoming Webhook

1. **Go to Slack API**
   - Visit: https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name: "InsightPulse Deployments"
   - Select your workspace

2. **Enable Incoming Webhooks**
   - Click "Incoming Webhooks" in sidebar
   - Toggle "Activate Incoming Webhooks" to ON
   - Click "Add New Webhook to Workspace"
   - Select channel (e.g., #deployment-alerts)
   - Click "Allow"

3. **Copy Webhook URL**
   - Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)
   - Save it securely

### Step 2: Add to GitHub Secrets

```bash
# Via GitHub CLI
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Verify
gh secret list
```

**Or via GitHub UI**:
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `SLACK_WEBHOOK_URL`
4. Value: Your webhook URL
5. Click "Add secret"

---

## 📊 Notification Examples

### Deployment Started

```
🚀 InsightPulse Deployment Started

Commit: a1b2c3d
Branch: main
Author: pulser-hub-bot
Workflow: View Logs →
```

### Deployment Successful

```
✅ InsightPulse Deployment Successful

Services Deployed:
• Odoo ERP
• Superset Analytics

Duration: 8 minutes

[View Odoo] [View Superset]
```

### Deployment Failed

```
❌ InsightPulse Deployment Failed

Deployment failed for commit a1b2c3d

Branch: main
Author: pulser-hub-bot

[View Logs]
```

### Pull Request Opened

```
🔔 New Pull Request: feat: add mobile app integration

jgtolentino opened PR #42 in insightpulse-odoo

Description: Adds React Native mobile app with PaddleOCR integration

[View PR] [Review Changes]
```

---

## 🎯 Use Cases

### 1. DevOps Team Notifications

**Channel**: #deployment-alerts

**Setup**:
```
/github subscribe jgtolentino/insightpulse-odoo deployments workflows
```

**Benefits**:
- Immediate deployment status
- No need to check GitHub manually
- Team-wide visibility

### 2. Code Review Reminders

**Channel**: #pull-requests

**Setup**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls reviews
/github subscribe jgtolentino/insightpulse-odoo reminders:"https://github.com/jgtolentino/insightpulse-odoo"
```

**Benefits**:
- Get reminded about pending reviews
- Daily summaries of open PRs
- Faster code review cycles

### 3. Issue Tracking

**Channel**: #issues

**Setup**:
```
/github subscribe jgtolentino/insightpulse-odoo issues +label:"urgent" +label:"bug"
```

**Benefits**:
- Instant bug notifications
- Team awareness of critical issues
- Faster response times

### 4. Release Announcements

**Channel**: #releases

**Setup**:
```
/github subscribe jgtolentino/insightpulse-odoo releases
```

**Benefits**:
- Announce new versions
- Share release notes
- Coordinate rollouts

---

## 🔧 Advanced Features

### Scheduled Reminders

Get daily reminders about PRs needing review:

```
/github subscribe jgtolentino/insightpulse-odoo reminders:"https://github.com/jgtolentino/insightpulse-odoo"
```

**Customize Schedule**:
```
/github subscribe jgtolentino/insightpulse-odoo reminders:"https://github.com/jgtolentino/insightpulse-odoo" schedule:daily time:09:00
```

### Team-Specific Notifications

**Backend Team**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls +label:"backend"
```

**Frontend Team**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls +label:"frontend"
```

**Mobile Team**:
```
/github subscribe jgtolentino/insightpulse-odoo pulls +label:"mobile"
```

### Filter by Author

**Only Human Contributions** (exclude bots):
```
/github subscribe jgtolentino/insightpulse-odoo -author:"dependabot" -author:"pulser-hub-bot"
```

**Specific Team Members**:
```
/github subscribe jgtolentino/insightpulse-odoo commits +author:"jgtolentino"
```

---

## 🎨 Rich Notification Examples

### Custom Deployment Notification with Actions

```yaml
- name: Notify Slack with Rich Content
  uses: slackapi/slack-github-action@v1.25.0
  with:
    payload: |
      {
        "text": "Deployment Update",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Deployment Status*\n✅ All services deployed successfully"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "fields": [
              {
                "type": "mrkdwn",
                "text": "*Odoo ERP*\nVersion: 19.0.1\nStatus: ✅ Active"
              },
              {
                "type": "mrkdwn",
                "text": "*Superset*\nVersion: 3.0.0\nStatus: ✅ Active"
              },
              {
                "type": "mrkdwn",
                "text": "*PaddleOCR*\nVersion: 2.7.0\nStatus: ✅ Active"
              },
              {
                "type": "mrkdwn",
                "text": "*Traefik*\nVersion: 2.10\nStatus: ✅ Active"
              }
            ]
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "mrkdwn",
                "text": "Deployed at <!date^${{ github.event.head_commit.timestamp }}^{date_short_pretty} at {time}|${{ github.event.head_commit.timestamp }}>"
              }
            ]
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 📚 Useful Commands

### Subscription Management

```bash
# List subscriptions
/github subscribe list

# Unsubscribe from a repo
/github unsubscribe jgtolentino/insightpulse-odoo

# Unsubscribe from specific features
/github unsubscribe jgtolentino/insightpulse-odoo commits

# Show help
/github help
```

### Repository Management

```bash
# Open issue
/github open jgtolentino/insightpulse-odoo issues

# Close issue
/github close jgtolentino/insightpulse-odoo#42

# Reopen issue
/github reopen jgtolentino/insightpulse-odoo#42
```

### Search

```bash
# Search issues
/github search issues repo:jgtolentino/insightpulse-odoo is:open label:bug

# Search PRs
/github search prs repo:jgtolentino/insightpulse-odoo is:open review:required
```

---

## 🔒 Security & Privacy

### What GitHub Can Access in Slack

- ✅ Post messages in channels where invited
- ✅ Read channel names and topics
- ✅ No access to private messages
- ✅ No access to other channels

### What Slack Can Access in GitHub

- ✅ Repository metadata (name, description)
- ✅ Commits, PRs, issues (based on permissions)
- ✅ Actions workflow runs
- ✅ No access to private repos without authorization

### Best Practices

1. **Use separate channels** for different teams
2. **Filter notifications** to reduce noise
3. **Review permissions** regularly
4. **Use webhooks** for custom notifications
5. **Rotate webhook URLs** if compromised

---

## 🐛 Troubleshooting

### Not Receiving Notifications

**Check**:
1. Bot is invited to the channel
2. Subscription is active: `/github subscribe list`
3. Repository permissions are correct
4. Filters aren't too restrictive

**Fix**:
```
# Unsubscribe and re-subscribe
/github unsubscribe jgtolentino/insightpulse-odoo
/github subscribe jgtolentino/insightpulse-odoo
```

### Webhook Fails in Workflow

**Error**: `Error: Invalid webhook URL`

**Fix**:
```bash
# Verify secret exists
gh secret list

# Recreate webhook in Slack
# Update GitHub secret with new URL
gh secret set SLACK_WEBHOOK_URL --body "new-webhook-url"
```

### Too Many Notifications

**Solution**:
```
# Add filters
/github subscribe jgtolentino/insightpulse-odoo pulls +label:"urgent"

# Exclude bots
/github subscribe jgtolentino/insightpulse-odoo -author:"dependabot"

# Specific branches only
/github subscribe jgtolentino/insightpulse-odoo commits:main
```

---

## 📈 Metrics & Insights

### Track These Metrics

With Slack integration, you can track:

- **Deployment frequency** (notifications per day)
- **Time to deployment** (commit → deployed)
- **PR review time** (opened → merged)
- **Issue response time** (opened → first response)

### Example: Weekly Summary

Create a scheduled workflow for weekly summaries:

```yaml
name: Weekly Slack Summary
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9 AM

jobs:
  summary:
    runs-on: ubuntu-latest
    steps:
      - name: Send Summary
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload: |
            {
              "text": "📊 Weekly Summary",
              "blocks": [
                {
                  "type": "header",
                  "text": {
                    "type": "plain_text",
                    "text": "📊 InsightPulse Weekly Summary"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {
                      "type": "mrkdwn",
                      "text": "*Deployments*\n7 successful"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*PRs Merged*\n12 PRs"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*Issues Closed*\n8 issues"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*New Features*\n3 features"
                    }
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## ✅ Quick Start Checklist

- [ ] Install GitHub app in Slack workspace
- [ ] Authenticate GitHub account
- [ ] Create #deployment-alerts channel
- [ ] Subscribe to deployments: `/github subscribe jgtolentino/insightpulse-odoo deployments workflows`
- [ ] Create Slack webhook for custom notifications
- [ ] Add SLACK_WEBHOOK_URL to GitHub secrets
- [ ] Update ai-auto-commit.yml with Slack notifications
- [ ] Test deployment with notification
- [ ] Configure additional channels as needed

---

## 📞 Support

**Slack Integration Issues**:
- GitHub Slack Integration: https://slack.github.com/
- Slack API Documentation: https://api.slack.com/

**Internal Support**:
- DevOps Team: devops@insightpulseai.net
- Slack Workspace Admin: admin@insightpulseai.net

---

## 🎉 Conclusion

With GitHub Slack integration, your team gets:

✅ **Real-time notifications** for all important events
✅ **Interactive commands** without leaving Slack
✅ **Rich formatting** with buttons and actions
✅ **Team-wide visibility** on deployments and PRs
✅ **Faster response times** to issues and reviews

**Next**: Update your workflows to include custom Slack notifications!

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
**Maintained By**: InsightPulse DevOps Team
