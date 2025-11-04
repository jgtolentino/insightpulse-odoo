# Deployment Ready Checklist

## Overview
This checklist ensures all components are ready for production deployment to DigitalOcean App Platform.

## Pre-Deployment Verification

### 1. Repository & Source Code ✅
- [x] Custom Docker images built and tested
  - `/workspaces/insightpulse-odoo/Dockerfile.custom` (Odoo)
  - `/workspaces/insightpulse-odoo/docker/superset/Dockerfile` (Superset)
  - `/workspaces/insightpulse-odoo/services/mcp-hub/Dockerfile` (MCP)
- [x] All required files present in repository
- [x] GitHub repository accessible: `jgtolentino/insightpulse-odoo`
- [x] Branch exists: `main`

### 2. Infrastructure Specifications ✅
- [x] Odoo spec updated: `infra/do/odoo-saas-platform.yaml`
  - Custom Docker image reference: `Dockerfile.custom`
  - Environment variables configured
  - Health checks configured
  - Resource limits: basic-xxs (512MB)
- [x] Superset spec updated: `infra/superset/superset-app.yaml`
  - 3 services: web, worker, beat
  - Redis service included
  - Supabase PostgreSQL connection
  - Health endpoints configured
  - Resource limits: basic-xs (web), basic-xxs (workers)
- [x] MCP spec updated: `infra/do/mcp-coordinator.yaml`
  - FastAPI service configured
  - Custom domain: mcp.insightpulseai.net
  - Health endpoint configured
  - Resource limits: basic-xxs (512MB)

### 3. Database Configuration ⏳
- [ ] Supabase project created
  - Project ID: spdtwktxdalcfigzeqrz
  - Region: AWS US East 1
- [ ] Connection pooler enabled (port 6543)
- [ ] Database credentials secured
  - Host: `aws-1-us-east-1.pooler.supabase.com`
  - User: `postgres.spdtwktxdalcfigzeqrz`
  - Password: (stored in secrets manager)
- [ ] Firewall rules configured (allow DO App Platform IPs)

### 4. Secrets Management ⏳
Generate and configure these secrets in DigitalOcean dashboard:

#### Odoo Secrets
- [ ] `ODOO_DB_PASSWORD` - Supabase PostgreSQL password
- [ ] `ODOO_ADMIN_PASSWORD` - Generate: `openssl rand -base64 32`
- [ ] `DO_AGENT_KEY` - DigitalOcean Gradient AI agent key (optional)
- [ ] `DO_MODEL_ACCESS_KEY` - DigitalOcean Gradient AI model key (optional)

#### Superset Secrets
- [ ] `DATABASE_PASSWORD` - Supabase PostgreSQL password (same as Odoo)
- [ ] `SUPERSET_SECRET_KEY` - Generate: `openssl rand -base64 42`
- [ ] `SUPERSET_ADMIN_PASSWORD` - Superset admin password

#### MCP Secrets
- [ ] `GITHUB_TOKEN` - GitHub personal access token
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- [ ] `DO_API_TOKEN` - DigitalOcean API token
- [ ] `SUPERSET_PASSWORD` - Superset admin password (same as above)
- [ ] `ODOO_ADMIN_PASSWORD` - Odoo admin password (same as above)
- [ ] `DO_AGENT_KEY` - DigitalOcean Gradient AI key (same as Odoo)
- [ ] `DO_MODEL_ACCESS_KEY` - DigitalOcean Gradient AI key (same as Odoo)
- [ ] `NOTION_TOKEN` - Notion integration token (optional)

### 5. DNS Configuration ⏳
- [ ] Domain ownership verified: insightpulseai.net
- [ ] Access to DNS management (Namecheap/Cloudflare/GoDaddy)
- [ ] CNAME records ready to create:
  - `mcp.insightpulseai.net`
  - `superset.insightpulseai.net`
  - `odoo.insightpulseai.net` (optional)

### 6. DigitalOcean Setup ⏳
- [ ] DigitalOcean account active
- [ ] Payment method added
- [ ] API token generated (read + write access)
- [ ] `doctl` CLI installed and configured
  ```bash
  doctl auth init
  doctl apps list  # Verify access
  ```

## Deployment Execution

