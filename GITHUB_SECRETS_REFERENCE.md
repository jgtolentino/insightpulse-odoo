# GitHub Secrets Reference - InsightPulse Odoo

**Project**: jgtolentino/insightpulse-odoo
**Last Updated**: 2025-11-06

---

## 🔑 Secrets Already in Use

Based on your workflows and configs, here are the secrets you've been using:

### ✅ KNOWN VALUES (From Your Codebase)

These are already hardcoded in your config files:

```bash
# Supabase
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co

# Database (Supabase PostgreSQL)
SUPABASE_DB_USER=postgres.spdtwktxdalcfigzeqrz
SUPABASE_DB_PASSWORD=SHWYXDMFAwXI1drT
SUPABASE_DB_HOST=aws-1-us-east-1.pooler.supabase.com
SUPABASE_DB_PORT=6543

# Odoo
ODOO_ADMIN_PASSWORD=InsightPulse2025!Admin

# Superset (uses same password as DB)
SUPERSET_PASSWORD=SHWYXDMFAwXI1drT
SUPERSET_ADMIN_PASSWORD=SHWYXDMFAwXI1drT
```

---

## 🎯 Required GitHub Secrets

These need to be configured in your repository:

### **1. DigitalOcean Secrets**

```bash
# Main App IDs (get from DO dashboard or doctl)
DO_APP_ID=<odoo-app-id>              # Main Odoo ERP app
DO_APP_MCP_ID=<mcp-coordinator-id>   # MCP coordinator app
DO_APP_SUPERSET_ID=<superset-id>     # Superset analytics app
DO_MONITOR_APP_ID=<monitor-id>       # Monitoring app (optional)

# API Access Token
DO_ACCESS_TOKEN=dop_v1_xxxxx         # DigitalOcean API token
DIGITALOCEAN_ACCESS_TOKEN=<same>     # Alias for compatibility
DO_TOKEN=<same>                      # Another alias
```

**How to get DO_APP_ID values:**
```bash
# List all apps
doctl apps list

# Or if you need to create them first
doctl apps create --spec infra/do/odoo-saas-platform.yaml
doctl apps create --spec infra/do/mcp-coordinator.yaml
doctl apps create --spec infra/do/superset-app.yaml
```

### **2. Supabase Secrets**

```bash
# API Keys (from Supabase dashboard)
SUPABASE_ACCESS_TOKEN=sbp_xxxxxxxxxxxxx        # Management API token
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5...  # Anonymous/public key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsI...  # Service role key (admin)
SUPABASE_SERVICE_ROLE_KEY=<same-as-above>      # Alias

# These are already known (in your configs)
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz     # ✅ Already set
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co  # ✅ Already set
SUPABASE_DB_PASSWORD=SHWYXDMFAwXI1drT          # ✅ Already set
```

**How to get Supabase keys:**
1. Go to: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api
2. Copy:
   - **anon / public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_KEY`
3. For Management API token:
   - Go to: https://supabase.com/dashboard/account/tokens
   - Generate new token → `SUPABASE_ACCESS_TOKEN`

### **3. GitHub Container Registry**

```bash
CR_PAT=ghp_xxxxxxxxxxxxxxxxxxxxx  # Personal Access Token
```

**How to create:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `write:packages`
   - ✅ `read:packages`
   - ✅ `delete:packages`
4. Generate token and copy it

### **4. Application Passwords**

```bash
# Superset (already known from your configs)
SUPERSET_PASSWORD=SHWYXDMFAwXI1drT
SUPERSET_ADMIN_PASSWORD=SHWYXDMFAwXI1drT
SUPERSET_SECRET_KEY_PROD=<generate-random-32-char-string>

# RAG System (optional, for search/answer functions)
RAG_REINDEX_TOKEN=<optional-custom-token>
```

**Generate SUPERSET_SECRET_KEY_PROD:**
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

---

## 📝 Quick Setup Commands

### Option 1: Set Secrets Individually

```bash
# DigitalOcean
gh secret set DO_APP_ID
gh secret set DO_ACCESS_TOKEN
gh secret set DIGITALOCEAN_ACCESS_TOKEN  # Same as DO_ACCESS_TOKEN

# Supabase
gh secret set SUPABASE_ACCESS_TOKEN
gh secret set SUPABASE_ANON_KEY
gh secret set SUPABASE_SERVICE_ROLE_KEY
gh secret set SUPABASE_PROJECT_REF -b "spdtwktxdalcfigzeqrz"

# GitHub Container Registry
gh secret set CR_PAT

