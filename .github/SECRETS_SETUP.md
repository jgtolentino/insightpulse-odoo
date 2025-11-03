# GitHub Secrets Setup - Quick Reference

This file provides a quick checklist for setting up repository secrets.

---

## ✅ Required Secrets Checklist

Copy this checklist and fill in the values as you complete each step.

### GitHub App Secrets

- [ ] **APP_ID**
  - Source: GitHub App settings page
  - Format: Numeric ID (e.g., `123456`)
  - Value: `_________________`

- [ ] **INSTALLATION_ID**
  - Source: GitHub App installation URL
  - Format: Numeric ID (e.g., `12345678`)
  - Value: `_________________`

- [ ] **PRIVATE_KEY**
  - Source: GitHub App private key (.pem file)
  - Format: PEM-encoded RSA private key
  - Value: `_________________` (full PEM content)

### DigitalOcean Secrets

- [ ] **DO_API_TOKEN**
  - Source: DigitalOcean → API → Tokens/Keys
  - Format: `dop_v1_...`
  - Value: `_________________`

- [ ] **ODOO_APP_ID**
  - Source: `doctl apps list`
  - Format: Alphanumeric ID
  - Value: `_________________`

- [ ] **SUPERSET_APP_ID**
  - Source: `doctl apps list`
  - Format: Alphanumeric ID
  - Value: `_________________`

### Optional Secrets (for future use)

- [ ] **SLACK_WEBHOOK_URL**
  - Source: Slack App → Incoming Webhooks
  - Format: `https://hooks.slack.com/services/...`
  - Value: `_________________`

- [ ] **GRAFANA_ADMIN_PASSWORD**
  - Source: Generate strong password
  - Format: Any strong password
  - Value: `_________________`

- [ ] **OCR_API_KEY**
  - Source: Generate with `openssl rand -hex 32`
  - Format: Hex string
  - Value: `_________________`

---

## 🔐 How to Add Secrets

### Via GitHub Web UI

1. Go to repository on GitHub
2. Click **Settings**
3. Navigate to **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Enter:
   - **Name**: Secret name (e.g., `APP_ID`)
   - **Value**: Secret value
6. Click **"Add secret"**

### Via GitHub CLI

```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu/Debian

# Authenticate
gh auth login

# Add secrets
gh secret set APP_ID --body "123456"
gh secret set INSTALLATION_ID --body "12345678"
gh secret set PRIVATE_KEY < path/to/private-key.pem
gh secret set DO_API_TOKEN --body "dop_v1_..."
gh secret set ODOO_APP_ID --body "abc123..."
gh secret set SUPERSET_APP_ID --body "xyz789..."

# Verify secrets
gh secret list
```

---

## 📋 Quick Commands

### Get GitHub App ID

```bash
# From GitHub App settings page URL:
https://github.com/settings/apps/pulser-hub-bot
#                                  ^^^^^^^^^^^^^^
#                                  Your app name

# App ID is shown at the top of the page
```

### Get Installation ID

```bash
# Method 1: From installation URL
https://github.com/settings/installations/12345678
#                                          ^^^^^^^^
#                                          Installation ID

# Method 2: Using GitHub API
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.github.com/app/installations
```

### Get DigitalOcean App IDs

```bash
# List all apps with IDs
doctl apps list --format ID,Spec.Name

# Get Odoo app ID
ODOO_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep odoo | awk '{print $1}')
echo "Odoo App ID: $ODOO_APP_ID"

# Get Superset app ID
SUPERSET_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep superset | awk '{print $1}')
echo "Superset App ID: $SUPERSET_APP_ID"
```

### Generate API Keys

```bash
# Generate OCR API key
OCR_API_KEY=$(openssl rand -hex 32)
echo "OCR API Key: $OCR_API_KEY"

# Generate Grafana admin password
GRAFANA_PASSWORD=$(openssl rand -base64 24)
echo "Grafana Password: $GRAFANA_PASSWORD"
```

---

## 🧪 Verify Secrets

### Test GitHub App Authentication

```bash
# Create test script
cat > test_github_app.py <<'EOF'
import os, jwt, time, requests

APP_ID = int(os.environ["APP_ID"])
INSTALLATION_ID = os.environ["INSTALLATION_ID"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"].encode()

# Create JWT
payload = {
    "iat": int(time.time()) - 60,
    "exp": int(time.time()) + 600,
    "iss": APP_ID
}
jwt_token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# Get installation token
headers = {"Authorization": f"Bearer {jwt_token}"}
url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"
response = requests.post(url, headers=headers)

if response.status_code == 201:
    print("✅ GitHub App authentication successful!")
    print(f"Token: {response.json()['token'][:20]}...")
else:
    print(f"❌ Authentication failed: {response.status_code}")
    print(response.text)
EOF

# Run test
export APP_ID="your-app-id"
export INSTALLATION_ID="your-installation-id"
export PRIVATE_KEY=$(cat path/to/private-key.pem)
python3 test_github_app.py
```

