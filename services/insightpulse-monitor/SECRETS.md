# Secrets Configuration Guide

This document describes how to set up secrets and environment variables for the InsightPulse Monitor MCP Server.

## GitHub Secrets

Configure these secrets in your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

#### DigitalOcean Configuration
```yaml
DO_ACCESS_TOKEN:
  description: DigitalOcean API access token
  how_to_get: |
    1. Go to https://cloud.digitalocean.com/account/api/tokens
    2. Click "Generate New Token"
    3. Name: "GitHub Actions - InsightPulse Monitor"
    4. Scopes: Read + Write
    5. Copy the token (starts with dop_v1_)
  example: "dop_v1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

DO_MONITOR_APP_ID:
  description: DigitalOcean App Platform app ID for monitor service
  how_to_get: |
    1. Create app: doctl apps create --spec services/insightpulse-monitor/app.yaml
    2. Or get existing: doctl apps list --format ID,Spec.Name
    3. Copy the app ID (UUID format)
  example: "12345678-1234-1234-1234-123456789abc"
```

#### Docker Registry
```yaml
DOCKERHUB_USERNAME:
  description: DockerHub username for image registry
  how_to_get: Your DockerHub account username
  example: "yourusername"

DOCKERHUB_TOKEN:
  description: DockerHub access token
  how_to_get: |
    1. Go to https://hub.docker.com/settings/security
    2. Click "New Access Token"
    3. Name: "GitHub Actions - InsightPulse"
    4. Permissions: Read, Write, Delete
  example: "dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### Supabase Configuration
```yaml
SUPABASE_URL:
  description: Supabase project URL
  how_to_get: |
    1. Go to https://supabase.com/dashboard/project/_/settings/api
    2. Copy "Project URL"
  example: "https://abcdefghijklmnop.supabase.co"

SUPABASE_SERVICE_KEY:
  description: Supabase service role key (full access)
  how_to_get: |
    1. Go to https://supabase.com/dashboard/project/_/settings/api
    2. Copy "service_role" key (NOT anon key)
    3. WARNING: This key has full database access
  example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  security: NEVER commit this key or expose it publicly
```

#### Odoo Configuration
```yaml
ODOO_URL:
  description: Odoo instance URL
  how_to_get: Your DigitalOcean App Platform Odoo URL
  example: "https://your-odoo-app.ondigitalocean.app"

ODOO_API_KEY:
  description: Odoo API key for authentication
  how_to_get: |
    1. Log into Odoo as admin
    2. Go to Settings → Users → Your User
    3. Under "Account Security", generate API key
  example: "your_odoo_api_key_here"
```

## DigitalOcean App Platform Secrets

After creating the app, set these environment variables:
```bash
# Using doctl CLI
doctl apps update $DO_MONITOR_APP_ID --spec services/insightpulse-monitor/app.yaml

# Set secrets via doctl
doctl apps update $DO_MONITOR_APP_ID \
  --app-spec - <<EOF
name: insightpulse-monitor
services:
  - name: monitor
    envs:
      - key: SUPABASE_URL
        value: "https://your-project.supabase.co"
        scope: RUN_TIME
        type: SECRET

      - key: SUPABASE_SERVICE_KEY
        value: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        scope: RUN_TIME
        type: SECRET

      - key: ODOO_URL
        value: "https://your-odoo-app.ondigitalocean.app"
        scope: RUN_TIME
        type: SECRET

      - key: ODOO_API_KEY
        value: "your_odoo_api_key"
        scope: RUN_TIME
        type: SECRET
EOF
```

Or via DigitalOcean web UI:
1. Go to https://cloud.digitalocean.com/apps
2. Select your "insightpulse-monitor" app
3. Go to Settings → Components → monitor
4. Edit environment variables
5. Add secrets with "Encrypted" toggle enabled

## Local Development Setup

### 1. Copy environment template
```bash
cd services/insightpulse-monitor
cp .env.example .env
```

### 2. Edit .env file
```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ODOO_URL=https://your-odoo-app.ondigitalocean.app
ODOO_API_KEY=your_odoo_api_key

# Optional
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

### 3. Test configuration
```bash
# Test with Docker Compose
docker-compose up

# Or test directly with Python
python server.py

# In another terminal, run tests
./test_mcp.sh
```

## Security Best Practices

### ✅ DO:
- Use GitHub Secrets for all sensitive data
- Use DigitalOcean encrypted environment variables
- Rotate API keys regularly (every 90 days)
- Use service role keys only on backend servers
- Keep `.env` files in `.gitignore`
- Use `SECRET` type for sensitive values in app.yaml
- Enable two-factor authentication on all accounts

### ❌ DON'T:
- Commit secrets to git repositories
- Share service role keys in Slack/email
- Use anon keys for backend services
- Store secrets in code comments
- Log sensitive environment variables
- Use same keys across dev/staging/prod
- Expose service endpoints without authentication

## Secret Rotation Schedule

| Secret | Rotation Period | How to Rotate |
|--------|----------------|---------------|
| SUPABASE_SERVICE_KEY | Every 90 days | Regenerate in Supabase dashboard → Update GitHub + DO |
| ODOO_API_KEY | Every 90 days | Regenerate in Odoo → Update GitHub + DO |
| DO_ACCESS_TOKEN | Every 180 days | Create new token → Update GitHub Secret |
| DOCKERHUB_TOKEN | Every 180 days | Create new token → Update GitHub Secret |

## Verification Checklist

Before deploying, verify:

- [ ] All GitHub Secrets are set correctly
- [ ] DigitalOcean app has all environment variables
- [ ] Supabase service key has correct permissions
- [ ] Odoo URL is accessible from internet
- [ ] No secrets are committed in git history
- [ ] `.env` file is in `.gitignore`
- [ ] Test script passes locally
- [ ] Health check endpoint works

## Troubleshooting

### "Supabase connection failed"
- Verify `SUPABASE_URL` format: `https://[project-id].supabase.co`
- Check if `SUPABASE_SERVICE_KEY` is service_role (not anon)
- Test connection: `curl $SUPABASE_URL/rest/v1/`

### "Odoo connection failed"
- Verify `ODOO_URL` is accessible: `curl $ODOO_URL/web/database/list`
- Check if API key is valid
- Ensure Odoo instance is running

### "GitHub Actions deployment failed"
- Check if all GitHub Secrets are set
- Verify `DO_MONITOR_APP_ID` is correct
- Review GitHub Actions logs for specific error
- Test doctl locally: `doctl apps get $DO_MONITOR_APP_ID`

### "Docker build failed"
- Check if `requirements.txt` is valid
- Verify Python version in Dockerfile
- Review Docker build logs in GitHub Actions

## Emergency Access

If secrets are compromised:

1. **Immediately rotate all secrets**
   ```bash
   # Supabase: Regenerate service key
   # Odoo: Regenerate API key
   # DigitalOcean: Revoke and create new token
   ```

2. **Update GitHub Secrets**
   ```bash
   # Go to repository Settings → Secrets
   # Update all compromised secrets
   ```

3. **Redeploy application**
   ```bash
   # Trigger manual deployment via GitHub Actions
   # Or: doctl apps create-deployment $DO_MONITOR_APP_ID --force-rebuild
   ```

4. **Verify new secrets work**
   ```bash
   # Run health check
   curl https://your-app.ondigitalocean.app/health

   # Run full test suite
   ./test_mcp.sh
   ```

## Support

For help with secrets configuration:
- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Internal docs: See team wiki for credential storage
