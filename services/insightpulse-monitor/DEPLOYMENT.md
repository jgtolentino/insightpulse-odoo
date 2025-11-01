# Deployment Guide - InsightPulse Monitor MCP Server

Complete step-by-step guide for deploying the InsightPulse Monitor MCP Server to DigitalOcean App Platform.

## Prerequisites

- GitHub account with repository access
- DigitalOcean account
- doctl CLI installed (https://docs.digitalocean.com/reference/doctl/)
- DockerHub account
- Supabase project
- Odoo instance running

## Part 1: Initial Setup

### Step 1: Install doctl CLI

**macOS:**
```bash
brew install doctl
```

**Linux:**
```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.100.0/doctl-1.100.0-linux-amd64.tar.gz
tar xf ~/doctl-1.100.0-linux-amd64.tar.gz
sudo mv ~/doctl /usr/local/bin
```

**Verify installation:**
```bash
doctl version
```

### Step 2: Authenticate with DigitalOcean

```bash
# Generate token at: https://cloud.digitalocean.com/account/api/tokens
doctl auth init

# Verify authentication
doctl account get
```

### Step 3: Prepare Database Schema

Create required tables in Supabase:

```sql
-- Month-end tasks
CREATE TABLE month_end_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  month TEXT NOT NULL,
  agency TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked')),
  assigned_to TEXT,
  block_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Background jobs
CREATE TABLE background_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_type TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  next_retry_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Error logs
CREATE TABLE error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service TEXT NOT NULL,
  error_message TEXT NOT NULL,
  stack_trace TEXT,
  context JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Compliance tracking
CREATE TABLE compliance_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agency TEXT NOT NULL,
  compliance_type TEXT NOT NULL,
  expiry_date DATE,
  status TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agency metrics
CREATE TABLE agency_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agency TEXT NOT NULL,
  period TEXT NOT NULL,
  revenue DECIMAL,
  expenses DECIMAL,
  profit_margin DECIMAL,
  budget_variance DECIMAL,
  tasks_completed INTEGER,
  sla_adherence DECIMAL,
  avg_resolution_time DECIMAL,
  employee_count INTEGER,
  bir_filings_on_time INTEGER,
  dole_compliant BOOLEAN,
  audit_findings INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_month_end_tasks_month ON month_end_tasks(month);
CREATE INDEX idx_month_end_tasks_agency ON month_end_tasks(agency);
CREATE INDEX idx_background_jobs_status ON background_jobs(status);
CREATE INDEX idx_error_logs_service ON error_logs(service);
CREATE INDEX idx_compliance_tracking_agency ON compliance_tracking(agency);
CREATE INDEX idx_agency_metrics_agency_period ON agency_metrics(agency, period);
```

## Part 2: Create DigitalOcean App

### Step 1: Create the app

```bash
cd services/insightpulse-monitor

# Create app from spec
doctl apps create --spec app.yaml

# Note the App ID from output
export DO_MONITOR_APP_ID="<your-app-id>"
```

### Step 2: Set environment variables

```bash
# Set secrets via doctl
doctl apps update $DO_MONITOR_APP_ID --spec - <<EOF
name: insightpulse-monitor
region: sgp
services:
  - name: monitor
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    source_dir: services/insightpulse-monitor
    dockerfile_path: services/insightpulse-monitor/Dockerfile
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs

    envs:
      - key: SUPABASE_URL
        value: "$(echo $SUPABASE_URL)"
        scope: RUN_TIME
        type: SECRET

      - key: SUPABASE_SERVICE_KEY
        value: "$(echo $SUPABASE_SERVICE_KEY)"
        scope: RUN_TIME
        type: SECRET

      - key: ODOO_URL
        value: "$(echo $ODOO_URL)"
        scope: RUN_TIME
        type: SECRET

      - key: ODOO_API_KEY
        value: "$(echo $ODOO_API_KEY)"
        scope: RUN_TIME
        type: SECRET

      - key: ODOO_DATABASE
        value: "postgres"
        scope: RUN_TIME

      - key: PORT
        value: "8000"
        scope: RUN_TIME

      - key: HOST
        value: "0.0.0.0"
        scope: RUN_TIME

      - key: LOG_LEVEL
        value: "INFO"
        scope: RUN_TIME

    health_check:
      http_path: /health
      initial_delay_seconds: 15
      period_seconds: 30
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
EOF
```

### Step 3: Get app URL

```bash
# Get the app URL
APP_URL=$(doctl apps get $DO_MONITOR_APP_ID --format DefaultIngress --no-header)
echo "App URL: https://$APP_URL"
```

## Part 3: Configure GitHub

### Step 1: Set GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions**

Add these secrets:

```yaml
DO_ACCESS_TOKEN: <your-digitalocean-api-token>
DO_MONITOR_APP_ID: <your-app-id>
DOCKERHUB_USERNAME: <your-dockerhub-username>
DOCKERHUB_TOKEN: <your-dockerhub-token>
SUPABASE_URL: <your-supabase-url>
SUPABASE_SERVICE_KEY: <your-supabase-service-key>
ODOO_URL: <your-odoo-url>
ODOO_API_KEY: <your-odoo-api-key>
```

### Step 2: Enable GitHub Actions

1. Go to repository **Actions** tab
2. Enable workflows if disabled
3. Workflows should now be active

## Part 4: Deploy

### Option A: Automatic Deployment (Recommended)

Push changes to main branch:

```bash
git add services/insightpulse-monitor/
git commit -m "feat: add InsightPulse Monitor MCP server"
git push origin main
```

GitHub Actions will automatically:
1. Validate code
2. Build Docker image
3. Deploy to DigitalOcean
4. Run health checks

Monitor progress: **GitHub → Actions → InsightPulse Monitor - Deploy**

### Option B: Manual Deployment via GitHub Actions

1. Go to **Actions** tab
2. Select "InsightPulse Monitor - Deploy"
3. Click "Run workflow"
4. Select branch: `main`
5. Check "Force rebuild" if needed
6. Click "Run workflow"

### Option C: Manual Deployment via CLI

```bash
# Create deployment
doctl apps create-deployment $DO_MONITOR_APP_ID

# Or force rebuild
doctl apps create-deployment $DO_MONITOR_APP_ID --force-rebuild

# Watch deployment progress
doctl apps list-deployments $DO_MONITOR_APP_ID
```

## Part 5: Verification

### Step 1: Check deployment status

```bash
# Get app info
doctl apps get $DO_MONITOR_APP_ID

# Check deployment logs
doctl apps logs $DO_MONITOR_APP_ID --type build
doctl apps logs $DO_MONITOR_APP_ID --type run --follow
```

### Step 2: Test health endpoint

```bash
# Get app URL
APP_URL=$(doctl apps get $DO_MONITOR_APP_ID --format DefaultIngress --no-header)

# Test health
curl https://$APP_URL/health

# Expected output:
# {"status":"ok","service":"insightpulse-monitor"}
```

### Step 3: Test MCP tools

```bash
# List available tools
curl -X POST https://$APP_URL/mcp \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/list","params":{}}'

# Test system health
curl -X POST https://$APP_URL/mcp \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"get_system_health","arguments":{}}}'
```

### Step 4: Run full test suite

```bash
# Set environment
export MCP_HOST=$(echo $APP_URL | sed 's/https:\/\///')
export MCP_PORT=443

# Run tests (requires jq installed)
./test_mcp.sh
```

## Part 6: Custom Domain (Optional)

### Step 1: Add domain to app spec

Edit `app.yaml`:

```yaml
domains:
  - domain: monitor.insightpulseai.net
    type: PRIMARY
```

### Step 2: Update app

```bash
doctl apps update $DO_MONITOR_APP_ID --spec app.yaml
```

### Step 3: Configure DNS

Add CNAME record in your DNS provider:

```
Type: CNAME
Name: monitor
Value: <your-app-url>.ondigitalocean.app
TTL: 3600
```

### Step 4: Verify SSL

```bash
curl -I https://monitor.insightpulseai.net/health
```

SSL certificate is automatically provisioned by DigitalOcean.

## Part 7: Monitoring & Maintenance

### View Logs

```bash
# Real-time logs
doctl apps logs $DO_MONITOR_APP_ID --type run --follow

# Build logs
doctl apps logs $DO_MONITOR_APP_ID --type build

# Filter by time
doctl apps logs $DO_MONITOR_APP_ID --type run --since 1h
```

### Check Metrics

Go to DigitalOcean dashboard:
1. Apps → insightpulse-monitor
2. Click "Insights" tab
3. View:
   - Request count
   - Response times
   - Error rates
   - CPU/Memory usage

### Update App

```bash
# Update environment variables
doctl apps update $DO_MONITOR_APP_ID --spec app.yaml

# Scale instances
doctl apps update $DO_MONITOR_APP_ID --spec - <<EOF
services:
  - name: monitor
    instance_count: 2  # Scale to 2 instances
    instance_size_slug: basic-xs  # Upgrade to larger size
EOF
```

### Restart App

```bash
# Create new deployment (restarts)
doctl apps create-deployment $DO_MONITOR_APP_ID
```

### Delete App

```bash
# WARNING: This will delete the app and all data
doctl apps delete $DO_MONITOR_APP_ID
```

## Troubleshooting

### Deployment fails during build

**Check Dockerfile:**
```bash
# Test build locally
cd services/insightpulse-monitor
docker build -t insightpulse-monitor .
docker run -p 8000:8000 --env-file .env insightpulse-monitor
```

**Check GitHub Actions logs:**
- Go to Actions → Failed workflow
- Review "Build Docker Image" step
- Check for missing dependencies

### Health check fails

**Check environment variables:**
```bash
doctl apps spec get $DO_MONITOR_APP_ID
```

**Check logs:**
```bash
doctl apps logs $DO_MONITOR_APP_ID --type run
```

**Common issues:**
- Supabase URL format incorrect
- Service key is anon key (should be service_role)
- Odoo URL not accessible
- Database tables not created

### GitHub Actions can't deploy

**Check secrets:**
```bash
# Verify DO_ACCESS_TOKEN
doctl auth list

# Verify DO_MONITOR_APP_ID
doctl apps get $DO_MONITOR_APP_ID
```

**Check permissions:**
- Token needs Read + Write permissions
- GitHub Actions needs write access to repository

## Cost Estimation

**DigitalOcean App Platform:**
- basic-xxs: $5/month (512MB RAM, 1 vCPU)
- basic-xs: $12/month (1GB RAM, 1 vCPU)
- basic-s: $24/month (2GB RAM, 2 vCPU)

**Supabase:**
- Free tier: 500MB database, 1GB bandwidth
- Pro: $25/month (8GB database, 50GB bandwidth)

**Total estimated cost:**
- Development: $5-10/month
- Production: $30-50/month

## Scaling Recommendations

### Traffic < 1000 req/day
```yaml
instance_count: 1
instance_size_slug: basic-xxs
```

### Traffic 1000-10000 req/day
```yaml
instance_count: 2
instance_size_slug: basic-xs
```

### Traffic > 10000 req/day
```yaml
instance_count: 3
instance_size_slug: basic-s
```

## Backup & Recovery

### Backup App Spec

```bash
# Save current spec
doctl apps spec get $DO_MONITOR_APP_ID > app-backup.yaml

# Version control
git add app-backup.yaml
git commit -m "backup: app spec"
```

### Backup Database

Supabase handles automatic backups. To manually backup:

```bash
# Export all data
curl -X GET \
  "https://your-project.supabase.co/rest/v1/month_end_tasks" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
  > backup-month_end_tasks.json
```

### Recovery

```bash
# Recreate app from backup
doctl apps create --spec app-backup.yaml

# Import data to new database
# (Use Supabase SQL editor or restore from backup)
```

## Next Steps

1. **Set up monitoring alerts**
   - Configure DigitalOcean monitoring
   - Add Slack/email notifications

2. **Enable OAuth authentication**
   - Follow OAuth setup in README.md
   - Secure MCP endpoints

3. **Add custom metrics**
   - Extend monitoring tools
   - Add business-specific KPIs

4. **Configure backup automation**
   - Set up daily database backups
   - Export configuration regularly

## Support

- Documentation: See README.md
- Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
