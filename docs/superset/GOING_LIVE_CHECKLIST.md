# Making https://insightpulseai.net/superset Live

**Goal**: Deploy Apache Superset and make it accessible at https://insightpulseai.net/superset

**Current Status**: Infrastructure ready, needs deployment + reverse proxy configuration

**Estimated Time**: 30-45 minutes

---

## Architecture Overview

```
Client → Caddy (insightpulseai.net) → DigitalOcean App Platform
         ├── /odoo/* → Odoo (127.0.0.1:8069)
         └── /superset/* → Superset (DO App Platform URL)
                           ├── Superset Web (Gunicorn)
                           ├── Superset Worker (Celery)
                           ├── Superset Beat (Scheduler)
                           └── Redis (Cache)
                                     ↓
                           Supabase PostgreSQL (Metadata DB)
```

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] DigitalOcean account with API access
- [ ] `doctl` CLI installed and authenticated
- [ ] SSH access to server running Caddy at insightpulseai.net
- [ ] Supabase PostgreSQL credentials (already configured in spec)
- [ ] Domain DNS pointing to Caddy server

---

## Step 1: Deploy Superset to DigitalOcean App Platform

### 1.1 Verify Prerequisites

```bash
# Check doctl is installed
doctl version

# Check authentication
doctl auth list

# Check you can access apps
doctl apps list
```

If `doctl` is not installed:
```bash
# macOS
brew install doctl

# Linux
cd /tmp
wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
tar xf doctl-*.tar.gz
sudo mv doctl /usr/local/bin
```

### 1.2 Authenticate to DigitalOcean

```bash
# Initialize authentication (will open browser)
doctl auth init

# Verify
doctl auth list
```

### 1.3 Deploy Superset

**Option A: Automated Deployment (Recommended)**

```bash
cd /path/to/insightpulse-odoo

# Run deployment script
./deploy/superset/deploy.sh
```

The script will:
- ✅ Verify prerequisites
- ✅ Create or update Superset app
- ✅ Deploy all services (web, worker, beat, redis)
- ✅ Monitor deployment logs
- ✅ Display app URL

**Option B: Manual Deployment**

```bash
cd /path/to/insightpulse-odoo

# Create app from spec
doctl apps create --spec infra/superset/superset-app.yaml

# Wait ~5 seconds for app to be created
sleep 5

# Get app ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "superset-analytics" | awk '{print $1}')

# Monitor deployment
doctl apps logs $APP_ID --follow
```

### 1.4 Wait for Deployment

Deployment takes **5-15 minutes**. Watch for these log messages:

```
✓ PostgreSQL is ready
✓ Redis is ready
✓ Running database migrations
✓ Creating admin user
✓ Starting Apache Superset
```

### 1.5 Get App URL

```bash
# Get the live URL
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "superset-analytics" | awk '{print $1}')
APP_URL=$(doctl apps get $APP_ID --format LiveURL --no-header)

echo "Superset URL: $APP_URL"
# Example: https://superset-analytics-abcde.ondigitalocean.app
```

### 1.6 Verify Deployment

```bash
# Test health endpoint
curl -f $APP_URL/health

# Expected output:
# {"status":"ok"}

# Test login page
curl -I $APP_URL/login/

# Expected: HTTP/1.1 200 OK
```

✅ **Checkpoint**: Superset is now running on DigitalOcean App Platform

---

## Step 2: Update Caddy Configuration for /superset Path

### 2.1 SSH to Caddy Server

```bash
ssh user@insightpulseai.net
```

### 2.2 Backup Current Caddyfile

```bash
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup.$(date +%Y%m%d)
```

### 2.3 Edit Caddyfile

```bash
sudo nano /etc/caddy/Caddyfile
```

**Add the following Superset configuration:**

```caddyfile
insightpulseai.net {
  encode zstd gzip

  # Superset paths - MUST BE FIRST to take precedence
  @superset path /superset* /static/appbuilder* /static/assets*
  handle @superset {
    # Replace with your actual DO App Platform URL
    reverse_proxy https://superset-analytics-xxxxx.ondigitalocean.app {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-Host {host}
      header_up X-Forwarded-Proto {scheme}
      header_up X-Real-IP {remote_host}
    }
  }

  # Odoo paths
  @odoo path /odoo* /web* /longpolling* /calendar* /website* /shop*
  handle @odoo {
    reverse_proxy 127.0.0.1:8069
  }

  # Block database manager
  @dbm path /web/database/* /database/*
  respond @dbm 403

  # Default
  handle {
    respond "OK" 200
  }

  # Security headers
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "SAMEORIGIN"
    Referrer-Policy "strict-origin-when-cross-origin"
  }
}
```