# Superset
gh secret set SUPERSET_PASSWORD -b "SHWYXDMFAwXI1drT"
gh secret set SUPERSET_ADMIN_PASSWORD -b "SHWYXDMFAwXI1drT"
gh secret set SUPERSET_SECRET_KEY_PROD
```

### Option 2: Set from .env File

Create a file `.github-secrets.env` (DON'T commit this):

```bash
DO_APP_ID=your-odoo-app-id
DO_ACCESS_TOKEN=dop_v1_xxxxx
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_xxxxx
SUPABASE_ACCESS_TOKEN=sbp_xxxxx
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
CR_PAT=ghp_xxxxx
SUPERSET_PASSWORD=SHWYXDMFAwXI1drT
SUPERSET_SECRET_KEY_PROD=your-random-key
```

Then set all at once:
```bash
while IFS='=' read -r key value; do
  [[ "$key" =~ ^#.*$ ]] || [[ -z "$key" ]] && continue
  gh secret set "$key" -b "$value"
done < .github-secrets.env
```

---

## 🔍 Check What's Currently Set

```bash
# List all secrets (doesn't show values, just names)
gh secret list

# Example output:
# DO_APP_ID               Updated 2025-11-06
# DO_ACCESS_TOKEN         Updated 2025-11-06
# SUPABASE_ACCESS_TOKEN   Updated 2025-11-06
# CR_PAT                  Updated 2025-11-06
```

---

## 📊 Secrets Usage by Workflow

### `deploy-unified.yml` (Main deployment)
- ✅ SUPABASE_PROJECT_REF
- ✅ DO_APP_ID
- ✅ CR_PAT
- ✅ SUPABASE_ACCESS_TOKEN
- ✅ DIGITALOCEAN_ACCESS_TOKEN
- ✅ SUPABASE_ANON_KEY
- ✅ RAG_REINDEX_TOKEN (optional)
- ✅ SUPERSET_PASSWORD

### `deploy-mcp.yml` (MCP Coordinator)
- ✅ DO_APP_MCP_ID
- ✅ DIGITALOCEAN_ACCESS_TOKEN
- ✅ SUPABASE_ANON_KEY

### `deploy-superset.yml` (Superset Analytics)
- ✅ DO_APP_SUPERSET_ID
- ✅ DIGITALOCEAN_ACCESS_TOKEN
- ✅ SUPERSET_SECRET_KEY_PROD
- ✅ SUPABASE_DB_PASSWORD
- ✅ SUPERSET_ADMIN_PASSWORD
- ✅ SUPABASE_ANON_KEY

### `integration-tests.yml` (Testing)
- ✅ SUPERSET_ADMIN_PASSWORD
- ✅ SUPABASE_ANON_KEY

### `performance-testing.yml` (Load tests)
- ✅ SUPABASE_DB_PASSWORD

---

## 🎯 Minimal Set for Backend Deployment

If you just want to deploy the backend right now, you ONLY need:

```bash
# Core 5 secrets
gh secret set DO_APP_ID              # Your Odoo app ID
gh secret set DO_ACCESS_TOKEN        # DigitalOcean API token
gh secret set SUPABASE_ACCESS_TOKEN  # Supabase management token
gh secret set CR_PAT                 # GitHub packages token
gh secret set DIGITALOCEAN_ACCESS_TOKEN  # Alias for DO_ACCESS_TOKEN (same value)

# These are already in your configs
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz  # Already hardcoded
SUPABASE_DB_PASSWORD=SHWYXDMFAwXI1drT      # Already hardcoded
ODOO_ADMIN_PASSWORD=InsightPulse2025!Admin # Already hardcoded
```

---

## 🚨 Security Notes

1. **NEVER commit secrets to git**
2. **Rotate tokens periodically** (every 90 days recommended)
3. **Use separate tokens for prod/staging** (when you set up staging)
4. **Backup your secrets** in a password manager (1Password, Bitwarden, etc.)
5. **Current passwords are in your configs** - Consider rotating them after initial deployment

---

## 📖 Related Documentation

- Main Deployment Plan: `DEPLOYMENT_PLAN.md`
- Infrastructure Architecture: `infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md`
- Secrets Configuration: `infra/do/SECRETS_SETUP.md`
- CI/CD Automation: `docs/CI_CD_AUTOMATION_COMPLETE.md`

---

## 🎬 Next Steps

1. **Get your DO app IDs:**
   ```bash
   # Install doctl if not already
   brew install doctl  # macOS

   # Authenticate
   doctl auth init

   # List existing apps (or create new ones)
   doctl apps list
   ```

2. **Get Supabase keys:**
   - Visit: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api
   - Copy the keys shown there

3. **Create GitHub PAT:**
   - Visit: https://github.com/settings/tokens
   - Generate new token with `write:packages` scope

4. **Set all secrets:**
   ```bash
   gh secret set DO_APP_ID
   gh secret set DO_ACCESS_TOKEN
   gh secret set SUPABASE_ACCESS_TOKEN
   gh secret set CR_PAT
   gh secret set DIGITALOCEAN_ACCESS_TOKEN
   ```

5. **Deploy!**
   ```bash
   ./scripts/deploy-full-stack.sh --backend-only
   ```

---

**Last Updated**: 2025-11-06
**Maintained By**: InsightPulse DevOps Team
