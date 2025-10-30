# Pulser-Hub GitHub App Integration

Complete guide for the **pulser-hub** GitHub App - a custom integration connecting GitHub with your Odoo instance.

---

## 🤖 Overview

**pulser-hub** is a custom GitHub App that enables bidirectional integration between GitHub and your InsightPulse Odoo instance.

### App Details

| Property | Value |
|----------|-------|
| **App ID** | 2191216 |
| **Client ID** | Iv23liwGL7fnYySPPAjS |
| **Owner** | @jgtolentino |
| **Homepage** | https://insightpulseai.net/pulser-hub |
| **Status** | Active |

---

## 🔗 Integration Endpoints

### OAuth Callback
**URL**: `https://insightpulseai.net/odoo/github/auth/callback`

**Purpose**: Handle user authorization after GitHub App installation

**Flow**:
1. User installs pulser-hub on repository
2. GitHub redirects to this URL with auth code
3. Odoo exchanges code for access token
4. Token stored in Odoo for API operations

### Webhook Endpoint
**URL**: `https://insightpulseai.net/odoo/github/webhook`

**Purpose**: Receive GitHub events in real-time

**Security**:
- ✅ SSL verification enabled
- ✅ Webhook secret configured
- ✅ Private key authentication

---

## 📡 Architecture

```
┌─────────────────────────────────────────────────────────┐
│ GitHub Repository (jgtolentino/insightpulse-odoo)       │
│  ├─ GitHub Actions (automation workflows)               │
│  ├─ Pull Requests (code reviews)                        │
│  ├─ Issues (bug tracking)                               │
│  └─ Webhooks (event notifications)                      │
└────────────────────────┬────────────────────────────────┘
                         │ Webhook Events
                         ↓
┌─────────────────────────────────────────────────────────┐
│ pulser-hub GitHub App                                   │
│  ├─ App ID: 2191216                                     │
│  ├─ OAuth: User authorization                           │
│  ├─ Webhooks: Event delivery                            │
│  └─ Private Key: API authentication                     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS POST
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Odoo Instance (insightpulseai.net)                      │
│  ├─ Webhook Handler: /odoo/github/webhook              │
│  ├─ OAuth Handler: /odoo/github/auth/callback          │
│  ├─ GitHub API Client: Make API calls                  │
│  └─ Custom Modules: Process GitHub data                │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Authentication & Security

### OAuth Flow

**Installation Authorization**:
```
1. User clicks "Install" on pulser-hub
   ↓
2. GitHub shows permission screen
   ↓
3. User approves
   ↓
4. GitHub redirects to:
   https://insightpulseai.net/odoo/github/auth/callback?code=ABC123
   ↓
5. Odoo exchanges code for access token
   ↓
6. Token stored securely in Odoo database
```

### API Authentication

**Using Private Key**:
```python
import jwt
import time

# Generate JWT for GitHub App authentication
payload = {
    'iat': int(time.time()),
    'exp': int(time.time()) + (10 * 60),  # 10 minutes
    'iss': 2191216  # App ID
}

# Sign with private key
token = jwt.encode(payload, private_key, algorithm='RS256')

