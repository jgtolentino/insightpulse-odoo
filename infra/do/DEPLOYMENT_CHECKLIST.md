# DigitalOcean Deployment Checklist

Complete pre-deployment and post-deployment checklist for InsightPulse Odoo 19.0.

---

## Pre-Deployment Checklist

### 1. Prerequisites ✅

- [ ] DigitalOcean account created
- [ ] DigitalOcean API token generated
- [ ] Supabase account created
- [ ] Supabase PostgreSQL database created
- [ ] GitHub repository access configured
- [ ] `doctl` CLI installed and authenticated
- [ ] `gh` CLI installed (optional, for GitHub secrets)

### 2. Environment Configuration ✅

- [ ] `.env.example` copied to `.env` (local development only)
- [ ] Database credentials configured in `.env`
- [ ] Odoo admin password generated (`openssl rand -base64 32`)
- [ ] GitHub secrets configured (see `infra/do/secrets-template.md`)
- [ ] Environment variables verified in DigitalOcean console

**GitHub Secrets Required**:
- [ ] `DO_ACCESS_TOKEN`
- [ ] `DO_APP_ID`
- [ ] `POSTGRES_HOST`
- [ ] `POSTGRES_USER`
- [ ] `POSTGRES_PASSWORD`
- [ ] `ODOO_ADMIN_PASSWORD`

### 3. Code Quality ✅

- [ ] All Python code linted (`ruff check addons/`)
- [ ] Manifest files validated (`python scripts/validate-manifests.py`)
- [ ] Dockerfile builds successfully (`docker build -t test .`)
- [ ] No secrets committed to git (`git grep -E 'password|secret|token'`)
- [ ] `.gitignore` includes `.env` file
- [ ] Tests pass (if available)

### 4. Infrastructure Configuration ✅

- [ ] `infra/do/odoo-saas-platform.yaml` reviewed
- [ ] Instance size appropriate for workload (basic-xxs for MVP)
- [ ] Region selected (Singapore for Asia, NYC for US)
- [ ] Health check endpoint configured (`/web/health`)
- [ ] Memory limits set (80% of instance size)
- [ ] Worker configuration optimized (2 workers for 512MB)

### 5. Database Setup ✅

- [ ] Supabase project created
- [ ] Database connection tested (`psql "$POSTGRES_URL" -c "SELECT 1;"`)
- [ ] Connection pooler enabled (port 6543)
- [ ] RLS policies configured (if needed)
- [ ] Database backup configured (automatic with Supabase)

### 6. Security Review ✅

- [ ] Secrets stored in environment variables (not in code)
- [ ] Admin password is strong and unique
- [ ] Database password is strong and unique
- [ ] API tokens have minimal required scopes
- [ ] 2FA enabled on DigitalOcean account
- [ ] 2FA enabled on GitHub account
- [ ] No hardcoded credentials in repository

---

## Deployment Checklist

### 1. Initial Deployment ✅

- [ ] Create DigitalOcean app:
  ```bash
  doctl apps create --spec infra/do/odoo-saas-platform.yaml
  ```
- [ ] Note app ID from output
- [ ] Add `DO_APP_ID` to GitHub secrets
- [ ] Update environment variables in DigitalOcean console
- [ ] Create first deployment:
  ```bash
  doctl apps create-deployment [app-id] --force-rebuild
  ```

### 2. Monitor Deployment ✅

- [ ] Watch build logs:
  ```bash
  doctl apps logs [app-id] --type build --follow
  ```
- [ ] Wait for deployment to complete (10-20 minutes)
- [ ] Check deployment status:
  ```bash
  doctl apps list-deployments [app-id] --format ID,Phase,Progress
  ```
- [ ] Verify deployment is ACTIVE

### 3. Post-Deployment Verification ✅

- [ ] Get app URL:
  ```bash
  doctl apps get [app-id] --format DefaultIngress --no-header
  ```
- [ ] Health check passes:
  ```bash
  curl -sf https://[app-url]/web/health
  ```
- [ ] Main page accessible:
  ```bash
  curl -sf https://[app-url]/web
  ```
- [ ] Database selector accessible:
  ```bash
  curl -sf https://[app-url]/web/database/selector
  ```

### 4. Odoo Configuration ✅

- [ ] Access Odoo web interface: `https://[app-url]/web`
- [ ] Create database (first time only)
- [ ] Login with admin credentials
- [ ] Install base modules
- [ ] Install custom modules (InsightPulse, etc.)
- [ ] Verify all modules loaded correctly

### 5. Monitoring Setup ✅

- [ ] Configure billing alerts in DigitalOcean
- [ ] Set alert threshold to $10/month
- [ ] Monitor database size in Supabase:
  ```sql
  SELECT pg_size_pretty(pg_database_size('postgres'));
  ```
- [ ] Monitor resource usage in DigitalOcean dashboard
- [ ] Set up uptime monitoring (optional, Uptime Robot free tier)

---

## CI/CD Activation Checklist

### 1. GitHub Actions Configuration ✅

- [ ] `.github/workflows/digitalocean-deploy.yml` committed
- [ ] All GitHub secrets configured
- [ ] Workflow enabled in GitHub settings
- [ ] Branch protection rules configured (optional)

### 2. Test Automated Deployment ✅

