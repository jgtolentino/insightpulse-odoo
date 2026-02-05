# GitHub Apps Development

**Skill ID:** `github-apps-development`
**Version:** 1.0.0
**Category:** GitHub Developer Program, Application Development
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables AI agents to design, build, and deploy production-grade GitHub Apps that integrate seamlessly with GitHub's ecosystem, following best practices for authentication, permissions, and user experience.

### Key Capabilities
- GitHub App creation and configuration
- Installation and authorization flows
- Fine-grained permissions management
- Probot framework for Node.js apps
- FastAPI-based GitHub Apps in Python
- Webhook event handling
- GitHub Marketplace distribution

---

## 🧠 Core Competencies

### 1. GitHub App Architecture

#### App Manifest Configuration
```yaml
# github-app-manifest.yml
# Use this to create a GitHub App via https://github.com/settings/apps/new

name: InsightPulse Bot
url: https://insightpulseai.net
hook_attributes:
  url: https://api.insightpulseai.net/webhooks/github
  active: true
redirect_url: https://insightpulseai.net/auth/callback
setup_url: https://insightpulseai.net/setup
public: true
default_events:
  - issues
  - pull_request
  - push
  - release
default_permissions:
  issues: write
  pull_requests: write
  contents: read
  metadata: read
```

#### FastAPI GitHub App Server
```python
# apps/github-bot/app.py
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
import hmac
import hashlib
import os
import jwt
import time
import requests
from typing import Optional

app = FastAPI(title="InsightPulse GitHub Bot")

# Configuration
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = open('github-app-private-key.pem').read()
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

class GitHubAppAuth:
    """Handle GitHub App authentication"""

    def __init__(self, app_id: str, private_key: str):
        self.app_id = app_id
        self.private_key = private_key
        self._installation_tokens = {}

    def generate_jwt(self) -> str:
        """Generate JWT for GitHub App"""
        now = int(time.time())
        payload = {
            'iat': now - 60,
            'exp': now + 600,
            'iss': self.app_id
        }
        return jwt.encode(payload, self.private_key, algorithm='RS256')

    def get_installation_token(self, installation_id: str) -> str:
        """Get or refresh installation token"""
        # Check cache
        if installation_id in self._installation_tokens:
            token_data = self._installation_tokens[installation_id]
            if time.time() < token_data['expires_at'] - 60:
                return token_data['token']

        # Generate new token
        jwt_token = self.generate_jwt()
        response = requests.post(
            f'https://api.github.com/app/installations/{installation_id}/access_tokens',
            headers={
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {jwt_token}',
                'X-GitHub-Api-Version': '2022-11-28'
            }
        )
        response.raise_for_status()
        data = response.json()

        # Cache token
        self._installation_tokens[installation_id] = {
            'token': data['token'],
            'expires_at': time.time() + 3600
        }

        return data['token']

auth = GitHubAppAuth(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    expected = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.get('/health')
def health_check():
    return {'status': 'healthy', 'app': 'InsightPulse GitHub Bot'}

@app.post('/webhooks/github')
async def webhook_handler(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    x_github_delivery: str = Header(None)
):
    """Handle GitHub webhook events"""
    payload_bytes = await request.body()

    # Verify signature
    if not verify_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail='Invalid signature')

    payload = await request.json()

    # Route to event handler
    handlers = {
        'pull_request': handle_pull_request,
        'issues': handle_issue,
        'push': handle_push,
        'release': handle_release,
        'installation': handle_installation
    }

    handler = handlers.get(x_github_event)
    if handler:
        result = await handler(payload)
        return {'status': 'processed', 'result': result}

    return {'status': 'ignored', 'event': x_github_event}

async def handle_pull_request(payload: dict):
    """Handle pull request events"""
    action = payload['action']
    pr = payload['pull_request']
    installation_id = payload['installation']['id']

    if action == 'opened':
        # Get installation token
        token = auth.get_installation_token(installation_id)

        # Add welcome comment
        comment_url = pr['comments_url']
        requests.post(
            comment_url,
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json'
            },
            json={
                'body': '👋 Thanks for your pull request! Our CI/CD pipeline will validate your changes shortly.'
            }
        )

        return {'action': 'comment_added', 'pr': pr['number']}

    return {'action': action, 'pr': pr['number']}

async def handle_issue(payload: dict):
    """Handle issue events"""
    action = payload['action']
    issue = payload['issue']
    installation_id = payload['installation']['id']

    if action == 'opened':
        # Auto-label based on title/body
        labels = []
        title_lower = issue['title'].lower()
        body_lower = (issue['body'] or '').lower()

        if 'bug' in title_lower or 'error' in title_lower:
            labels.append('bug')
        if 'feature' in title_lower or 'enhancement' in title_lower:
            labels.append('enhancement')
        if 'urgent' in title_lower or 'critical' in body_lower:
            labels.append('priority:high')

        if labels:
            token = auth.get_installation_token(installation_id)
            requests.post(
                issue['url'] + '/labels',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/vnd.github+json'
                },
                json={'labels': labels}
            )

        return {'action': 'labels_added', 'issue': issue['number'], 'labels': labels}

    return {'action': action, 'issue': issue['number']}

async def handle_push(payload: dict):
    """Handle push events"""
    ref = payload['ref']
    commits = payload['commits']

    # Example: Trigger deployment on main branch
    if ref == 'refs/heads/main':
        # Trigger deployment workflow
        return {'action': 'deployment_triggered', 'commits': len(commits)}

    return {'action': 'ignored', 'ref': ref}

async def handle_release(payload: dict):
    """Handle release events"""
    action = payload['action']
    release = payload['release']

    if action == 'published':
        # Example: Post to Slack, update changelog, etc.
        return {'action': 'release_published', 'tag': release['tag_name']}

    return {'action': action}

async def handle_installation(payload: dict):
    """Handle installation events"""
    action = payload['action']
    installation = payload['installation']

    if action == 'created':
        # New installation - setup repositories
        return {'action': 'installation_created', 'id': installation['id']}

    return {'action': action}
```

