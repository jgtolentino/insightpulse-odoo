# Pulser Hub Sync - Installation Guide

## Prerequisites Checklist

### ✅ GitHub App Configuration (Already Completed)
- [x] GitHub App "pulser-hub" created
- [x] App ID: 2191216
- [x] Client ID: Iv23liwGL7fnYySPPAjS
- [x] PEM file downloaded and secured: `~/.github/apps/pulser-hub.pem`
- [x] Environment variables added to `~/.zshrc`
- [x] Helper scripts created in `scripts/`

### ⏳ Python Dependencies (To Be Installed)
- [ ] PyJWT >= 2.8.0
- [ ] cryptography >= 41.0.0
- [ ] requests >= 2.31.0

### ⏳ Odoo Configuration (To Be Completed)
- [ ] Module installed in Odoo
- [ ] GitHub App webhook secret configured
- [ ] OAuth callback tested
- [ ] Webhook listener tested

## Installation Steps

### Step 1: Install Python Dependencies

**Option A: System-wide (if using system Python)**
```bash
pip3 install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
```

**Option B: Odoo virtualenv (recommended)**
```bash
# Activate Odoo's virtualenv first
source /path/to/odoo/venv/bin/activate

# Install dependencies
pip install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
```

**Option C: Docker container**
```bash
# If Odoo is running in Docker, install in container
docker exec -it odoo-bundle pip3 install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0

# Or add to Dockerfile:
# RUN pip3 install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
```

### Step 2: Verify Environment Variables

Check that environment variables are loaded:
```bash
echo "GITHUB_APP_ID: $GITHUB_APP_ID"
echo "GITHUB_APP_CLIENT_ID: $GITHUB_APP_CLIENT_ID"
echo "GITHUB_APP_PEM_PATH: $GITHUB_APP_PEM_PATH"

# Verify PEM file exists and has correct permissions
ls -la ~/.github/apps/pulser-hub.pem
# Should show: -rw------- (600 permissions)
```

**If not loaded**, source your shell config:
```bash
source ~/.zshrc
```

### Step 3: Get GitHub App Client Secret

1. Visit: https://github.com/settings/apps/pulser-hub
2. Scroll to "Client secrets"
3. Click "Generate a new client secret"
4. Copy the secret (only shown once!)
5. Add to `~/.zshrc`:
```bash
export GITHUB_APP_CLIENT_SECRET=your_secret_here
```
6. Reload: `source ~/.zshrc`

### Step 4: Install Odoo Module

**Option A: Via Odoo Shell (recommended for production)**
```bash
# Start Odoo shell
odoo shell -d odoo -c /etc/odoo/odoo.conf

# Or via Docker:
docker exec -it odoo-bundle odoo shell -d odoo -c /etc/odoo/odoo.conf
```

In the Odoo shell:
```python
# Update module list
self.env['ir.module.module'].update_list()
self.env.cr.commit()

# Find and install the module
module = self.env['ir.module.module'].search([('name', '=', 'pulser_hub_sync')], limit=1)
if module:
    print(f"Found module: {module.name} (state: {module.state})")
    if module.state != 'installed':
        module.button_immediate_install()
        print("Module installed successfully!")
    else:
        print("Module already installed")
else:
    print("ERROR: Module not found. Check addon path configuration.")
```

**Option B: Via Web UI (for testing)**
1. Login to Odoo as admin
2. Navigate to: Apps (activate Developer Mode if needed)
3. Click "Update Apps List"
4. Search for "Pulser Hub Sync"
5. Click "Install"

### Step 5: Configure Webhook Secret

1. Navigate to: **GitHub → Integrations** (create a test record if none exist)
2. Set **Webhook Secret**: Use a strong random string
```bash
# Generate a secure webhook secret:
openssl rand -hex 32
```
3. Save the record

### Step 6: Configure GitHub App Webhook

1. Visit: https://github.com/settings/apps/pulser-hub
2. Scroll to "Webhook"
3. Set **Webhook URL**: `https://your-odoo-domain.com/odoo/github/webhook`
4. Set **Webhook secret**: Same value as configured in Odoo (Step 5)
5. Set **Permissions** (if not already set):
   - Repository contents: Read-only
   - Pull requests: Read & write
   - Issues: Read & write
   - Workflows: Read-only
6. Subscribe to events:
   - [x] Push
   - [x] Pull request
   - [x] Issues
   - [x] Workflow run
7. Set **Active**: ✅ Enabled
8. Click "Save changes"

### Step 7: Install GitHub App on Repository

1. Visit: https://github.com/apps/pulser-hub
2. Click "Install" or "Configure"
3. Select repositories to grant access (or "All repositories")
4. Click "Install"
5. **Important**: You will be redirected to `/odoo/github/auth/callback`
6. Verify success page appears

If successful, you should see:
```
✅ GitHub App Connected!
Successfully connected to your-github-account
Installation ID: 12345678
```

### Step 8: Verify Installation

**Check Odoo Integration Record**:
1. Navigate to: **GitHub → Integrations**
2. Verify record exists with:
   - Account Login: your-github-account
   - Installation ID: (auto-populated)
   - Repository Selection: all or selected
   - Last Sync: recent timestamp

