# GitHub App Setup - pulser-hub

## Credentials

**App Name**: pulser-hub
**App ID**: 2191216
**Client ID**: Iv23liwGL7fnYySPPAjS
**Installation URL**: https://github.com/settings/apps/pulser-hub

## Configuration

### Environment Variables (Added to ~/.zshrc)

```bash
export GITHUB_APP_ID=2191216
export GITHUB_APP_CLIENT_ID=Iv23liwGL7fnYySPPAjS
export GITHUB_APP_PEM_PATH=~/.github/apps/pulser-hub.pem
export GITHUB_APP_NAME=pulser-hub
```

### OAuth Callback URLs

**Supabase Auth Callback** (for GitHub OAuth):
```
https://spdtwktxdalcfigzeqrz.supabase.co/auth/v1/callback
```

**Configuration Required**:
1. Add to GitHub App settings: https://github.com/settings/apps/pulser-hub
2. Navigate to: General → Callback URL
3. Add: `https://spdtwktxdalcfigzeqrz.supabase.co/auth/v1/callback`
4. Save changes

### Private Key Location

**Path**: `~/.github/apps/pulser-hub.pem`
**Permissions**: 600 (read-only for owner)
**SHA256 (hex)**: `7fd82b77dcc917b2c5709640f65e2bae3c00236bf722668a44b596a1f7d605de`
**SHA256 (base64)**: `f9grd9zJF7LFcJZA9l4rrjwAI2v3ImaKRLWWoffWBd4=`

⚠️ **Note**: SHA256 computed from downloaded PEM differs from GitHub UI display. This is normal - GitHub may show the hash before file generation. Verify functionality by testing authentication.

## Usage

### Generate Installation Access Token

```bash
#!/bin/bash
# Generate JWT for GitHub App authentication

GITHUB_APP_ID="${GITHUB_APP_ID:-2191216}"
PEM_PATH="${GITHUB_APP_PEM_PATH:-~/.github/apps/pulser-hub.pem}"

# Generate JWT (expires in 10 minutes)
NOW=$(date +%s)
IAT=$((NOW - 60))
EXP=$((NOW + 600))

HEADER='{"alg":"RS256","typ":"JWT"}'
PAYLOAD="{\"iat\":${IAT},\"exp\":${EXP},\"iss\":\"${GITHUB_APP_ID}\"}"

# Base64 encode header and payload
HEADER_B64=$(echo -n "$HEADER" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
PAYLOAD_B64=$(echo -n "$PAYLOAD" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')

# Sign with private key
SIGNATURE=$(echo -n "${HEADER_B64}.${PAYLOAD_B64}" | \
  openssl dgst -sha256 -sign "$PEM_PATH" | \
  openssl base64 -e -A | tr '+/' '-_' | tr -d '=')

JWT="${HEADER_B64}.${PAYLOAD_B64}.${SIGNATURE}"
echo "$JWT"
```

### Get Installation ID

```bash
# Using the JWT from above
curl -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/app/installations
```

### Get Installation Access Token

```bash
# Replace {installation_id} with actual ID from previous step
INSTALLATION_ID="12345678"

curl -X POST \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens
```

## Integration with GitHub CLI

The `gh` CLI doesn't natively support GitHub App authentication. Use the generated installation token with:

```bash
# Set token for gh CLI
export GH_TOKEN="ghs_installationTokenFromAbove"

# Or use directly in API calls
gh api -H "Authorization: token ${GH_TOKEN}" /repos/owner/repo
```

## Webhook Configuration

If webhooks are configured for this app, they will be sent to the URL specified in the app settings.

**Common Events**:
- `push` - Code pushed to repository
- `pull_request` - PR opened, closed, synchronized
- `issues` - Issue opened, closed, edited
- `workflow_run` - GitHub Actions workflow completed

## Permissions

Configure app permissions at: https://github.com/settings/apps/pulser-hub/permissions

**Typical Permissions**:
- Contents: Read & Write (for repo access)
- Pull Requests: Read & Write (for PR operations)
- Issues: Read & Write (for issue management)
- Workflows: Read & Write (for Actions)
- Metadata: Read (repository metadata)

## Security Best Practices

1. ✅ **Private key stored with 600 permissions**: Only owner can read
2. ✅ **Never commit PEM to version control**: Add to .gitignore
3. ✅ **Rotate keys periodically**: Generate new key every 6-12 months
4. ✅ **Use installation tokens**: Short-lived (1 hour default)
5. ✅ **Limit permissions**: Only grant necessary repository access