**Replace `superset-analytics-xxxxx.ondigitalocean.app` with your actual DO App URL!**

### 2.4 Validate Caddyfile

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
```

Expected output: `Valid configuration`

### 2.5 Reload Caddy

```bash
sudo systemctl reload caddy

# Check status
sudo systemctl status caddy
```

✅ **Checkpoint**: Caddy is now routing /superset to Superset

---

## Step 3: Update Superset Configuration for Reverse Proxy

### 3.1 Update Environment Variables in DO Dashboard

1. Go to: https://cloud.digitalocean.com/apps

2. Click on **superset-analytics** app

3. Go to **Settings** → **Environment Variables**

4. Update the following variables for the **superset-web** service:

| Variable | Current Value | New Value |
|----------|---------------|-----------|
| `SUPERSET_APP_ROOT` | `/superset` | `/superset` ✅ (already correct) |
| `SUPERSET_WEBSERVER_PROTOCOL` | `https` | `https` ✅ (already correct) |

**These should already be correct in the spec!** Just verify them.

5. Add new variable (if not present):

| Variable | Value | Type |
|----------|-------|------|
| `ENABLE_PROXY_FIX` | `true` | Plain Text |

6. Click **Save** (app will auto-redeploy)

### 3.2 Wait for Redeployment

```bash
# Monitor logs
doctl apps logs $APP_ID --follow
```

Wait for: `Starting Apache Superset`

---

## Step 4: Test the Deployment

### 4.1 Test Health Endpoint

```bash
curl -f https://insightpulseai.net/superset/health

# Expected: {"status":"ok"}
```

### 4.2 Test Login Page

```bash
curl -I https://insightpulseai.net/superset/login/

