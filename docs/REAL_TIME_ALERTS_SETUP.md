# Real-Time Health Monitoring Alerts Setup

The health monitor now supports real-time notifications via Slack, Discord, and PagerDuty.

## Overview

- **Alert on Failure**: Immediate notifications when health checks fail
- **Alert on Recovery**: Notifications when health is restored
- **PagerDuty Integration**: Auto-resolve incidents when systems recover
- **Optional**: All webhook configurations are optional - configure only what you need

## Setup Instructions

### Slack Notifications

1. Create a Slack Incoming Webhook:
   - Go to https://api.slack.com/apps
   - Create a new app or select an existing one
   - Enable "Incoming Webhooks"
   - Create a new webhook for your desired channel
   - Copy the webhook URL

2. Add to GitHub Secrets:
   ```bash
   gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```

### Discord Notifications

1. Create a Discord Webhook:
   - Open your Discord server settings
   - Go to Integrations > Webhooks
   - Click "New Webhook"
   - Select the channel for notifications
   - Copy the webhook URL

2. Add to GitHub Secrets:
   ```bash
   gh secret set DISCORD_WEBHOOK_URL --body "https://discord.com/api/webhooks/YOUR/WEBHOOK"
   ```

### PagerDuty Integration

1. Get your PagerDuty Integration Key:
   - Log in to PagerDuty
   - Go to Configuration > Services
   - Select or create a service for health monitoring
   - Go to Integrations > Add Integration
   - Select "Events API V2"
   - Copy the Integration Key

2. Add to GitHub Secrets:
   ```bash
   gh secret set PAGERDUTY_INTEGRATION_KEY --body "your-integration-key-here"
   ```

## Notification Behavior

### Failure Notifications
When health checks fail, you'll receive:
- **Slack**: Formatted card with health status and workflow link
- **Discord**: Embedded message with health status
- **PagerDuty**: Triggered incident with custom details
- **GitHub**: Issue created (or updated if one already exists)

### Recovery Notifications
When health is restored, you'll receive:
- **Slack**: Success message
- **Discord**: Success embedded message
- **PagerDuty**: Incident auto-resolved
- **GitHub**: All open health check issues closed

## Testing

Test your webhook configuration:

```bash
# Trigger a manual health check
gh workflow run health-monitor.yml
```

## Troubleshooting

### Webhook not working?
- Verify the secret is set: `gh secret list`
- Check workflow logs for curl errors
- Verify the webhook URL is correct
- Test the webhook manually with curl

### Too many notifications?
The health monitor is designed to:
- Only create ONE GitHub issue per incident (not spam)
- Use PagerDuty dedup_key to prevent duplicate pages
- Auto-close issues when health restores

### Want to disable notifications temporarily?
Remove the GitHub secret:
```bash
gh secret delete SLACK_WEBHOOK_URL
```

## Related Issues
- Issue #307: Implement Real-Time Alerts in Health Monitor ✅ Completed
- Issue #313-284: Health check failures (fixed with smart issue management)
