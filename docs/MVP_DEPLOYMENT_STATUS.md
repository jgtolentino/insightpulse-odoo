# MVP Deployment Status

**Deployment Date**: 2025-11-08
**Branch**: pr-327-merge-fix
**Commit**: b2f26b41
**Status**: ✅ **OPERATIONAL** (Pending Token for Full Automation)

---

## Deployment Summary

Successfully deployed Mattermost Team Edition + n8n workflow automation stack on localhost with auto-generated secure credentials.

### Services Running

| Service | Container | Status | Port | Health |
|---------|-----------|--------|------|--------|
| Mattermost App | mattermost-mattermost-1 | Up 14 min | 8065 | ✅ Healthy |
| Mattermost DB | mattermost-postgres-1 | Up 14 min | - | ✅ Running |
| n8n App | n8n-n8n-1 | Up 13 min | 5678 | ✅ Running |
| n8n DB | n8n-postgres-1 | Up 13 min | - | ✅ Healthy |
| n8n Queue | n8n-redis-1 | Up 13 min | - | ✅ Healthy |

### Service Health Verification

```bash
# Mattermost API
curl http://localhost:8065/api/v4/system/ping
# Response: {"status":"OK"}

# n8n UI
curl -I http://localhost:5678/
# Response: HTTP/1.1 200 OK
```

### Access URLs

- **Mattermost**: http://localhost:8065
- **n8n**: http://localhost:5678
  - Username: `admin`
  - Password: `DV27RTfhx4YY10XUggVKNxE2t0R37zao` (from .env.mvp)

---

## Credentials Generated

All credentials auto-generated using `openssl rand -base64 32` (32-character secure random strings):

| Variable | Value | Purpose |
|----------|-------|---------|
| `N8N_BASIC_AUTH_PASSWORD` | DV27RTfhx4YY10XUggVKNxE2t0R37zao | n8n admin login |
| `N8N_POSTGRES_PASSWORD` | vsaHf8BK6LakIAyQuaxcIU9iLnLBbB7l | n8n database |
| `MM_POSTGRES_PASSWORD` | HUWBjFEjTb8JuvTtoqUIIO8iaYje6hEq | Mattermost database |
| `MM_ADMIN_TOKEN` | **(pending manual creation)** | Mattermost API access |

**Location**: `.env.mvp` (gitignored)

---

## Completed Deployment Steps

1. ✅ Created Docker Compose configurations
   - `infra/mattermost/compose.yml`
   - `infra/n8n/compose.yml`

2. ✅ Created deployment automation
   - `scripts/mvp/quickstart.sh` - One-command deployment
   - `scripts/mvp/_rand.py` - Fallback password generator
   - `scripts/mvp/seed_n8n.sh` - n8n workflow seeding
   - `scripts/mvp/seed_mattermost.sh` - Mattermost bootstrap

3. ✅ Created n8n test workflow
   - `workflows/n8n/hello_webhook.json`

4. ✅ Created CI/CD smoke tests
   - `.github/workflows/mvp_smoke.yml`

5. ✅ Updated Makefile with 6 MVP targets
   - `mvp-quickstart`, `mvp-up`, `mvp-tls`, `mvp-seed`, `mvp-verify`

6. ✅ Generated secure .env.mvp with random passwords

7. ✅ Started all 5 containers successfully

8. ✅ Verified service health

---

## Remaining Manual Steps

To complete the full automation workflow, generate a Mattermost Personal Access Token:

### Step 1: Create Mattermost Admin Account

```bash
# Open Mattermost in browser
open http://localhost:8065

# OR navigate manually to:
http://localhost:8065
```

1. Create the first user account (becomes admin automatically)
2. Fill in:
   - Email: your-email@insightpulseai.net
   - Username: admin (or your preference)
   - Password: (choose a secure password)

### Step 2: Generate Personal Access Token

1. Click profile icon (top right) → **Profile**
2. Navigate to **Account Settings** → **Security**
3. Scroll to **Personal Access Tokens**
4. Click **Create Token**
5. Description: `MVP Seeding Automation`
6. **Copy the token immediately** (shown only once)

### Step 3: Complete Seeding

```bash
# Add token to .env.mvp
echo "MM_ADMIN_TOKEN=<paste-token-here>" >> .env.mvp

# Export and run seeding
export MM_ADMIN_TOKEN='<paste-token-here>'
make mvp-seed

# Verify everything
make mvp-verify
```