# Use token to get installation access token
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json'
}
```

### Webhook Security

**Verify webhook signatures**:
```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify GitHub webhook signature."""
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

---

## 📨 Webhook Events

### Subscribed Events

The pulser-hub app should subscribe to these events:

#### Pull Request Events
- `pull_request.opened`
- `pull_request.closed`
- `pull_request.synchronize`
- `pull_request.reopened`
- `pull_request.labeled`
- `pull_request.unlabeled`

#### Pull Request Review Events
- `pull_request_review.submitted`
- `pull_request_review.dismissed`

#### Issue Events
- `issues.opened`
- `issues.closed`
- `issues.reopened`
- `issues.labeled`

#### Push Events
- `push` (to main, develop branches)

#### Issue Comment Events
- `issue_comment.created` (for bot commands)

---

## 🔧 Odoo Module Implementation

### Required Odoo Module: `github_integration`

**Location**: `addons/insightpulse/ops/github_integration/`

### Module Structure

```
addons/insightpulse/ops/github_integration/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── github_webhook.py        # Webhook event processing
│   ├── github_repository.py     # Repository metadata
│   ├── github_pull_request.py   # PR tracking
│   └── github_issue.py          # Issue tracking
├── controllers/
│   ├── __init__.py
│   ├── webhook.py               # /odoo/github/webhook handler
│   └── oauth.py                 # /odoo/github/auth/callback handler
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── github_repository_views.xml
│   ├── github_pull_request_views.xml
│   └── github_issue_views.xml
└── data/
    └── github_config.xml
```

### Example: Webhook Controller

```python
# controllers/webhook.py
from odoo import http
from odoo.http import request
import json
import hmac
import hashlib

class GitHubWebhookController(http.Controller):

    @http.route('/odoo/github/webhook', type='json', auth='public', csrf=False, methods=['POST'])
    def github_webhook(self, **kwargs):
        """Handle GitHub webhook events."""

        # Get request data
        payload = request.httprequest.data
        signature = request.httprequest.headers.get('X-Hub-Signature-256')
        event_type = request.httprequest.headers.get('X-GitHub-Event')

        # Verify signature
        webhook_secret = request.env['ir.config_parameter'].sudo().get_param('github.webhook_secret')
        if not self._verify_signature(payload, signature, webhook_secret):
            return {'error': 'Invalid signature'}, 401

        # Parse payload
        data = json.loads(payload)

        # Route to appropriate handler
        handlers = {
            'pull_request': self._handle_pull_request,
            'pull_request_review': self._handle_pr_review,
            'issues': self._handle_issue,
            'push': self._handle_push,
            'issue_comment': self._handle_comment,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(data)
            return {'status': 'ok'}

        return {'status': 'ignored'}

    def _verify_signature(self, payload, signature, secret):
        """Verify webhook signature."""
        if not signature or not secret:
            return False

        expected = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def _handle_pull_request(self, data):
        """Handle pull_request events."""
        action = data['action']
        pr = data['pull_request']

        # Create or update PR record in Odoo
        PullRequest = request.env['github.pull.request'].sudo()

        pr_record = PullRequest.search([
            ('number', '=', pr['number']),
            ('repository', '=', data['repository']['full_name'])
        ], limit=1)

        if action == 'opened':
            if not pr_record:
                pr_record = PullRequest.create({
                    'number': pr['number'],
                    'title': pr['title'],
                    'body': pr['body'],
                    'repository': data['repository']['full_name'],
                    'state': pr['state'],
                    'author': pr['user']['login'],
                    'url': pr['html_url'],
                    'created_at': pr['created_at'],
                })

            # Trigger automation
            self._trigger_odoo_actions(pr_record, 'pr_opened')

        elif action == 'closed':
            if pr_record:
                pr_record.write({
                    'state': 'closed',
                    'merged': pr.get('merged', False),
                    'closed_at': pr.get('closed_at'),
                })

            # Trigger automation
            if pr.get('merged'):
                self._trigger_odoo_actions(pr_record, 'pr_merged')

    def _handle_pr_review(self, data):
        """Handle pull_request_review events."""
        review = data['review']
        pr = data['pull_request']

        # Update PR record with review
        PullRequest = request.env['github.pull.request'].sudo()
        pr_record = PullRequest.search([
            ('number', '=', pr['number']),
            ('repository', '=', data['repository']['full_name'])
        ], limit=1)

        if pr_record and review['state'] == 'approved':
            # Increment approval count
            pr_record.write({
                'approvals': pr_record.approvals + 1
            })

    def _handle_issue(self, data):
        """Handle issues events."""
        action = data['action']
        issue = data['issue']

        # Create or update issue record
        Issue = request.env['github.issue'].sudo()

        issue_record = Issue.search([
            ('number', '=', issue['number']),
            ('repository', '=', data['repository']['full_name'])
        ], limit=1)

        if action == 'opened' and not issue_record:
            issue_record = Issue.create({
                'number': issue['number'],
                'title': issue['title'],
                'body': issue['body'],
                'repository': data['repository']['full_name'],
                'state': issue['state'],
                'author': issue['user']['login'],
                'url': issue['html_url'],
                'created_at': issue['created_at'],
            })

    def _handle_push(self, data):
        """Handle push events."""
        ref = data['ref']
        commits = data['commits']

        # Log push event
        request.env['github.push.event'].sudo().create({
            'repository': data['repository']['full_name'],
            'ref': ref,
            'commits_count': len(commits),
            'pusher': data['pusher']['name'],
            'pushed_at': data['head_commit']['timestamp'],
        })

    def _handle_comment(self, data):
        """Handle issue_comment events."""
        comment = data['comment']
        issue = data['issue']

        # Check if comment contains bot command
        body = comment['body'].strip()

        if body.startswith('/'):
            # Parse command
            parts = body.split()
            command = parts[0][1:]  # Remove leading /
            args = parts[1:]

            # Execute bot command
            self._execute_bot_command(issue, comment, command, args)

    def _execute_bot_command(self, issue, comment, command, args):
        """Execute bot command from comment."""
        # Implement bot command logic
        # This can trigger GitHub Actions workflows
        # or perform Odoo-specific actions
        pass

    def _trigger_odoo_actions(self, record, trigger_type):
        """Trigger Odoo automated actions based on GitHub events."""
        # Find and execute relevant automated actions
        # This integrates with Odoo Studio automated actions
        pass
```

### Example: OAuth Controller

```python
# controllers/oauth.py
from odoo import http
from odoo.http import request
import requests

class GitHubOAuthController(http.Controller):

    @http.route('/odoo/github/auth/callback', type='http', auth='public', methods=['GET'])
    def github_oauth_callback(self, code=None, state=None, **kwargs):
        """Handle GitHub OAuth callback."""

        if not code:
            return request.render('github_integration.oauth_error', {
                'error': 'No authorization code received'
            })

        # Exchange code for access token
        client_id = request.env['ir.config_parameter'].sudo().get_param('github.client_id')
        client_secret = request.env['ir.config_parameter'].sudo().get_param('github.client_secret')

        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            headers={'Accept': 'application/json'},
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
            }
        )

        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')

            # Store token
            request.env['github.oauth.token'].sudo().create({
                'access_token': access_token,
                'token_type': token_data.get('token_type'),
                'scope': token_data.get('scope'),
            })

            return request.render('github_integration.oauth_success', {
                'message': 'GitHub App successfully connected!'
            })

        return request.render('github_integration.oauth_error', {
            'error': 'Failed to exchange authorization code'
        })
```

---

## 🎯 Integration with GitHub Actions

The pulser-hub app complements the GitHub Actions workflows I created:

### Workflow Architecture

```
┌────────────────────────────────────────────────────┐
│ GitHub Actions Workflows                          │
│  ├─ oca-bot-automation.yml                        │
│  │   ├─ Auto-label PRs                            │
│  │   ├─ Delete branches                           │
│  │   ├─ Mention maintainers                       │
│  │   └─ Bot commands (/merge, /rebase)           │
│  └─ odoo-module-tools.yml                         │
│      ├─ Generate README                           │
│      ├─ Bump versions                             │
│      └─ Validate manifests                        │
└────────────────────────────────────────────────────┘
                         │
                         │ Trigger via API
                         ↓
┌────────────────────────────────────────────────────┐
│ pulser-hub GitHub App                             │
│  ├─ Receive webhook events                        │
│  ├─ Process in Odoo                               │
│  ├─ Trigger Odoo automated actions                │
│  └─ Call GitHub API (create issues, PRs, etc.)   │
└────────────────────────────────────────────────────┘
```

### Use Cases

#### 1. PR Merged → Update Odoo Records
```
GitHub: PR merged
  ↓ Webhook
Odoo: Update project task status
Odoo: Create deployment record
Odoo: Trigger automated action
```

#### 2. Issue Created → Create Odoo Task
```
GitHub: Issue opened
  ↓ Webhook
Odoo: Create project.task record
Odoo: Assign to maintainer
Odoo: Link to GitHub issue
```

#### 3. Odoo Action → Trigger GitHub Workflow
```
Odoo: Release approved
  ↓ GitHub API
GitHub: Trigger workflow_dispatch
GitHub: Run odoo-module-tools (bump-version)
  ↓ Webhook
Odoo: Log version bump
```

---

## 🛠️ Configuration

### Required System Parameters (Odoo)

Set these in **Settings → Technical → Parameters → System Parameters**:

```
github.app_id = 2191216
github.client_id = Iv23liwGL7fnYySPPAjS
github.client_secret = [YOUR_CLIENT_SECRET]
github.webhook_secret = [YOUR_WEBHOOK_SECRET]
github.private_key = [YOUR_PRIVATE_KEY_PEM]
```

### GitHub App Permissions

Ensure pulser-hub has these permissions:

**Repository permissions:**
- ✅ Contents: Read & write
- ✅ Issues: Read & write
- ✅ Pull requests: Read & write
- ✅ Metadata: Read-only
- ✅ Webhooks: Read & write

**Organization permissions:**
- ✅ Members: Read-only

**User permissions:**
- ✅ Email addresses: Read-only

---

## 📊 Monitoring & Logs

### View Webhook Deliveries

1. Go to GitHub App settings
2. Navigate to **Advanced → Recent Deliveries**
3. View request/response for each webhook

### Odoo Logs

Check webhook processing logs:
```python
# In Odoo shell
webhooks = env['github.webhook.event'].search([], order='create_date desc', limit=10)
for wh in webhooks:
    print(f"{wh.event_type} - {wh.status} - {wh.create_date}")
```

---

## 🚀 Advanced Features

### Trigger GitHub Workflows from Odoo

```python
import requests
import jwt
import time

class GitHubAPI:
    def trigger_workflow(self, repo, workflow_id, inputs=None):
        """Trigger GitHub Actions workflow from Odoo."""

        # Generate JWT
        token = self._get_installation_token()

        # Trigger workflow
        response = requests.post(
            f'https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches',
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github.v3+json'
            },
            json={
                'ref': 'main',
                'inputs': inputs or {}
            }
        )

        return response.status_code == 204
```

### Sync GitHub Issues with Odoo Tasks

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    github_issue_number = fields.Integer('GitHub Issue #')
    github_issue_url = fields.Char('GitHub Issue URL')
    github_repository = fields.Char('GitHub Repository')

    def sync_to_github(self):
        """Create GitHub issue from Odoo task."""
        github_api = self.env['github.api']

        issue = github_api.create_issue(
            repo=self.github_repository,
            title=self.name,
            body=self.description,
            labels=['odoo-sync']
        )

        self.write({
            'github_issue_number': issue['number'],
            'github_issue_url': issue['html_url']
        })
```

---

## 📚 References

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Odoo Controllers](https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html)
- [Odoo Automated Actions](https://www.odoo.com/documentation/19.0/applications/studio/automated_actions.html)

---

## 🤝 Support

Questions about pulser-hub integration?

- **GitHub Issues**: [Create issue](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Email**: support@insightpulse.ai
- **App Owner**: @jgtolentino

---

**Last Updated**: 2025-10-30
**App Version**: 1.0.0
**App ID**: 2191216
**Status**: Active
