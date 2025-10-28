# Pulser Hub Sync

GitHub App integration module for Odoo 19, providing webhook listeners and OAuth authentication.

## Features

- **OAuth 2.0 Authentication**: Handle GitHub App installation callbacks
- **Webhook Processing**: Receive and process GitHub events (push, PR, issues, workflows)
- **JWT Authentication**: Secure API access using RSA private keys
- **Event Tracking**: Complete audit trail with payload storage
- **Token Management**: Automatic installation token refresh

## Installation

### Prerequisites

1. GitHub App credentials (already configured):
   - App ID: `2191216`
   - Client ID: `Iv23liwGL7fnYySPPAjS`
   - PEM file: `~/.github/apps/pulser-hub.pem`

2. Environment variables in `~/.zshrc`:
```bash
export GITHUB_APP_ID=2191216
export GITHUB_APP_CLIENT_ID=Iv23liwGL7fnYySPPAjS
export GITHUB_APP_PEM_PATH=~/.github/apps/pulser-hub.pem
export GITHUB_APP_CLIENT_SECRET=your_client_secret_here  # Get from GitHub App settings
```

3. Python dependencies (add to requirements.txt if needed):
```
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0
```

### Module Installation

1. Copy module to Odoo addons directory:
```bash
# Module is already in: addons/custom/pulser_hub_sync/
```

2. Update Odoo module list:
```bash
# Via Odoo shell
odoo shell -d odoo -c /etc/odoo/odoo.conf
```
```python
self.env['ir.module.module'].update_list()
```

3. Install the module:
```python
module = self.env['ir.module.module'].search([('name', '=', 'pulser_hub_sync')], limit=1)
module.button_immediate_install()
```

Or via Apps menu: Search for "Pulser Hub Sync" → Install

## Configuration

### 1. GitHub App Setup

The GitHub App "pulser-hub" is already created with:
- **App URL**: https://github.com/settings/apps/pulser-hub
- **Callback URL**: `https://your-odoo-domain.com/odoo/github/auth/callback`
- **Webhook URL**: `https://your-odoo-domain.com/odoo/github/webhook`

### 2. Odoo Configuration

1. Navigate to: **GitHub → Integrations**
2. After GitHub App installation, integration record auto-created
3. Configure webhook secret for signature verification:
   - Open the integration record
   - Set **Webhook Secret** (same as GitHub App webhook secret)

### 3. GitHub Webhook Configuration

Configure webhook at: https://github.com/settings/apps/pulser-hub

**Webhook URL**: `https://your-odoo-domain.com/odoo/github/webhook`

**Events to subscribe**:
- ✅ Push events
- ✅ Pull requests
- ✅ Issues
- ✅ Workflow runs

**Content type**: `application/json`

**Secret**: Set a strong secret and configure same in Odoo

## Usage

### Install GitHub App

1. Visit: https://github.com/apps/pulser-hub
2. Click "Install" and select repositories
3. Authorize the app → Redirects to `/odoo/github/auth/callback`
4. Success page confirms connection

### Monitor Webhook Events

Navigate to: **GitHub → Webhook Events**

View all received events with:
- Event type (push, pull_request, issues, etc.)
- Repository and sender
- Delivery ID
- Payload (JSON)
- Processing status

### Reprocess Failed Events

1. Open failed webhook event (red highlight in list)
2. Click "Reprocess" button
3. Event marked as unprocessed and re-queued

## API Routes

### OAuth Callback
```
GET /odoo/github/auth/callback
```

**Query Parameters**:
- `code`: Authorization code from GitHub
- `installation_id`: GitHub App installation ID
- `setup_action`: install/update

**Response**: HTML success/error page

### Webhook Listener
```
POST /odoo/github/webhook
```

**Headers**:
- `X-GitHub-Event`: Event type (push, pull_request, etc.)
- `X-Hub-Signature-256`: HMAC signature for verification
- `X-GitHub-Delivery`: Unique delivery ID

**Body**: JSON payload from GitHub

**Response**: `{"status": "success", "message": "Webhook processed"}`

## Event Handlers

Currently implemented handlers:

### Push Events
- Triggered on git push
- Logs commits and branch information
- Custom logic: Add deployment triggers, documentation updates

### Pull Request Events
- Triggered on PR open/close/update
- Logs PR number and action
- Custom logic: CI checks, automated labeling, comment posting

### Issue Events
- Triggered on issue create/update/close
- Logs issue number and action
- Custom logic: Create Odoo tasks, update status

### Workflow Run Events
- Triggered on GitHub Actions completion
- Logs workflow name and conclusion
- Custom logic: Team notifications, downstream task triggers

## Security

### JWT Authentication
- RS256 signing algorithm
- 10-minute token expiry
- Private key stored securely at `~/.github/apps/pulser-hub.pem`

### Webhook Signature Verification
- HMAC-SHA256 signature verification
- Webhook secret stored in Odoo (encrypted)
- Prevents unauthorized webhook submissions

### Token Management
- Installation tokens expire after 1 hour
- Automatic refresh on expiry
- Tokens stored encrypted in database

## Troubleshooting

### OAuth Callback Errors

**Symptom**: "Missing authorization code or installation ID"

**Fix**: Ensure GitHub App redirect URL is correctly configured:
```
https://your-odoo-domain.com/odoo/github/auth/callback
```

### Webhook Signature Verification Failed

**Symptom**: "Invalid webhook signature"

**Fix**:
1. Verify webhook secret matches GitHub App settings
2. Check Odoo integration record has webhook_secret configured
3. Ensure payload body is not modified before verification

### JWT Generation Failed

**Symptom**: "Failed to generate JWT"

**Fix**:
1. Check PEM file exists: `ls -la ~/.github/apps/pulser-hub.pem`
2. Verify permissions: `chmod 600 ~/.github/apps/pulser-hub.pem`
3. Test PEM validity: `openssl rsa -in ~/.github/apps/pulser-hub.pem -check -noout`

### Installation Token Refresh Failed

**Symptom**: Token expired, API calls fail

**Fix**:
1. Check JWT generation is working
2. Verify App ID and installation ID are correct
3. Manually refresh: GitHub → Integrations → Open record → Token should auto-refresh

## Development

### Adding Custom Event Handlers

Edit `controllers/github_webhook.py`:

```python
def _process_webhook_event(self, event_type, payload):
    """Add your custom event type"""
    handlers = {
        'push': self._handle_push_event,
        'custom_event': self._handle_custom_event,  # Add your handler
    }

    handler = handlers.get(event_type)
    if handler:
        handler(payload)

def _handle_custom_event(self, payload):
    """Your custom logic here"""
    _logger.info(f"Custom event: {payload}")
```

### Extending Models

Create additional models in `models/` directory:
```python
# models/github_repository.py
class GitHubRepository(models.Model):
    _name = 'github.repository'
    _description = 'GitHub Repository'

    name = fields.Char(required=True)
    full_name = fields.Char(required=True)
    integration_id = fields.Many2one('github.integration', required=True)
```

## Support

- **GitHub App**: https://github.com/settings/apps/pulser-hub
- **Documentation**: `docs/GITHUB_APP_SETUP.md`
- **Helper Scripts**: `scripts/gh-app-*.sh`

## License

LGPL-3

## Author

InsightPulse AI (https://insightpulseai.net)
