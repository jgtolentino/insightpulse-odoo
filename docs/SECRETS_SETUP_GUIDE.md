# GitHub Secrets Setup Guide

**Last Updated**: 2025-11-09
**Based on**: CI/CD Audit 2025-11-04

This guide documents all GitHub secrets required for CI/CD workflows to function properly.

---

## 🚨 Critical Secrets (Required)

### DigitalOcean App Platform

```bash
# Superset App ID (fixes superset-postgres-guard.yml)
gh secret set DO_APP_ID_SUPERSET --body '73af11cb-dab2-4cb1-9770-291c536531e6'

# DigitalOcean API Token (get from https://cloud.digitalocean.com/account/api/tokens)
gh secret set DIGITALOCEAN_ACCESS_TOKEN --body 'dop_v1_YOUR_TOKEN_HERE'
```

### Droplet Configuration

```bash
# ERP Droplet
gh secret set ODOO_HOST --body '165.227.10.178'
gh secret set ODOO_SSH_USER --body 'root'
gh secret set ODOO_SSH_KEY --body "$(cat ~/.ssh/id_rsa)"

# OCR Droplet
gh secret set OCR_HOST --body '188.166.237.231'
gh secret set OCR_SSH_USER --body 'root'
gh secret set OCR_SSH_KEY --body "$(cat ~/.ssh/id_rsa)"
```

### TLS/SSL

```bash
gh secret set CERTBOT_EMAIL --body 'jgtolentino_rn@yahoo.com'
```

### API Keys

```bash
# OpenAI API (for CI autofix, code review)
gh secret set OPENAI_API_KEY --body 'sk-YOUR_KEY_HERE'

# Anthropic Claude API (for Claude autofix bot)
gh secret set ANTHROPIC_API_KEY --body 'sk-ant-YOUR_KEY_HERE'
```

---

## 📢 Optional Secrets (Notifications)

### Slack Integration

```bash
gh secret set SLACK_WEBHOOK --body 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

**How to get Slack webhook:**
1. Go to https://api.slack.com/apps
2. Create new app → Incoming Webhooks
3. Activate Incoming Webhooks → Add New Webhook to Workspace
4. Copy webhook URL

### Discord Integration

```bash
gh secret set DISCORD_WEBHOOK --body 'https://discord.com/api/webhooks/YOUR/WEBHOOK/URL'
```

**How to get Discord webhook:**
1. Go to your Discord server → Server Settings → Integrations
2. Create Webhook → Copy URL

---

## 🔒 Secrets Not Needed (Architecture Mismatch)

These were in old workflows but are no longer required:

```bash
# ❌ PRODUCTION_HOST (replaced by ODOO_HOST and OCR_HOST)
# ❌ PRODUCTION_SSH_KEY (replaced by ODOO_SSH_KEY and OCR_SSH_KEY)
# ❌ PRODUCTION_USER (replaced by ODOO_SSH_USER and OCR_SSH_USER)
# ❌ PROD_COMPOSE_DIR (not using Docker Compose)
# ❌ DOCKER_USER (not publishing to Docker Hub)
# ❌ DOCKER_PAT (not publishing to Docker Hub)
# ❌ DOCKERHUB_USERNAME (not publishing to Docker Hub)
# ❌ DOCKERHUB_TOKEN (not publishing to Docker Hub)
```

---

## ✅ Verification

### Check if secrets are set

```bash
gh secret list
```

### Test Superset Guard (requires DO_APP_ID_SUPERSET)

```bash
gh workflow run superset-postgres-guard.yml
gh run watch
```

### Test Health Monitor (requires all droplet secrets)

```bash
gh workflow run health-monitor.yml
gh run watch
```

### Test Deployment (requires all secrets)

```bash
gh workflow run odoo-deploy.yml
gh run watch
```

---

## 📊 Secrets Coverage Status

| Secret | Required For | Status | Priority |
|--------|--------------|--------|----------|
| DO_APP_ID_SUPERSET | superset-postgres-guard.yml | ❌ Missing | 🔴 High |
| DIGITALOCEAN_ACCESS_TOKEN | All DO deployments | ⚠️ Unknown | 🔴 High |
| ODOO_HOST | odoo-deploy.yml, health-monitor.yml | ❌ Missing | 🔴 High |
| OCR_HOST | deploy-ocr.yml, health-monitor.yml | ❌ Missing | 🔴 High |
| ODOO_SSH_KEY | odoo-deploy.yml | ⚠️ Unknown | 🔴 High |
| OCR_SSH_KEY | deploy-ocr.yml | ⚠️ Unknown | 🔴 High |
| CERTBOT_EMAIL | TLS certificate renewal | ⚠️ Unknown | 🟡 Medium |
| OPENAI_API_KEY | CI autofix, ai-code-review.yml | ⚠️ Unknown | 🟡 Medium |
| ANTHROPIC_API_KEY | claude-autofix-bot.yml | ⚠️ Unknown | 🟡 Medium |
| SLACK_WEBHOOK | health-monitor.yml notifications | ❌ Missing | 🟢 Low |
| DISCORD_WEBHOOK | health-monitor.yml notifications | ❌ Missing | 🟢 Low |

---

## 🔄 Secret Rotation Policy

**Recommended rotation schedule:**

- **API Keys** (OpenAI, Anthropic): Rotate every 90 days
- **DigitalOcean Access Token**: Rotate every 90 days
- **SSH Keys**: Rotate every 180 days
- **Webhooks**: No rotation needed (can be regenerated if compromised)

**How to rotate:**

```bash
# 1. Generate new credential (API key, token, SSH key)
# 2. Update the secret
gh secret set SECRET_NAME --body 'NEW_VALUE'
# 3. Test workflows to ensure they still work
# 4. Revoke old credential
```

---

## 🚀 Quick Setup (Automated)

Run the automated setup script:

```bash
chmod +x scripts/setup-missing-secrets.sh
./scripts/setup-missing-secrets.sh
```

**Note:** You'll still need to manually set sensitive secrets (API keys, SSH keys, tokens).

---

## 📞 Troubleshooting

### "Secret not found" error in workflow

**Solution:** Set the missing secret using the commands above, then re-run the workflow.

### "Invalid credentials" error

**Solution:** Verify the secret value is correct. You may need to regenerate the credential.

### Workflow still failing after setting secret

**Solution:** Check workflow logs for specific error. May need to wait a few minutes for secret to propagate.

---

## 📚 Related Documentation

- [CI/CD Audit Report](./CI_CD_AUDIT_2025-11-04.md)
- [Workflow Review](./CI_CD_WORKFLOW_REVIEW.md)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [DigitalOcean API Tokens](https://docs.digitalocean.com/reference/api/create-personal-access-token/)

---

**Last Reviewed**: 2025-11-09
**Next Review**: 2025-12-09