# Expected: HTTP/2 200
```

### 4.3 Access in Browser

Open: **https://insightpulseai.net/superset**

**Login Credentials:**
- Username: `admin`
- Password: `Postgres_26` (or your configured password)

### 4.4 Verify Assets Load

Check browser console (F12) - should see no 404 errors for static assets.

If assets fail to load, check:
1. Caddy is routing `/static/*` paths correctly
2. `SUPERSET_APP_ROOT` is set to `/superset` in DO dashboard
3. Clear browser cache and try again

---

## Step 5: Post-Deployment Configuration

### 5.1 Create Database Connection

1. In Superset, go to: **Data** → **Databases** → **+ Database**

2. Select: **PostgreSQL**

3. Add connection string:
   ```
   postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```

4. Click **Test Connection** → Should show **Success**

5. Click **Add**

### 5.2 Create First Dashboard

1. Go to: **SQL Lab** → **SQL Editor**

2. Select your database

3. Run a test query:
   ```sql
   SELECT
     generate_series(1, 10) AS id,
     'Sample Data' AS name,
     random() * 100 AS value;
   ```

4. Click **Explore** → **Create Chart**

5. Configure chart and **Save**

6. Go to: **Dashboards** → **+ Dashboard**

7. Add your chart to the dashboard

---

## Step 6: Security Hardening

### 6.1 Change Default Admin Password

1. In Superset, go to: **Settings** → **User Info & Security**

2. Click **Info** → **Change Password**

3. Set a strong password (16+ characters)

### 6.2 Create Additional Users

1. Go to: **Settings** → **List Users** → **+**

2. Create user with appropriate role:
   - **Admin**: Full access
   - **Alpha**: Can create dashboards
   - **Gamma**: View-only access

### 6.3 Enable Row Level Security (Optional)

```sql
-- In Superset SQL Lab, run:
CREATE POLICY user_own_data ON your_table
  FOR SELECT
  USING (user_id = current_setting('request.user_id')::int);
```

### 6.4 Configure HTTPS Enforcement

Already done via Caddy configuration! ✅

---

## Troubleshooting Guide

### Issue 1: "502 Bad Gateway" when accessing /superset

**Cause**: Caddy can't reach DO App Platform URL

**Solution**:
1. Verify DO app is running:
   ```bash
   doctl apps get $APP_ID --format Status
   ```
2. Verify DO app URL is correct in Caddyfile
3. Test direct access:
   ```bash
   curl -I https://superset-analytics-xxxxx.ondigitalocean.app/health
   ```

### Issue 2: Assets (CSS/JS) not loading (404 errors)

**Cause**: `SUPERSET_APP_ROOT` not set correctly

**Solution**:
1. Verify `SUPERSET_APP_ROOT=/superset` in DO dashboard
2. Redeploy app:
   ```bash
   doctl apps create-deployment $APP_ID --force-rebuild
   ```
3. Clear browser cache

### Issue 3: "Cannot connect to database"

**Cause**: Supabase connection string incorrect

**Solution**:
1. Verify password is correct: `Postgres_26`
2. Test connection directly:
   ```bash
   psql "postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" -c "SELECT 1"
   ```
3. Check Supabase project is running at https://supabase.com/dashboard

### Issue 4: Slow performance

**Cause**: Instance size too small

**Solution**:
1. Edit `infra/superset/superset-app.yaml`
2. Change: `instance_size_slug: basic-xs` → `basic-s`
3. Redeploy:
   ```bash
   doctl apps update $APP_ID --spec infra/superset/superset-app.yaml
   ```

### Issue 5: Redirect loops

**Cause**: Proxy headers not configured correctly

**Solution**:
1. Verify Caddyfile has these headers:
   ```
   header_up X-Forwarded-Host {host}
   header_up X-Forwarded-Proto {scheme}
   ```
2. Verify `ENABLE_PROXY_FIX=true` in DO dashboard
3. Reload Caddy: `sudo systemctl reload caddy`

---

## Monitoring and Maintenance

### View Logs

```bash
# Real-time logs
doctl apps logs $APP_ID --follow

# Specific service
doctl apps logs $APP_ID --type run

# Last 100 lines
doctl apps logs $APP_ID --tail 100
```

### Check Resource Usage

```bash
# In DO dashboard
# Navigate to: Apps → superset-analytics → Insights

# View:
# - CPU usage
# - Memory usage
# - Request throughput
# - Response times
```

### Backup Dashboards

```bash
# Export dashboards via API
curl -X GET https://insightpulseai.net/superset/api/v1/dashboard/export/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -o dashboards_backup.zip
```

### Scale Resources

**Vertical scaling** (increase instance size):
```bash
# Edit infra/superset/superset-app.yaml
# Change: instance_size_slug: basic-xs → basic-s

doctl apps update $APP_ID --spec infra/superset/superset-app.yaml
```

**Horizontal scaling** (add instances):
```bash
# Edit infra/superset/superset-app.yaml
# Change: instance_count: 1 → 2

doctl apps update $APP_ID --spec infra/superset/superset-app.yaml
```

---

## Cost Breakdown

**Current Configuration:**
- Superset Web (basic-xs): **$12/month**
- Superset Worker (basic-xxs): **$5/month**
- Superset Beat (basic-xxs): **$5/month**
- Redis (basic-xxs): **$5/month**

**Total: $27/month**

**Budget Option** (basic-xxs for all): **$20/month**

---

## Quick Reference

| Resource | URL |
|----------|-----|
| **Superset UI** | https://insightpulseai.net/superset |
| **Health Check** | https://insightpulseai.net/superset/health |
| **DO App Dashboard** | https://cloud.digitalocean.com/apps |
| **Supabase Dashboard** | https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz |
| **Deployment Script** | `./deploy/superset/deploy.sh` |
| **Caddyfile Location** | `/etc/caddy/Caddyfile` |

| Credential | Value |
|------------|-------|
| **Admin Username** | `admin` |
| **Admin Password** | `Postgres_26` (change after first login!) |
| **Database Password** | `Postgres_26` |
| **Secret Key** | `8UToEhL2C0ovd7S4maFPsi7e4mU05pqAH907G5yUaLsr9prnJdHu7+6k` |

---

## Success Checklist

- [ ] DigitalOcean App Platform deployed successfully
- [ ] Health endpoint returns `{"status":"ok"}`
- [ ] Caddy routes `/superset` correctly
- [ ] https://insightpulseai.net/superset loads in browser
- [ ] Can login with admin credentials
- [ ] Static assets (CSS/JS) load without 404 errors
- [ ] Database connection created and tested
- [ ] First dashboard created
- [ ] Admin password changed from default
- [ ] Backups configured

---

**Deployment Date**: 2025-10-31
**Version**: 1.0.0
**Status**: Ready for deployment
**Support**: See `docs/superset/DEPLOYMENT_GUIDE.md` for detailed instructions