### Phase 1: Deploy Infrastructure

#### Step 1: Deploy Odoo SaaS Platform
```bash
# Deploy
doctl apps create --spec infra/do/odoo-saas-platform.yaml

# Capture app ID
ODOO_APP_ID=$(doctl apps list --format ID,Spec.Name | grep odoo-saas-platform | awk '{print $1}')
echo "Odoo App ID: $ODOO_APP_ID"

# Monitor deployment
doctl apps get $ODOO_APP_ID
doctl apps logs $ODOO_APP_ID --type build --follow
```

**Expected Cost**: $5/month

#### Step 2: Deploy Superset Analytics
```bash
# Deploy
doctl apps create --spec infra/superset/superset-app.yaml

# Capture app ID
SUPERSET_APP_ID=$(doctl apps list --format ID,Spec.Name | grep superset-analytics | awk '{print $1}')
echo "Superset App ID: $SUPERSET_APP_ID"

# Monitor deployment
doctl apps get $SUPERSET_APP_ID
doctl apps logs $SUPERSET_APP_ID --type build --follow
```

**Expected Cost**: $27/month (web + worker + beat + redis)

#### Step 3: Deploy MCP Coordinator
```bash
# Deploy
doctl apps create --spec infra/do/mcp-coordinator.yaml

# Capture app ID
MCP_APP_ID=$(doctl apps list --format ID,Spec.Name | grep mcp-coordinator | awk '{print $1}')
echo "MCP App ID: $MCP_APP_ID"

# Monitor deployment
doctl apps get $MCP_APP_ID
doctl apps logs $MCP_APP_ID --type build --follow
```

**Expected Cost**: $5/month

### Phase 2: Configure DNS

#### Get App URLs
```bash
# Get default DigitalOcean URLs
doctl apps get $ODOO_APP_ID --format DefaultIngress
doctl apps get $SUPERSET_APP_ID --format DefaultIngress
doctl apps get $MCP_APP_ID --format DefaultIngress
```

#### Add DNS Records
See `DNS_RECORDS.md` for detailed instructions.

```
CNAME: mcp.insightpulseai.net → mcp-coordinator-<app-id>.ondigitalocean.app
CNAME: superset.insightpulseai.net → superset-analytics-<app-id>.ondigitalocean.app
CNAME: odoo.insightpulseai.net → odoo-saas-platform-<app-id>.ondigitalocean.app
```

#### Verify DNS Propagation
```bash
# Wait 5-60 minutes, then verify
dig mcp.insightpulseai.net
dig superset.insightpulseai.net
dig odoo.insightpulseai.net
```

### Phase 3: Configure Secrets

#### Via DigitalOcean Dashboard
1. Navigate to App Platform → Select app → Settings → Environment Variables
2. Add secrets marked as `type: SECRET` in the YAML specs
3. Restart app after adding secrets

#### Via CLI (Alternative)
```bash
# Example: Add Odoo database password
doctl apps update $ODOO_APP_ID --spec <(
  cat infra/do/odoo-saas-platform.yaml | \
  sed 's/value: ""/value: "YOUR_PASSWORD_HERE"/'
)
```

### Phase 4: Verify Deployments

#### Health Checks
```bash
# Wait for SSL provisioning (15-30 minutes), then test
curl -f https://mcp.insightpulseai.net/health
curl -f https://superset.insightpulseai.net/health
curl -f https://odoo.insightpulseai.net/web/health
```

Expected responses:
- MCP: `{"status":"ok"}`
- Superset: HTTP 200 OK
- Odoo: HTTP 200 OK

#### Service Status
```bash
# Check all apps
doctl apps list

# Check specific app
doctl apps get $ODOO_APP_ID --format Phase
doctl apps get $SUPERSET_APP_ID --format Phase
doctl apps get $MCP_APP_ID --format Phase
```

Expected: `ACTIVE`

#### View Logs
```bash
# Odoo
doctl apps logs $ODOO_APP_ID --type run --tail 100

# Superset (web)
doctl apps logs $SUPERSET_APP_ID --type run --component superset-web --tail 100

# Superset (worker)
doctl apps logs $SUPERSET_APP_ID --type run --component superset-worker --tail 100

# MCP
doctl apps logs $MCP_APP_ID --type run --tail 100
```

