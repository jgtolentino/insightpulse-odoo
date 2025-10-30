# Apache Superset Production Deployment Guide

## Overview

This guide covers deploying Apache Superset to production at `http://insightpulseai.net/superset` using DigitalOcean App Platform with Supabase PostgreSQL and Traefik reverse proxy.

**Architecture:**
```
Client → Traefik (HTTPS/Path Routing) → DigitalOcean App Platform
                                          ├── Superset Web (Gunicorn/gevent)
                                          ├── Superset Worker (Celery)
                                          ├── Superset Beat (Scheduler)
                                          └── Redis (Cache)
                                                    ↓
                                          Supabase PostgreSQL (Metadata DB)
```

## Prerequisites

### 1. Required Tools
- ✅ `doctl` - DigitalOcean CLI ([install guide](https://docs.digitalocean.com/reference/doctl/how-to/install/))
- ✅ `git` - Version control
- ✅ Access to DigitalOcean account with App Platform enabled
- ✅ Access to Supabase project (spdtwktxdalcfigzeqrz)

### 2. Environment Variables

Add to `~/.zshrc` or export before deployment:

```bash
# Supabase PostgreSQL (default: Postgres_26)
export POSTGRES_PASSWORD="Postgres_26"

# Superset Security (pre-configured defaults)
export SUPERSET_SECRET_KEY="8UToEhL2C0ovd7S4maFPsi7e4mU05pqAH907G5yUaLsr9prnJdHu7+6k"
export SUPERSET_ADMIN_PASSWORD="Postgres_26"

# Optional: Redis password if using managed Redis
export REDIS_PASSWORD="redis_password"
```

**Note**: Defaults are pre-configured in deployment script. Only export if you want to override.

Reload shell configuration:
```bash
source ~/.zshrc
```

## Deployment Steps

### Step 1: Verify Configuration Files

Ensure all required files are in place:

```bash
# Check deployment files
ls -la infra/superset/
ls -la config/superset/
ls -la docker/superset/
ls -la deploy/superset/
```

**Required files:**
- ✅ `infra/superset/superset-app.yaml` - DO App Platform spec
- ✅ `config/superset/superset_config_production.py` - Production config
- ✅ `docker/superset/Dockerfile` - Production image
- ✅ `docker/superset/entrypoint.sh` - Initialization script
- ✅ `deploy/superset/deploy.sh` - Deployment automation
- ✅ `deploy/superset/traefik.yml` - Reverse proxy config

### Step 2: Authenticate to DigitalOcean

```bash
# Initialize doctl authentication
doctl auth init

# Verify authentication
doctl auth list

# Verify access to App Platform
doctl apps list
```

### Step 3: Deploy to DigitalOcean App Platform

**Option A: Automated Deployment (Recommended)**

```bash
# Run deployment script
./deploy/superset/deploy.sh
```

The script will:
1. Check prerequisites
2. Verify environment variables
3. Create or update the app
4. Initiate deployment
5. Monitor deployment logs
6. Display post-deployment instructions

**Option B: Manual Deployment**

```bash
# Create app from spec
doctl apps create --spec infra/superset/superset-app.yaml

# Get app ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "superset-analytics" | awk '{print $1}')

# Monitor deployment
doctl apps logs $APP_ID --follow
```

### Step 4: Configure Secrets in DO Dashboard

**Pre-configured Secrets**: Secrets are already set in the App Platform spec with default values:
- `POSTGRES_PASSWORD` = `Postgres_26`
- `SUPERSET_SECRET_KEY` = `8UToEhL2C0ovd7S4maFPsi7e4mU05pqAH907G5yUaLsr9prnJdHu7+6k`
- `SUPERSET_ADMIN_PASSWORD` = `Postgres_26`

**Optional**: To change secrets in DigitalOcean dashboard:

1. Go to: https://cloud.digitalocean.com/apps/[APP_ID]
2. Navigate to: **Settings** → **Environment Variables**
3. Edit the **SECRET** variables if needed
4. Click **Save** → App will automatically redeploy

### Step 5: Verify Deployment

**Health Check:**
```bash
# Get app URL
APP_URL=$(doctl apps get $APP_ID --format LiveURL --no-header)

# Check health endpoint
curl -f $APP_URL/health

# Expected output: {"status":"ok"}
```

**Database Initialization:**
```bash
# Check logs for successful initialization
doctl apps logs $APP_ID | grep "Database Migration"

# Look for:
# ✓ PostgreSQL is ready
# ✓ Redis is ready
# ✓ Admin user created
# Starting Apache Superset
```

**Access Superset:**
```bash
# Access directly via DO URL
open $APP_URL

# Login with:
# Username: admin
# Password: [SUPERSET_ADMIN_PASSWORD]
```

### Step 6: Configure Traefik Reverse Proxy

**For path-based routing at `/superset`:**

1. **Install Traefik** on your server/droplet:
   ```bash
   # Docker installation
   docker run -d \
     --name traefik \
     -p 80:80 \
     -p 443:443 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v /path/to/deploy/superset/traefik.yml:/etc/traefik/traefik.yml \
     traefik:v2.10
   ```

2. **Update Traefik config** with actual DO App URL:
   ```yaml
   # In deploy/superset/traefik.yml
   services:
     superset-service:
       loadBalancer:
         servers:
           - url: "http://[ACTUAL_DO_APP_URL]:8088"
   ```

3. **Configure DNS**:
   - Add A record: `insightpulseai.net` → Traefik server IP
   - Or CNAME: `insightpulseai.net` → DO App Platform domain

4. **Verify path routing**:
   ```bash
   curl -f https://insightpulseai.net/superset/health
   ```

## Post-Deployment Configuration

### 1. Create Database Connections

In Superset UI:
1. Go to: **Data** → **Databases** → **+ Database**
2. Add Supabase PostgreSQL connection:
   ```
   Connection: postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```

### 2. Configure Alerts and Notifications

**Email Alerts** (optional):
```bash
# Set SMTP environment variables in DO dashboard
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-password
```

**Slack Notifications** (optional):
```bash
# Set Slack API token in DO dashboard
SLACK_API_TOKEN=xoxb-your-slack-token
```

### 3. Enable Row Level Security

```sql
-- In Superset SQL Lab
CREATE POLICY user_own_data ON your_table
  USING (user_id = current_user);
```

### 4. Setup Backups

**Automated via Supabase:**
- Supabase automatically backs up PostgreSQL database
- Retention: 7 days for free tier, 30 days for Pro

**Manual Backup:**
```bash
# Export Superset metadata
psql $DATABASE_URL -c "\\copy (SELECT * FROM dashboards) TO 'dashboards_backup.csv' CSV HEADER"
```

## Monitoring and Maintenance

### View Logs

```bash
# Real-time logs
doctl apps logs $APP_ID --follow

# Specific service logs
doctl apps logs $APP_ID --type deploy
doctl apps logs $APP_ID --type run
doctl apps logs $APP_ID --type build
```

### Performance Monitoring

```bash
# Check resource usage in DO dashboard
# Navigate to: Apps → superset-analytics → Insights

# View metrics:
# - CPU usage
# - Memory usage
# - Request throughput
# - Response times
```

### Scaling

**Vertical Scaling** (increase instance size):
```bash
# Edit infra/superset/superset-app.yaml
# Change: instance_size_slug: basic-xs → basic-s

# Update app
doctl apps update $APP_ID --spec infra/superset/superset-app.yaml
```

**Horizontal Scaling** (add instances):
```bash
# Edit infra/superset/superset-app.yaml
# Change: instance_count: 1 → 2

# Update app
doctl apps update $APP_ID --spec infra/superset/superset-app.yaml
```

### Database Maintenance

**Vacuum and analyze:**
```sql
-- Run periodically to optimize performance
VACUUM ANALYZE;
```

**Check table sizes:**
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Troubleshooting

### Common Issues

**1. Deployment Failed**
```bash
# Check build logs
doctl apps logs $APP_ID --type build

# Common causes:
# - Missing environment variables
# - Dockerfile errors
# - Build timeout

# Solution: Review logs, fix errors, redeploy
doctl apps create-deployment $APP_ID --force-rebuild
```

**2. Database Connection Failed**
```bash
# Check database connectivity
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:$POSTGRES_PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" -c "SELECT 1"

# Common causes:
# - Wrong password
# - Network issues
# - Supabase maintenance

# Solution: Verify credentials, check Supabase status
```

**3. Redis Connection Failed**
```bash
# Check Redis service
doctl apps get $APP_ID --format Services

# Solution: Restart Redis worker
doctl apps create-deployment $APP_ID
```

**4. Slow Performance**
```bash
# Check resource usage
doctl apps get $APP_ID

# Solution: Increase instance size or add workers
# Edit: infra/superset/superset-app.yaml
# Update: instance_size_slug or SUPERSET_WORKERS
```

**5. Path Routing Not Working**
```bash
# Check Traefik configuration
docker logs traefik

# Verify DNS
dig insightpulseai.net

# Test direct access
curl -I https://insightpulseai.net/superset/health
```

### Emergency Procedures

**Rollback Deployment:**
```bash
# List deployments
doctl apps list-deployments $APP_ID

# Get previous deployment ID
PREVIOUS_DEPLOYMENT_ID=...

# Rollback
doctl apps rollback-deployment $APP_ID $PREVIOUS_DEPLOYMENT_ID
```

**Database Restore:**
```bash
# Restore from Supabase backup
# 1. Go to Supabase dashboard
# 2. Navigate to: Database → Backups
# 3. Select backup point
# 4. Click "Restore"
```

## Security Checklist

- [ ] Strong `SUPERSET_SECRET_KEY` (42+ characters)
- [ ] Strong admin password (16+ characters)
- [ ] HTTPS enabled (via Traefik)
- [ ] Secrets stored in DO dashboard (not in code)
- [ ] Database SSL enabled (`sslmode=require`)
- [ ] Row Level Security policies configured
- [ ] Rate limiting enabled (via Traefik)
- [ ] Security headers configured (Content Security Policy)
- [ ] Regular backups verified
- [ ] Monitoring and alerting configured

## Cost Optimization

**Current Configuration:**
- Superset Web (basic-xs): $12/month
- Superset Worker (basic-xxs): $5/month
- Superset Beat (basic-xxs): $5/month
- Redis (basic-xxs): $5/month
- **Total: ~$27/month**

**Budget Option** (basic-xxs for all):
- Superset Web (basic-xxs): $5/month
- Superset Worker (basic-xxs): $5/month
- Superset Beat (basic-xxs): $5/month
- Redis (basic-xxs): $5/month
- **Total: ~$20/month**

**To reduce costs:**
1. Use basic-xxs instances
2. Combine worker and beat into single service
3. Use external managed Redis (DO Managed Redis has free tier)
4. Disable features not in use (alerts, caching)

## Support and Resources

**Documentation:**
- [Apache Superset Docs](https://superset.apache.org/docs/6.0.0/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database)
- [Traefik Documentation](https://doc.traefik.io/traefik/)

**Community:**
- [Superset Slack](https://join.slack.com/t/apache-superset/shared_invite/)
- [GitHub Issues](https://github.com/apache/superset/issues)

**Internal:**
- Configuration: `/config/superset/`
- Deployment Scripts: `/deploy/superset/`
- Infrastructure: `/infra/superset/`
- Docker: `/docker/superset/`

---

**Deployment Date**: 2025-10-30
**Version**: 1.0.0
**Status**: ✅ Production Ready