### Test DigitalOcean API

```bash
# Test API token
curl -X GET \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  https://api.digitalocean.com/v2/account

# Test app access
curl -X GET \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  https://api.digitalocean.com/v2/apps/$ODOO_APP_ID
```

---

## 🔄 Rotating Secrets

### When to Rotate

- **GitHub App Private Key**: Every 12 months or if compromised
- **DO API Token**: Every 90 days
- **API Keys**: Every 90 days or if compromised

### How to Rotate

#### GitHub App Private Key

1. Go to GitHub App settings
2. Scroll to "Private keys"
3. Click "Generate a private key"
4. Download new `.pem` file
5. Update `PRIVATE_KEY` secret in GitHub
6. Delete old private key after verification

#### DigitalOcean API Token

1. Create new token in DO dashboard
2. Update `DO_API_TOKEN` secret in GitHub
3. Test workflow with new token
4. Revoke old token in DO dashboard

#### API Keys

```bash
# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Update in GitHub
gh secret set OCR_API_KEY --body "$NEW_KEY"

# Update in PaddleOCR service .env
ssh root@ocr.insightpulseai.net "echo 'API_KEY=$NEW_KEY' >> /opt/paddleocr/.env"
ssh root@ocr.insightpulseai.net "cd /opt/paddleocr && docker-compose restart"
```

---

## 🛡️ Security Best Practices

### Secret Management

1. **Never commit secrets** to git (use `.gitignore`)
2. **Use environment-specific secrets** (dev, staging, prod)
3. **Rotate secrets regularly** (automated reminders)
4. **Monitor secret usage** (GitHub Actions logs)
5. **Revoke compromised secrets immediately**

### Access Control

1. **Limit GitHub App permissions** to minimum required
2. **Use read-only tokens** where possible
3. **Create separate tokens** for different services
4. **Review access logs** regularly

### Audit Trail

1. **Enable secret scanning** on GitHub (automatic)
2. **Monitor workflow runs** for unexpected secret usage
3. **Set up alerts** for secret access
4. **Review audit logs** monthly

---

## 📝 Template for Secret Storage

**Option 1: Password Manager (Recommended)**

Store in 1Password, LastPass, Bitwarden, etc.:

```
Title: InsightPulse GitHub Secrets
Fields:
  - APP_ID: 123456
  - INSTALLATION_ID: 12345678
  - PRIVATE_KEY: [attach .pem file]
  - DO_API_TOKEN: dop_v1_...
  - ODOO_APP_ID: abc123...
  - SUPERSET_APP_ID: xyz789...
Notes:
  - Created: 2025-11-02
  - Rotate by: 2026-02-02
  - Owner: DevOps Team
```

**Option 2: Encrypted File**

```bash
# Create encrypted secrets file
cat > secrets.txt <<EOF
APP_ID=123456
INSTALLATION_ID=12345678
PRIVATE_KEY=$(cat private-key.pem | base64)
DO_API_TOKEN=dop_v1_...
ODOO_APP_ID=abc123...
SUPERSET_APP_ID=xyz789...
EOF

# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 secrets.txt

# Delete plaintext
shred -u secrets.txt

# To decrypt later
gpg secrets.txt.gpg
```

---

## 🆘 Emergency Procedures

### If Secrets Are Compromised

1. **Immediately revoke** compromised secrets
   - GitHub: Delete private key, regenerate
   - DigitalOcean: Revoke token, create new one

2. **Generate new secrets**
   ```bash
   # New GitHub App key
   # Go to GitHub App settings → Generate new key

   # New DO token
   doctl auth init  # Follow prompts
   ```

3. **Update GitHub secrets**
   ```bash
   gh secret set PRIVATE_KEY < new-private-key.pem
   gh secret set DO_API_TOKEN --body "new-token"
   ```

4. **Verify workflow**
   ```bash
   gh workflow run ai-auto-commit.yml
   ```

5. **Document incident**
   - Create post-mortem issue
   - Update security audit log
   - Review access controls

---

## 📞 Support

If you need help with secret setup:

1. **Documentation**: Review `.github/workflows/README.md`
2. **Team**: Contact DevOps team at devops@insightpulseai.net
3. **Emergency**: Page on-call engineer

---

**Last Updated**: 2025-11-02
**Version**: 1.0.0
**Security Level**: Confidential