## Post-Deployment Tasks

### 1. Initialize Odoo
```bash
# Access Odoo web interface
open https://odoo.insightpulseai.net

# First-time setup:
# - Select database name
# - Set admin email/password
# - Choose demo data (recommended: No)
```

### 2. Initialize Superset
```bash
# Access Superset web interface
open https://superset.insightpulseai.net

# Login with credentials from YAML:
# Username: admin
# Password: <SUPERSET_ADMIN_PASSWORD>

# Add data source:
# - Database: PostgreSQL
# - Host: aws-1-us-east-1.pooler.supabase.com
# - Port: 6543
# - Database: postgres
# - Username: postgres.spdtwktxdalcfigzeqrz
# - Password: <DATABASE_PASSWORD>
```

### 3. Test MCP Coordinator
```bash
# Test health endpoint
curl https://mcp.insightpulseai.net/health

# Test API documentation
open https://mcp.insightpulseai.net/docs

# Test integration endpoints (if applicable)
curl https://mcp.insightpulseai.net/api/v1/status
```

### 4. Configure Monitoring
- [ ] Set up DigitalOcean alerts (CPU, memory, response time)
- [ ] Configure Supabase database alerts
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure log aggregation (optional)

### 5. Security Hardening
- [ ] Review and rotate all secrets
- [ ] Enable two-factor authentication on DO account
- [ ] Configure IP whitelisting (if applicable)
- [ ] Review firewall rules
- [ ] Enable database backups in Supabase

### 6. Documentation
- [ ] Document admin credentials (use password manager)
- [ ] Update internal wiki/docs with URLs
- [ ] Share access with team members
- [ ] Document any custom configurations

## Cost Summary

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Odoo SaaS Platform | 1x basic-xxs (512MB) | $5.00 |
| Superset Web | 1x basic-xs (1GB) | $12.00 |
| Superset Worker | 1x basic-xxs (512MB) | $5.00 |
| Superset Beat | 1x basic-xxs (512MB) | $5.00 |
| Redis | 1x basic-xxs (512MB) | $5.00 |
| MCP Coordinator | 1x basic-xxs (512MB) | $5.00 |
| **TOTAL** | | **$37.00** |

**External Services** (not billed via DO):
- Supabase PostgreSQL: **Free** (500MB database)
- DigitalOcean Gradient AI: **Pay-per-use** (usage-based)

**Total estimated cost**: **$37-45/month** (depending on AI usage)

## Rollback Plan

If deployment fails or issues arise:

### Rollback Odoo
```bash
# Delete app
doctl apps delete $ODOO_APP_ID

# Redeploy previous version (if exists)
git checkout <previous-commit>
doctl apps create --spec infra/do/odoo-saas-platform.yaml
```

### Rollback Superset
```bash
doctl apps delete $SUPERSET_APP_ID
# Redeploy from backup spec
```

### Rollback MCP
```bash
doctl apps delete $MCP_APP_ID
# Redeploy from backup spec
```

## Support Contacts

- **DigitalOcean Support**: https://cloud.digitalocean.com/support
- **Supabase Support**: https://supabase.com/support
- **GitHub Support**: https://support.github.com
- **Internal Team**: [Add contact information]

## Sign-off

Deployment completed by: ___________________________

Date: ___________________________

Verified by: ___________________________

Date: ___________________________

## Next Steps After Deployment

1. **Week 1**: Monitor performance and error logs daily
2. **Week 2**: Fine-tune resource allocation based on usage
3. **Week 3**: Configure automated backups and disaster recovery
4. **Week 4**: Set up CI/CD pipelines for automated deployments
5. **Month 2**: Review costs and optimize instance sizes

## Resources

- **Architecture Diagram**: `DEPLOYMENT_ARCHITECTURE.md`
- **DNS Configuration**: `DNS_RECORDS.md`
- **Deployment Scripts**: `deploy-production.sh`
- **Smoke Tests**: `smoke-tests.sh`
- **Monitoring Setup**: `setup-monitoring.sh`

---

**Status Legend**:
- ✅ Completed
- ⏳ Pending
- ❌ Blocked
- 🔄 In Progress