---

## Expected Seeding Results

Once `MM_ADMIN_TOKEN` is set, `make mvp-seed` will:

1. **n8n Workflow Import**:
   - Import `hello_webhook` workflow
   - Activate webhook endpoint at `/webhook/hello`

2. **Mattermost Bootstrap**:
   - Create "InsightPulse" team
   - Create "General" channel
   - Post welcome message with n8n integration info

### Verification Commands

```bash
# Check n8n workflow imported
curl -u admin:DV27RTfhx4YY10XUggVKNxE2t0R37zao \
  http://localhost:5678/api/v1/workflows | jq '.data[] | select(.name=="hello_webhook")'

# Test n8n webhook
curl http://localhost:5678/webhook/hello
# Expected: "Hello from InsightPulse n8n!"

# Check Mattermost team created
curl -H "Authorization: Bearer $MM_ADMIN_TOKEN" \
  http://localhost:8065/api/v4/teams/name/insightpulse | jq '.display_name'
# Expected: "InsightPulse"
```

---

## Production Deployment (Optional)

To deploy to production domains (chat.insightpulseai.net, n8n.insightpulseai.net):

```bash
# SSH to ERP host
ssh root@165.227.10.178

# Pull latest code
cd insightpulse-odoo
git pull origin pr-327-merge-fix

# Run quickstart with TLS enabled
DOMAIN_BASE=insightpulseai.net \
ERP_HOST=165.227.10.178 \
MVP_TLS=1 \
make mvp-quickstart
```

**Prerequisites**:
- DNS A records pointing to 165.227.10.178:
  - `chat.insightpulseai.net`
  - `n8n.insightpulseai.net`
- Port 80/443 open on ERP host
- Certbot installed for Let's Encrypt TLS

---

## Architecture

```
┌─────────────────────────────────────────────┐
│ Docker Host (localhost or 165.227.10.178)  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌──────────────┐    │
│  │ Mattermost   │      │    n8n       │    │
│  │   :8065      │      │   :5678      │    │
│  └──────┬───────┘      └──────┬───────┘    │
│         │                     │            │
│         ▼                     ▼            │
│  ┌──────────────┐      ┌──────────────┐    │
│  │ PostgreSQL   │      │ PostgreSQL   │    │
│  │   :5432      │      │   :5432      │    │
│  └──────────────┘      └──────┬───────┘    │
│                                │            │
│                         ┌──────▼───────┐    │
│                         │    Redis     │    │
│                         │   :6379      │    │
│                         └──────────────┘    │
└─────────────────────────────────────────────┘
```

---

## Files Changed

**Created**:
- `infra/mattermost/compose.yml` (72 lines)
- `infra/n8n/compose.yml` (98 lines)
- `scripts/mvp/quickstart.sh` (120 lines)
- `scripts/mvp/_rand.py` (5 lines)
- `scripts/mvp/seed_n8n.sh` (65 lines)
- `scripts/mvp/seed_mattermost.sh` (85 lines)
- `workflows/n8n/hello_webhook.json` (32 lines)
- `.github/workflows/mvp_smoke.yml` (45 lines)
- `.env.mvp.example` (12 lines)
- `.env.mvp` (14 lines, gitignored)

**Modified**:
- `Makefile` (+35 lines, 6 new targets)
- `.gitignore` (+1 line, added .env.mvp)

**Total**: 11 files, ~583 lines of code

---

## Next Actions

1. **Manual**: Generate Mattermost Personal Access Token (see "Remaining Manual Steps" above)
2. **Automated**: Run `make mvp-seed` to complete workflow automation
3. **Verification**: Run `make mvp-verify` to confirm DNS, TLS, and endpoints
4. **Optional**: Deploy to production with `MVP_TLS=1 make mvp-quickstart`

---

## Support

For issues or questions:
- Check container logs: `docker logs mattermost-mattermost-1` or `docker logs n8n-n8n-1`
- Restart services: `make mvp-up`
- Full reset: `docker compose -f infra/mattermost/compose.yml down -v && docker compose -f infra/n8n/compose.yml down -v`
- CI smoke tests: `.github/workflows/mvp_smoke.yml` (runs on push to main/mvp)

---

**Deployment Engineer**: Claude (SuperClaude Framework)
**Project**: InsightPulse AI - Finance SSC
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