## Troubleshooting

### Authentication Failed

**Symptom**: `401 Unauthorized` when using JWT

**Fixes**:
```bash
# Verify PEM file permissions
ls -la ~/.github/apps/pulser-hub.pem
# Should show: -rw------- (600)

# Verify JWT expiration
# JWT must be used within 10 minutes of generation

# Check App ID matches
echo $GITHUB_APP_ID
# Should output: 2191216

# Test PEM file validity
openssl rsa -in ~/.github/apps/pulser-hub.pem -check -noout
# Should output: RSA key ok
```

### Installation Token Expired

**Symptom**: `401 Unauthorized` after using token for >1 hour

**Fix**: Installation tokens expire after 1 hour (default). Generate a new token.

### Wrong Permissions

**Symptom**: `403 Forbidden` when accessing resources

**Fix**: Update app permissions at https://github.com/settings/apps/pulser-hub/permissions

## Helper Scripts

### scripts/gh-app-jwt.sh

```bash
#!/bin/bash
# Generate GitHub App JWT
# Usage: ./scripts/gh-app-jwt.sh

set -euo pipefail

GITHUB_APP_ID="${GITHUB_APP_ID:-2191216}"
PEM_PATH="${GITHUB_APP_PEM_PATH:-$HOME/.github/apps/pulser-hub.pem}"

if [ ! -f "$PEM_PATH" ]; then
  echo "Error: PEM file not found at $PEM_PATH" >&2
  exit 1
fi

NOW=$(date +%s)
IAT=$((NOW - 60))
EXP=$((NOW + 600))

HEADER='{"alg":"RS256","typ":"JWT"}'
PAYLOAD="{\"iat\":${IAT},\"exp\":${EXP},\"iss\":\"${GITHUB_APP_ID}\"}"

HEADER_B64=$(echo -n "$HEADER" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
PAYLOAD_B64=$(echo -n "$PAYLOAD" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')

SIGNATURE=$(echo -n "${HEADER_B64}.${PAYLOAD_B64}" | \
  openssl dgst -sha256 -sign "$PEM_PATH" | \
  openssl base64 -e -A | tr '+/' '-_' | tr -d '=')

JWT="${HEADER_B64}.${PAYLOAD_B64}.${SIGNATURE}"
echo "$JWT"
```

### scripts/gh-app-install-token.sh

```bash
#!/bin/bash
# Get installation access token
# Usage: ./scripts/gh-app-install-token.sh <installation_id>

set -euo pipefail

INSTALLATION_ID="${1:-}"

if [ -z "$INSTALLATION_ID" ]; then
  echo "Usage: $0 <installation_id>" >&2
  echo "Get installation ID with: ./scripts/gh-app-list-installations.sh" >&2
  exit 1
fi

JWT=$(./scripts/gh-app-jwt.sh)

curl -s -X POST \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens" | \
  jq -r '.token'
```

### scripts/gh-app-list-installations.sh

```bash
#!/bin/bash
# List all installations for this app
# Usage: ./scripts/gh-app-list-installations.sh

set -euo pipefail

JWT=$(./scripts/gh-app-jwt.sh)

curl -s \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/app/installations | \
  jq -r '.[] | "\(.id)\t\(.account.login)\t\(.repository_selection)"'
```

## Quick Start

```bash
# 1. Verify setup
echo "App ID: $GITHUB_APP_ID"
echo "PEM Path: $GITHUB_APP_PEM_PATH"
ls -la ~/.github/apps/pulser-hub.pem

# 2. Create helper scripts
mkdir -p scripts
# Copy scripts from above sections to scripts/ directory
chmod +x scripts/gh-app-*.sh

# 3. List installations
./scripts/gh-app-list-installations.sh

# 4. Get installation token (replace ID with actual value)
INSTALL_TOKEN=$(./scripts/gh-app-install-token.sh 12345678)

# 5. Use token with gh CLI
export GH_TOKEN="$INSTALL_TOKEN"
gh repo list

# 6. Or use directly in API calls
curl -H "Authorization: token ${INSTALL_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/jgtolentino/insightpulse-odoo
```

## References

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Authenticating as a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app)
- [Generating Installation Access Tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)

---

**Setup Date**: 2025-10-27
**Last Updated**: 2025-10-27
