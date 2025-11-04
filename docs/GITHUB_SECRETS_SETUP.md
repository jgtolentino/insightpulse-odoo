# GitHub Actions Secrets Setup

Complete guide for configuring GitHub Actions secrets for InsightPulse infrastructure.

## Required Secrets

### Quick Setup (Bulk Commands)

```bash
# Navigate to repository
cd /Users/tbwa/insightpulse-odoo

# Use gh CLI to set secrets
# Install: brew install gh

# 1. OpenAI API (for AI-powered features)
gh secret set OPENAI_API_KEY --body 'sk-YOUR_OPENAI_KEY'

# 2. DigitalOcean (for deployments)
gh secret set DO_API_TOKEN --body 'dop_v1_YOUR_DO_TOKEN'
gh secret set DIGITALOCEAN_ACCESS_TOKEN --body 'dop_v1_YOUR_DO_TOKEN'  # Alias

# 3. App Platform IDs
gh secret set DO_APP_ID_SUPERSET --body 'PASTE_FROM_DO_DASHBOARD'
gh secret set DO_APP_ID_MCP --body 'PASTE_FROM_DO_DASHBOARD'
gh secret set DO_APP_ID_LANDING --body 'PASTE_FROM_DO_DASHBOARD'

# 4. ERP Droplet SSH (165.227.10.178)
gh secret set ODOO_HOST --body '165.227.10.178'
gh secret set ODOO_SSH_USER --body 'root'
gh secret set ODOO_SSH_KEY --body "$(cat ~/.ssh/id_rsa)"

# 5. OCR Droplet SSH (188.166.237.231)
gh secret set OCR_HOST --body '188.166.237.231'
gh secret set OCR_SSH_USER --body 'root'
gh secret set OCR_SSH_KEY --body "$(cat ~/.ssh/id_rsa)"

# 6. Let's Encrypt
gh secret set CERTBOT_EMAIL --body 'jgtolentino_rn@yahoo.com'

# 7. Supabase (for Superset and migrations)
gh secret set SUPABASE_URL --body 'https://spdtwktxdalcfigzeqrz.supabase.co'
gh secret set SUPABASE_ANON_KEY --body 'YOUR_ANON_KEY'
gh secret set SUPABASE_SERVICE_ROLE_KEY --body 'YOUR_SERVICE_ROLE_KEY'
gh secret set SUPERSET_DATABASE_URL --body 'postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&options=-csearch_path%3Dsuperset'

# 8. Backups (DigitalOcean Spaces S3-compatible)
gh secret set S3_ENDPOINT --body 'https://sgp1.digitaloceanspaces.com'
gh secret set S3_BUCKET --body 'insightpulse-backups'
gh secret set S3_ACCESS_KEY --body 'YOUR_SPACES_KEY'
gh secret set S3_SECRET_KEY --body 'YOUR_SPACES_SECRET'

# 9. Alerts (optional)
gh secret set SLACK_WEBHOOK_URL --body 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

---

## Secret Details

### 1. OpenAI API

**Required by:**
- AI-powered features
- OCR post-processing
- Agent workflows

**Obtain:**
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key (starts with `sk-`)

**Set:**
```bash
gh secret set OPENAI_API_KEY --body 'sk-...'
```

---

### 2. DigitalOcean Access Token

**Required by:**
- `deploy-nginx.yml`
- `superset-postgres-guard.yml`
- App Platform deployments

**Obtain:**
1. Go to: https://cloud.digitalocean.com/account/api/tokens
2. Generate New Token
3. Name: "GitHub Actions insightpulse-odoo"
4. Scopes: Read & Write
5. Copy token (starts with `dop_v1_`)

**Set:**
```bash
gh secret set DO_API_TOKEN --body 'dop_v1_...'
gh secret set DIGITALOCEAN_ACCESS_TOKEN --body 'dop_v1_...'  # Alias
```

---

### 3. App Platform IDs

**Required by:**
- Deployment workflows
- Health checks
- Automated updates

**Obtain:**
```bash
# List all apps
doctl apps list

# Get specific app ID
doctl apps get superset-nlavf --format ID

# Or from URL in DO dashboard
# https://cloud.digitalocean.com/apps/[APP_ID]/settings
```

**Set:**
```bash
# Superset BI
gh secret set DO_APP_ID_SUPERSET --body 'PASTE_APP_ID_HERE'