- [ ] Push to main branch:
  ```bash
  git add .
  git commit -m "feat: enable CI/CD deployment"
  git push origin main
  ```
- [ ] Monitor workflow run:
  ```bash
  gh run list --workflow=digitalocean-deploy.yml
  gh run watch
  ```
- [ ] Verify deployment completes successfully
- [ ] Health check passes in CI/CD

### 3. Rollback Test ✅

- [ ] Note current deployment ID
- [ ] Make a small change and deploy
- [ ] Test rollback:
  ```bash
  doctl apps rollback [app-id] --deployment-id [previous-deployment-id]
  ```
- [ ] Verify rollback successful
- [ ] Re-deploy to latest version

---

## Post-Deployment Checklist

### 1. Performance Validation ✅

- [ ] Page load time <3 seconds
- [ ] Health check response time <500ms
- [ ] Database query performance acceptable
- [ ] No memory warnings in logs
- [ ] No CPU throttling warnings

### 2. Security Validation ✅

- [ ] HTTPS enabled (automatic with DigitalOcean)
- [ ] Admin panel accessible only with credentials
- [ ] Database connections encrypted (Supabase default)
- [ ] No sensitive data in logs
- [ ] Error messages don't expose system details

### 3. Monitoring Configuration ✅

- [ ] Cost alerts configured (threshold: $10/month)
- [ ] Database size monitoring enabled
- [ ] Resource usage alerts configured
- [ ] Log aggregation working
- [ ] Health checks scheduled (every 5 minutes)

### 4. Documentation ✅

- [ ] Deployment guide reviewed
- [ ] Team members have access to credentials
- [ ] Runbook created for common issues
- [ ] Architecture diagram updated
- [ ] Budget tracking sheet created

### 5. Disaster Recovery ✅

- [ ] Database backup verified (Supabase automatic daily)
- [ ] Deployment rollback tested
- [ ] Recovery time objective (RTO) documented
- [ ] Recovery point objective (RPO) documented
- [ ] Emergency contacts list created

---

## Ongoing Maintenance Checklist

### Weekly Tasks ✅

- [ ] Review deployment logs for errors
- [ ] Check database size growth
- [ ] Monitor resource usage trends
- [ ] Review cost dashboard
- [ ] Check for Odoo security updates

### Monthly Tasks ✅

- [ ] Review and rotate secrets (if needed)
- [ ] Update dependencies
- [ ] Review and optimize database queries
- [ ] Analyze performance metrics
- [ ] Review and update documentation

### Quarterly Tasks ✅

- [ ] Security audit
- [ ] Disaster recovery drill
- [ ] Performance benchmarking
- [ ] Cost optimization review
- [ ] Team training and knowledge transfer

---

## Rollback Procedures

### Emergency Rollback ✅

If deployment fails or critical issues occur:

```bash
# 1. Get previous deployment ID
doctl apps list-deployments [app-id] --format ID,Phase,CreatedAt

# 2. Rollback to previous deployment
doctl apps rollback [app-id] --deployment-id [previous-deployment-id]

# 3. Verify rollback
curl -sf https://[app-url]/web/health

# 4. Notify team
# Send notification via Slack/email

# 5. Investigate root cause
doctl apps logs [app-id] --type run --follow
```

### Planned Rollback ✅

For planned rollbacks (e.g., feature revert):

```bash
# 1. Identify target version
git log --oneline

# 2. Create rollback branch
git checkout -b rollback/[issue-description]
git revert [commit-hash]
git push origin rollback/[issue-description]

# 3. Merge and deploy
# Create PR, review, merge to main

# 4. Monitor deployment
gh run watch
```

---

## Success Criteria

### Technical ✅

- [ ] Health check response: `{"status": "ok"}`
- [ ] Page load time: <3 seconds
- [ ] Database connection: <100ms
- [ ] Memory usage: <80% of limit
- [ ] CPU usage: <50% average
- [ ] Zero critical errors in logs

### Business ✅

- [ ] Cost: <$15/month (target achieved: $5/month)
- [ ] Uptime: >99.9% (8.7 hours downtime/year max)
- [ ] User experience: Login and navigation working
- [ ] Data integrity: All records accessible
- [ ] Backup strategy: Automated daily backups

### Compliance ✅

- [ ] HTTPS enforced
- [ ] Database encrypted at rest (Supabase default)
- [ ] Connection pooling enabled
- [ ] Secrets management proper
- [ ] Audit logging enabled (Supabase)

---

## Contact Information

### Support Channels
- **DigitalOcean Support**: https://cloud.digitalocean.com/support/tickets
- **Supabase Discord**: https://discord.supabase.com
- **GitHub Issues**: https://github.com/[your-org]/insightpulse-odoo/issues

### Emergency Contacts
- **DevOps Lead**: [Name] <email@example.com>
- **Backend Lead**: [Name] <email@example.com>
- **On-call rotation**: [Link to PagerDuty/Opsgenie]

---

## Notes

- Budget: $5/month base cost (75% under $20 target)
- Region: Singapore (sgp) for Asia-Pacific
- Instance: basic-xxs (512MB RAM, 1 vCPU)
- Workers: 2 Odoo workers + 1 cron thread
- Database: Supabase Free Tier (500MB)

**Status**: Ready for deployment ✅