### 2. Probot Framework (Node.js)

#### Probot App Configuration
```javascript
// apps/github-bot-probot/index.js
module.exports = (app) => {
  app.log.info("InsightPulse Bot is running!");

  // Handle new issues
  app.on('issues.opened', async (context) => {
    const issueComment = context.issue({
      body: '👋 Thanks for opening this issue! We\'ll review it shortly.'
    });
    return context.octokit.issues.createComment(issueComment);
  });

  // Handle new pull requests
  app.on('pull_request.opened', async (context) => {
    const pr = context.payload.pull_request;

    // Auto-assign reviewers based on files changed
    const files = await context.octokit.pulls.listFiles(
      context.repo({ pull_number: pr.number })
    );

    const reviewers = determineReviewers(files.data);

    if (reviewers.length > 0) {
      await context.octokit.pulls.requestReviewers(
        context.repo({
          pull_number: pr.number,
          reviewers: reviewers
        })
      );
    }

    // Add labels based on size
    const additions = pr.additions;
    const deletions = pr.deletions;
    const totalChanges = additions + deletions;

    let sizeLabel = 'size/XS';
    if (totalChanges > 500) sizeLabel = 'size/XL';
    else if (totalChanges > 200) sizeLabel = 'size/L';
    else if (totalChanges > 50) sizeLabel = 'size/M';
    else if (totalChanges > 10) sizeLabel = 'size/S';

    await context.octokit.issues.addLabels(
      context.repo({
        issue_number: pr.number,
        labels: [sizeLabel]
      })
    );
  });

  // Handle push to main branch
  app.on('push', async (context) => {
    const ref = context.payload.ref;

    if (ref === 'refs/heads/main') {
      app.log.info('Push to main branch detected');
      // Trigger deployment, notifications, etc.
    }
  });

  // Handle check run completion
  app.on('check_run.completed', async (context) => {
    const checkRun = context.payload.check_run;

    if (checkRun.conclusion === 'failure') {
      // Notify team of CI failure
      app.log.error(`Check run failed: ${checkRun.name}`);
    }
  });
};

function determineReviewers(files) {
  const reviewers = new Set();

  // CODEOWNERS-like logic
  const rules = [
    { pattern: /^odoo\/modules\//, reviewers: ['odoo-expert'] },
    { pattern: /^warehouse\//, reviewers: ['data-engineer'] },
    { pattern: /\.github\/workflows\//, reviewers: ['devops-lead'] },
    { pattern: /Dockerfile/, reviewers: ['devops-lead'] }
  ];

  files.forEach(file => {
    rules.forEach(rule => {
      if (rule.pattern.test(file.filename)) {
        rule.reviewers.forEach(r => reviewers.add(r));
      }
    });
  });

  return Array.from(reviewers);
}
```