# MCP Skill Hub
gh secret set DO_APP_ID_MCP --body 'PASTE_APP_ID_HERE'

# Landing page
gh secret set DO_APP_ID_LANDING --body 'PASTE_APP_ID_HERE'
```

---

### 4. ERP Droplet SSH

**Required by:**
- `deploy-nginx.yml`
- Odoo module deployment
- Remote script execution

**Obtain:**
```bash
# Use existing SSH key or generate new one
ssh-keygen -t rsa -b 4096 -C "github-actions@insightpulse" -f ~/.ssh/insightpulse_deploy

# Add public key to droplet
doctl compute ssh-key import github-actions --public-key-file ~/.ssh/insightpulse_deploy.pub

# Or manually:
ssh root@165.227.10.178
echo "PASTE_PUBLIC_KEY" >> ~/.ssh/authorized_keys
```

**Set:**
```bash
gh secret set ODOO_HOST --body '165.227.10.178'
gh secret set ODOO_SSH_USER --body 'root'
gh secret set ODOO_SSH_KEY --body "$(cat ~/.ssh/insightpulse_deploy)"
```

---

### 5. OCR Droplet SSH

**Required by:**
- OCR service deployment
- Model updates
- Health checks

**Set:**
```bash
gh secret set OCR_HOST --body '188.166.237.231'
gh secret set OCR_SSH_USER --body 'root'
gh secret set OCR_SSH_KEY --body "$(cat ~/.ssh/insightpulse_deploy)"
```

---

### 6. Let's Encrypt Email

**Required by:**
- `deploy-nginx.yml` (certbot)
- TLS certificate issuance
- Renewal notifications

**Set:**
```bash
gh secret set CERTBOT_EMAIL --body 'jgtolentino_rn@yahoo.com'
```

---

### 7. Supabase

**Required by:**
- Superset database connection
- Schema migrations
- Data pipeline workflows

**Obtain:**
1. Go to: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api
2. Copy Project URL
3. Copy anon public key
4. Copy service_role secret key

**Set:**
```bash
gh secret set SUPABASE_URL --body 'https://spdtwktxdalcfigzeqrz.supabase.co'
gh secret set SUPABASE_ANON_KEY --body 'eyJhbGci...'
gh secret set SUPABASE_SERVICE_ROLE_KEY --body 'eyJhbGci...'

# Superset connection string (with search_path)
gh secret set SUPERSET_DATABASE_URL --body 'postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&options=-csearch_path%3Dsuperset'
```

---

### 8. Backup Storage (DigitalOcean Spaces)

**Required by:**
- Automated backups
- Disaster recovery
- Snapshot storage

**Obtain:**
1. Go to: https://cloud.digitalocean.com/spaces
2. Create Space: `insightpulse-backups` (Singapore region)
3. Go to: API → Spaces access keys
4. Generate new key pair

**Set:**
```bash
gh secret set S3_ENDPOINT --body 'https://sgp1.digitaloceanspaces.com'
gh secret set S3_BUCKET --body 'insightpulse-backups'
gh secret set S3_ACCESS_KEY --body 'YOUR_ACCESS_KEY'
gh secret set S3_SECRET_KEY --body 'YOUR_SECRET_KEY'
```

---

### 9. Slack Alerts (Optional)

**Required by:**
- Health monitoring
- Deployment notifications
- Error alerts

**Obtain:**
1. Go to: https://api.slack.com/apps
2. Create new app
3. Enable Incoming Webhooks
4. Add webhook to channel
5. Copy webhook URL

**Set:**
```bash
gh secret set SLACK_WEBHOOK_URL --body 'https://hooks.slack.com/services/...'
```

---

## Verification

### List All Secrets

```bash
gh secret list
```

**Expected output:**
```
CERTBOT_EMAIL                    Updated 2025-11-04
DIGITALOCEAN_ACCESS_TOKEN        Updated 2025-11-04
DO_API_TOKEN                     Updated 2025-11-04
DO_APP_ID_LANDING                Updated 2025-11-04
DO_APP_ID_MCP                    Updated 2025-11-04
DO_APP_ID_SUPERSET               Updated 2025-11-04
OCR_HOST                         Updated 2025-11-04
OCR_SSH_KEY                      Updated 2025-11-04
OCR_SSH_USER                     Updated 2025-11-04
ODOO_HOST                        Updated 2025-11-04
ODOO_SSH_KEY                     Updated 2025-11-04
ODOO_SSH_USER                    Updated 2025-11-04
OPENAI_API_KEY                   Updated 2025-11-04
S3_ACCESS_KEY                    Updated 2025-11-04
S3_BUCKET                        Updated 2025-11-04
S3_ENDPOINT                      Updated 2025-11-04
S3_SECRET_KEY                    Updated 2025-11-04
SLACK_WEBHOOK_URL                Updated 2025-11-04
SUPABASE_ANON_KEY                Updated 2025-11-04
SUPABASE_SERVICE_ROLE_KEY        Updated 2025-11-04
SUPABASE_URL                     Updated 2025-11-04
SUPERSET_DATABASE_URL            Updated 2025-11-04
```

### Check Secrets Used by Workflows

```bash
grep -Rho "\${{ *secrets\.[A-Z0-9_]\+ *}}" .github/workflows | \
  sed -E 's/.*secrets\.([A-Z0-9_]+).*/\1/' | \
  sort -u
