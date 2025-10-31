# GitHub Integration Module (pulser-hub)

Integrates GitHub with Odoo via the **pulser-hub** GitHub App.

## Features

- ✅ **Webhook endpoint** - `/odoo/github/webhook` for receiving GitHub events
- ✅ **OAuth callback** - `/odoo/github/auth/callback` for app installation
- ✅ **Track PRs** - Monitor pull requests in Odoo
- ✅ **Track Issues** - Sync GitHub issues with Odoo tasks
- ✅ **Track Webhooks** - Log all webhook events for debugging
- ✅ **GitHub API client** - Call GitHub API from Odoo
- ✅ **Bidirectional sync** - Create GitHub issues from Odoo tasks

## Installation

1. Install module dependencies:
```bash
pip install PyJWT requests
```

2. Install module in Odoo:
```
Apps → Search "GitHub Integration" → Install
```

3. Configure system parameters:
```
Settings → Technical → Parameters → System Parameters
```

Add these parameters:
- `github.app_id` = `2191216` (pre-configured)
- `github.client_id` = `Iv23liwGL7fnYySPPAjS` (pre-configured)
- `github.client_secret` = `[YOUR_CLIENT_SECRET]` ⚠️ **Required**
- `github.webhook_secret` = `[YOUR_WEBHOOK_SECRET]` ⚠️ **Required**
- `github.private_key` = `[YOUR_PRIVATE_KEY_PEM]` ⚠️ **Required**
- `github.installation_id` = `[YOUR_INSTALLATION_ID]` ⚠️ **Required**

## Configuration

### GitHub App Settings

Ensure pulser-hub app has these webhook subscriptions:
- `pull_request`
- `pull_request_review`
- `issues`
- `push`
- `issue_comment`

### Webhook URL
```
https://insightpulseai.net/github/webhook
```

### OAuth Callback URL
```
https://insightpulseai.net/github/auth/callback
```

## Usage

### View GitHub Data

Navigate to: **GitHub** menu

- **Repositories** - View tracked repositories
- **Pull Requests** - Monitor PRs
- **Issues** - Track issues
- **Webhook Events** - Debug webhook deliveries

### Sync Issue to Odoo Task

When GitHub issue is received:
1. Webhook creates `github.issue` record
2. Controller automatically creates `project.task`
3. Task is linked to GitHub issue

### Sync Odoo Task to GitHub

From Odoo task form:
```
Action → Sync to GitHub
```

Requirements:
- Set `GitHub Repository` field (e.g., `jgtolentino/insightpulse-odoo`)
- Task will be created as GitHub issue

### Bot Commands

Comment on GitHub issues/PRs:

- `/odoo-sync` - Create Odoo task from issue
- `/odoo-link` - Link existing task
- `/odoo-status` - Get sync status

## API Usage

### Create GitHub Issue from Python

```python
github_api = env['github.api']

issue = github_api.create_issue(
    repo='jgtolentino/insightpulse-odoo',
    title='Bug in rate policy',
    body='Description of the bug',
    labels=['bug', 'high-priority']
)

print(f"Created issue #{issue['number']}")
```

### Trigger GitHub Workflow

```python
github_api = env['github.api']

success = github_api.trigger_workflow(
    repo='jgtolentino/insightpulse-odoo',
    workflow_id='odoo-module-tools.yml',
    ref='main',
    inputs={
        'action': 'bump-version',
        'version_bump': 'patch'
    }
)
```

## Troubleshooting

### Webhook Not Received

1. Check GitHub App webhook deliveries:
   ```
   GitHub App → Advanced → Recent Deliveries
   ```

2. Check Odoo logs:
   ```
   GitHub → Webhook Events → Find delivery_id
   ```

3. Verify webhook secret matches

### OAuth Failed

1. Check client credentials:
   ```
   Settings → Technical → Parameters → System Parameters
   github.client_id
   github.client_secret
   ```

2. Check OAuth callback URL matches GitHub App settings

### API Calls Failing

1. Check private key is configured:
   ```python
   env['ir.config_parameter'].get_param('github.private_key')
   ```

2. Check installation ID:
   ```python
   env['ir.config_parameter'].get_param('github.installation_id')
   ```

3. Test JWT generation:
   ```python
   jwt = env['github.api']._generate_jwt()
   print(jwt)
   ```

## Security

- ✅ Webhook signatures verified with HMAC SHA-256
- ✅ OAuth credentials stored securely in database
- ✅ Private key never exposed to frontend
- ✅ API tokens short-lived (JWT expires in 10 minutes)

## Dependencies

- `base` - Odoo core
- `project` - For task integration
- `web` - For controllers

External:
- `PyJWT` - JWT encoding for GitHub App auth
- `requests` - HTTP client for GitHub API

## License

LGPL-3.0

## Author

InsightPulse (@jgtolentino)

## Support

- **Documentation**: [docs/PULSER_HUB_INTEGRATION.md](../../../../docs/PULSER_HUB_INTEGRATION.md)
- **Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Email**: support@insightpulse.ai