#### Probot Configuration
```yaml
# apps/github-bot-probot/.env.example
APP_ID=123456
PRIVATE_KEY_PATH=github-app-private-key.pem
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_PROXY_URL=https://smee.io/your-channel
```

### 3. Fine-Grained Permissions

#### Permission Scopes Best Practices
```python
# docs/github-app-permissions.md
"""
GitHub App Permissions Strategy

Repository Permissions:
- contents: read     # Read repository files
- issues: write      # Create/update issues
- pull_requests: write  # Create/update PRs
- metadata: read     # Access repo metadata (always granted)
- checks: write      # Create check runs
- actions: read      # View workflow runs

Organization Permissions:
- members: read      # List org members (for auto-assign)

Account Permissions:
- email_addresses: read  # Access user email (requires user consent)

Event Subscriptions:
- issues
- pull_request
- push
- release
- check_run
- workflow_run
"""

def request_minimal_permissions():
    """
    Request only the minimum permissions needed for your app to function.
    Avoid requesting organization or user-level permissions unless absolutely necessary.
    """
    return {
        'repository': {
            'contents': 'read',
            'issues': 'write',
            'pull_requests': 'write',
            'checks': 'write'
        },
        'events': [
            'issues',
            'pull_request',
            'check_run'
        ]
    }
```

### 4. User Authorization Flow

#### OAuth Device Flow for CLI Apps
```python
# scripts/github_app/oauth_device_flow.py
import requests
import time
from typing import Dict

class GitHubDeviceFlow:
    """GitHub Device Flow for CLI and limited-input devices"""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.device_code_url = 'https://github.com/login/device/code'
        self.token_url = 'https://github.com/login/oauth/access_token'

    def start_flow(self) -> Dict[str, str]:
        """Initiate device flow"""
        response = requests.post(
            self.device_code_url,
            headers={'Accept': 'application/json'},
            data={'client_id': self.client_id}
        )
        response.raise_for_status()
        return response.json()

    def poll_for_token(self, device_code: str, interval: int = 5) -> str:
        """Poll for user authorization"""
        while True:
            response = requests.post(
                self.token_url,
                headers={'Accept': 'application/json'},
                data={
                    'client_id': self.client_id,
                    'device_code': device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
                }
            )

            data = response.json()

            if 'access_token' in data:
                return data['access_token']

            if data.get('error') == 'authorization_pending':
                time.sleep(interval)
                continue

            if data.get('error') == 'slow_down':
                interval += 5
                time.sleep(interval)
                continue

            raise Exception(f"Authorization failed: {data.get('error_description')}")

# Usage
flow = GitHubDeviceFlow(client_id='Iv1.1234567890abcdef')
device_data = flow.start_flow()

print(f"Visit: {device_data['verification_uri']}")
print(f"Enter code: {device_data['user_code']}")

token = flow.poll_for_token(device_data['device_code'])
print(f"✅ Authorized! Token: {token[:10]}...")
```

### 5. GitHub Marketplace Distribution