```

**Compare output with `gh secret list` to find missing secrets.**

---

## Security Best Practices

### ✅ DO:
- Rotate secrets every 90 days
- Use separate keys for CI/CD (not personal keys)
- Limit secret scope to necessary repositories
- Use environment-specific secrets for staging/production
- Monitor secret usage in Actions logs

### ❌ DON'T:
- Hardcode secrets in workflows or code
- Share secrets via Slack/email
- Use personal API keys for CI/CD
- Commit secrets to repository (even in .env.example)
- Echo full secrets in logs (use masking)

### Secret Masking in Workflows

GitHub Actions automatically masks secrets in logs, but be careful:

```yaml
# ✅ GOOD: Secret is masked
- run: echo "Token: ${{ secrets.OPENAI_API_KEY }}"

# ❌ BAD: Exposes secret if assigned to variable
- run: |
    TOKEN=${{ secrets.OPENAI_API_KEY }}
    echo "Token is: $TOKEN"  # NOT MASKED!

# ✅ GOOD: Use mask command
- run: |
    echo "::add-mask::${{ secrets.OPENAI_API_KEY }}"
    TOKEN=${{ secrets.OPENAI_API_KEY }}
    echo "Token set"
```

---

## Troubleshooting

### Workflow failing with "Secret not found"

**Solution:**
```bash
# Check secret name matches exactly (case-sensitive)
gh secret list

# Set missing secret
gh secret set SECRET_NAME --body 'value'
```

### SSH connection failing

**Solution:**
```bash
# Test SSH key locally first
ssh -i ~/.ssh/insightpulse_deploy root@165.227.10.178

# Verify key is added to droplet
ssh root@165.227.10.178 'cat ~/.ssh/authorized_keys'

# Check GitHub secret contains full private key
gh secret set ODOO_SSH_KEY --body "$(cat ~/.ssh/insightpulse_deploy)"
```

### Superset database connection failing

**Solution:**
```bash
# Test connection string locally
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&options=-csearch_path%3Dsuperset"

# Verify URL encoding for options parameter
# Space becomes %3D, comma becomes %2C
```

---

## Secrets Rotation Schedule

| Secret | Rotation Period | Priority |
|--------|----------------|----------|
| `OPENAI_API_KEY` | 90 days | High |
| `DO_API_TOKEN` | 90 days | Critical |
| `ODOO_SSH_KEY` | 180 days | Critical |
| `OCR_SSH_KEY` | 180 days | Critical |
| `SUPABASE_SERVICE_ROLE_KEY` | Manual (on breach) | Critical |
| `S3_ACCESS_KEY` | 180 days | Medium |
| `SLACK_WEBHOOK_URL` | Manual (on breach) | Low |

**Rotation Procedure:**
1. Generate new secret in source system
2. Update GitHub secret: `gh secret set SECRET_NAME --body 'new_value'`
3. Test in non-production workflow (manual dispatch)
4. Monitor for 24 hours
5. Revoke old secret in source system

---

## Additional Resources

- **GitHub Docs:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **DO API Tokens:** https://docs.digitalocean.com/reference/api/create-personal-access-token/
- **Supabase API:** https://supabase.com/docs/guides/api
- **gh CLI:** https://cli.github.com/manual/gh_secret