**Test Webhook Delivery**:
1. Navigate to: **GitHub → Webhook Events**
2. Trigger a test event:
   - Push a commit to a repository
   - Create an issue
   - Open a pull request
3. Verify event appears in list
4. Open event record to view payload

**Check GitHub Webhook Deliveries**:
1. Visit: https://github.com/settings/apps/pulser-hub/advanced
2. Scroll to "Recent Deliveries"
3. Verify recent webhook deliveries show "200 OK" response

## Verification Checklist

### ✅ Module Installation
- [ ] Module appears in Apps list
- [ ] Module state is "Installed"
- [ ] No errors in Odoo logs during installation
- [ ] Menu item "GitHub" appears in main menu

### ✅ OAuth Flow
- [ ] GitHub App installation redirects to Odoo
- [ ] Success page displays without errors
- [ ] Integration record auto-created in Odoo
- [ ] Access token and installation token populated

### ✅ Webhook Processing
- [ ] Webhook events appear in "GitHub → Webhook Events"
- [ ] Events marked as "Processed"
- [ ] GitHub webhook deliveries show 200 OK response
- [ ] No signature verification errors in logs

### ✅ Security
- [ ] PEM file has 600 permissions
- [ ] Webhook secret configured and matching
- [ ] Tokens stored encrypted in database
- [ ] Environment variables properly set

## Troubleshooting

### Module Not Found in Apps

**Check addon path**:
```bash
grep addons_path /etc/odoo/odoo.conf
# Verify path includes: /path/to/insightpulse-odoo/addons/custom
```

**Restart Odoo** (if addon path was added):
```bash
# System service
sudo systemctl restart odoo

# Docker
docker restart odoo-bundle
```

### OAuth Callback 404 Error

**Verify Odoo is accessible**:
```bash
curl -I https://your-odoo-domain.com/web/login
# Should return: HTTP/1.1 200 OK
```

**Check route registration**:
```python
# In Odoo shell
routes = self.env['ir.http']._get_routes()
github_routes = [r for r in routes if 'github' in r]
print(github_routes)
# Should show: /odoo/github/auth/callback, /odoo/github/webhook
```

### Webhook Signature Verification Failed

**Verify webhook secret matches**:
1. Check GitHub App webhook secret
2. Check Odoo integration record webhook_secret field
3. Ensure they are identical (no extra spaces)

**Test HMAC signature** (debug):
```python
import hmac
import hashlib

webhook_secret = b'your_secret_here'
payload = b'{"test": "payload"}'
signature = "sha256=" + hmac.new(webhook_secret, payload, hashlib.sha256).hexdigest()
print(f"Expected signature: {signature}")
```

### PyJWT Import Error

**Symptom**: `ImportError: No module named 'jwt'`

**Fix**: Install PyJWT in correct environment
```bash
# Find which Python Odoo is using
ps aux | grep odoo

# Install in that environment
/path/to/python -m pip install PyJWT cryptography requests
```

## Production Deployment

### Recommended: Add to requirements.txt

Create or update `requirements.txt`:
```
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0
```

### Recommended: Add to Dockerfile

If using Docker:
```dockerfile
# Add after Odoo installation
RUN pip3 install --no-cache-dir PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
```

### Environment Variables in Production

**Option A: Systemd service** (add to `/etc/systemd/system/odoo.service`):
```ini
[Service]
Environment="GITHUB_APP_ID=2191216"
Environment="GITHUB_APP_CLIENT_ID=Iv23liwGL7fnYySPPAjS"
Environment="GITHUB_APP_PEM_PATH=/etc/odoo/github/pulser-hub.pem"
Environment="GITHUB_APP_CLIENT_SECRET=your_secret_here"
```

**Option B: Docker Compose** (add to `docker-compose.yml`):
```yaml
services:
  odoo:
    environment:
      - GITHUB_APP_ID=2191216
      - GITHUB_APP_CLIENT_ID=Iv23liwGL7fnYySPPAjS
      - GITHUB_APP_PEM_PATH=/etc/odoo/github/pulser-hub.pem
      - GITHUB_APP_CLIENT_SECRET=${GITHUB_APP_CLIENT_SECRET}
    volumes:
      - ~/.github/apps/pulser-hub.pem:/etc/odoo/github/pulser-hub.pem:ro
```

**Option C: Odoo config file** (NOT RECOMMENDED - secrets in plaintext):
```ini
# /etc/odoo/odoo.conf - Don't store secrets here!
# Use environment variables instead
```

## Support

If issues persist:
1. Check Odoo logs: `tail -f /var/log/odoo/odoo.log`
2. Check GitHub webhook deliveries: https://github.com/settings/apps/pulser-hub/advanced
3. Verify PEM file integrity: `openssl rsa -in ~/.github/apps/pulser-hub.pem -check -noout`
4. Review module README: `addons/custom/pulser_hub_sync/README.md`

## Next Steps

After successful installation:
1. Customize event handlers in `controllers/github_webhook.py`
2. Add additional models for storing repository data
3. Create automated workflows based on GitHub events
4. Integrate with other Odoo modules (projects, tasks, etc.)