#### Marketplace Listing Configuration
```yaml
# .github/marketplace/listing.yml
# Configuration for GitHub Marketplace listing

name: InsightPulse Bot
tagline: Automated workflow assistant for enterprise teams
description: |
  InsightPulse Bot automates common GitHub workflows:
  - Auto-labels issues and PRs
  - Assigns reviewers based on file changes
  - Triggers deployments on release
  - Monitors CI/CD pipeline health
  - Posts status updates to Slack

categories:
  - Automation
  - CI/CD
  - Project Management

pricing:
  - name: Free
    price: 0
    description: For open source and small teams
    features:
      - Up to 10 repositories
      - Basic automation
      - Community support

  - name: Pro
    price: 9
    unit: monthly
    description: For growing teams
    features:
      - Unlimited repositories
      - Advanced automation
      - Priority support
      - Custom workflows

  - name: Enterprise
    price: 49
    unit: monthly
    description: For large organizations
    features:
      - Everything in Pro
      - Dedicated support
      - SLA guarantees
      - Custom integrations

support_url: https://insightpulseai.net/support
privacy_policy_url: https://insightpulseai.net/privacy
terms_of_service_url: https://insightpulseai.net/terms
```

---

## ✅ Validation Criteria

### App Quality Standards
- ✅ JWT token generation under 100ms
- ✅ Webhook processing under 1s
- ✅ Graceful error handling with retries
- ✅ Proper signature verification
- ✅ Minimum permission scopes requested

### Security Requirements
- ✅ Private key stored securely (not in repo)
- ✅ Webhook secret verification on all requests
- ✅ Installation token caching with expiry
- ✅ HTTPS-only webhook endpoints
- ✅ Rate limit handling

---

## 🎯 Usage Examples

### Example 1: Deploy GitHub App with Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Store private key securely
RUN mkdir -p /secrets
VOLUME /secrets

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  github-bot:
    build: apps/github-bot
    ports:
      - "8080:8080"
    environment:
      GITHUB_APP_ID: ${GITHUB_APP_ID}
      GITHUB_WEBHOOK_SECRET: ${GITHUB_WEBHOOK_SECRET}
    volumes:
      - ./secrets/github-app-private-key.pem:/secrets/github-app-private-key.pem:ro
    restart: unless-stopped
```

### Example 2: Local Development with Smee
```bash
# Install smee-client for local webhook testing
npm install -g smee-client

# Start smee proxy
smee -u https://smee.io/your-channel -t http://localhost:8080/webhooks/github

# In another terminal, start your app
cd apps/github-bot
uvicorn app:app --reload
```

### Example 3: Test Webhook Signature Verification
```python
# tests/test_webhooks.py
import pytest
from app import verify_signature

def test_valid_signature():
    payload = b'{"action": "opened"}'
    secret = 'test-secret'
    signature = 'sha256=' + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    assert verify_signature(payload, signature) == True

def test_invalid_signature():
    payload = b'{"action": "opened"}'
    signature = 'sha256=invalid'

    assert verify_signature(payload, signature) == False
```

---

## 📊 Success Metrics

### App Performance
- **Webhook Processing Time**: <500ms p95
- **Installation Token Cache Hit Rate**: >90%
- **API Error Rate**: <0.5%
- **Uptime**: >99.9%

### User Adoption
- **Active Installations**: 100+
- **Monthly Active Users**: 500+
- **User Satisfaction**: 4.5/5 stars
- **Support Ticket Volume**: <5/week

---

## 🔗 Related Skills
- `github-api-integration` - GitHub API usage
- `github-webhooks-integration` - Webhook handling
- `github-actions-workflows` - CI/CD integration

---

## 📚 References

- [Building GitHub Apps](https://docs.github.com/en/apps/creating-github-apps)
- [GitHub App Authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app)
- [Probot Framework](https://probot.github.io/)
- [GitHub Marketplace](https://docs.github.com/en/apps/publishing-apps-to-github-marketplace)

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
