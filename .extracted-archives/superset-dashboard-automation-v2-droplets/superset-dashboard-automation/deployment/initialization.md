# Superset Initialization Guide (DigitalOcean App Platform)

Step-by-step guide to initialize Apache Superset on DigitalOcean App Platform following DO best practices.

## Why Manual Initialization?

**DO limitation**: `doctl apps console` requires interactive TTY, which means:
- ❌ POST_DEPLOY jobs will hang
- ❌ PRE_DEPLOY jobs will hang
- ✅ Manual console initialization works reliably

This is confirmed by DO documentation and our production experience.

## Prerequisites

1. ✅ DigitalOcean account with billing enabled
2. ✅ `doctl` CLI installed and authenticated
3. ✅ Supabase project with PostgreSQL database
4. ✅ App spec YAML ready (see `digitalocean-spec.yaml`)

## Step 1: Deploy Superset App

Deploy WITHOUT any initialization jobs:

```bash
# Navigate to your project directory
cd /path/to/superset-config

# Create the app
doctl apps create --spec digitalocean-spec.yaml

# Get the app ID (save this!)
APP_ID=$(doctl apps list --format ID --no-header | head -1)
echo "App ID: $APP_ID"

# Wait for deployment to complete
doctl apps get $APP_ID --wait
```

Expected output:
```
Notice: App created
ID                                      Spec Name    Default Ingress    Active Deployment ID
73af11cb-dab2-4cb1-9770-291c536531e6    superset     superset-xxxxx     yyy...
```

## Step 2: Verify Deployment Status

Check that the service is running:

```bash
# Get full app status
doctl apps get $APP_ID

# Check component health
doctl apps get-component $APP_ID superset

# View runtime logs
doctl apps logs $APP_ID --type RUN --follow
```

Look for:
- ✅ Status: `HEALTHY`
- ✅ Phase: `ACTIVE`
- ✅ URL: `https://superset-xxxxx.ondigitalocean.app`

## Step 3: Open Interactive Console

This is where the DO-aligned approach differs from typical CI/CD:

```bash
# Open console to the running container
doctl apps console $APP_ID superset
```

You should see:
```
Opening console to component superset...
superset@superset-579674995-b6ss7:/app$
```

## Step 4: Initialize Database

Inside the console, run these commands **one by one**:

### 4.1 Check Environment
```bash
# Verify environment variables are set
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "REDIS_URL: ${REDIS_URL:0:20}..."
echo "SUPERSET_ENV: $SUPERSET_ENV"
```

### 4.2 Test Database Connection
```bash
# Test PostgreSQL connectivity
python3 << 'EOF'
from sqlalchemy import create_engine, text
import os

engine = create_engine(os.environ['DATABASE_URL'])
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version();'))
        print('✅ Database connected:', result.fetchone()[0][:50])
except Exception as e:
    print('❌ Database connection failed:', e)
EOF
```

### 4.3 Run Database Migrations
```bash
# Apply all database schema migrations
superset db upgrade

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> xxx
# INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy
# ...
```

### 4.4 Create Admin User
```bash
# Create the admin account
superset fab create-admin \
  --username admin \
  --firstname Jake \
  --lastname Tolentino \
  --email jgtolentino_rm@yahoo.com \
  --password SupersetAdmin2024!

# Expected output:
# Admin User admin created.
```

**Security Note**: Change the password after first login!

### 4.5 Initialize Superset
```bash
# Initialize roles and permissions
superset init

# Expected output:
# Syncing role definition
# Syncing Admin perms
# Syncing Alpha perms
# Syncing Gamma perms
```

### 4.6 Verify Initialization
```bash
# List users
superset fab list-users

# Count dashboards (should be 0 if SUPERSET_LOAD_EXAMPLES=False)
python3 << 'EOF'
from superset import app, db
from superset.models.dashboard import Dashboard

with app.app_context():
    count = db.session.query(Dashboard).count()
    print(f'Dashboards: {count}')
EOF
```

### 4.7 Exit Console
```bash
exit
```

## Step 5: Access Superset UI

Open your browser:

```bash
# Get the app URL
doctl apps get $APP_ID --format DefaultIngress --no-header
```

Visit the URL (e.g., `https://superset-xxxxx.ondigitalocean.app`)

Login with:
- **Username**: `admin`
- **Email**: `jgtolentino_rm@yahoo.com`
- **Password**: `SupersetAdmin2024!`

## Step 6: Add Custom Domain (Optional)

### 6.1 Update DNS
Add a CNAME record in your domain registrar:

```
Type: CNAME
Name: superset
Value: superset-xxxxx.ondigitalocean.app
TTL: 3600
```

### 6.2 Update App Spec
Edit `digitalocean-spec.yaml`:

```yaml
domains:
  - domain: superset.insightpulseai.net
    type: PRIMARY
  - domain: superset-xxxxx.ondigitalocean.app
    type: ALIAS

# Also update ALLOWED_HOSTS
envs:
  - key: ALLOWED_HOSTS
    value: "superset.insightpulseai.net"  # Change from "*"
    scope: RUN_TIME
```

Apply changes:
```bash
doctl apps update $APP_ID --spec digitalocean-spec.yaml
```

## Step 7: Configure Database Connection

### 7.1 Add Supabase Connection

Via UI:
1. Go to **Settings** > **Database Connections**
2. Click **+ Database**
3. Fill in:
   - **Database name**: `Supabase Production`
   - **SQLAlchemy URI**: `postgresql://postgres:PASSWORD@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres`
   - **Expose in SQL Lab**: ✅ Yes
   - **Allow DML**: ❌ No (for safety)
4. Click **Test Connection**
5. Click **Connect**

### 7.2 Add Odoo Connection (Optional)

If you have Odoo ERP:

```
Database name: Odoo ERP
SQLAlchemy URI: postgresql://odoo:password@odoo-host:5432/odoo
Expose in SQL Lab: Yes
Allow DML: No
```

## Troubleshooting

### Issue: "Database connection failed"

**Check DATABASE_URL format:**
```bash
# In console
echo $DATABASE_URL | head -c 50

# Should start with: postgresql://
```

**Test connection manually:**
```bash
apt-get update && apt-get install -y postgresql-client
psql "$DATABASE_URL" -c "SELECT current_database();"
```

### Issue: "Admin user already exists"

**Reset password:**
```bash
doctl apps console $APP_ID superset
superset fab reset-password --username admin
```

### Issue: "Health check failing"

**Check logs:**
```bash
doctl apps logs $APP_ID --type RUN --tail 100

# Look for errors like:
# - "Out of memory"
# - "Database connection refused"
# - "Redis connection failed"
```

**Solution**: Increase instance size or check environment variables.

### Issue: "502 Bad Gateway"

**Possible causes:**
1. App still initializing (wait 2-3 minutes)
2. Health check timeout too short
3. Out of memory (upgrade instance)

**Check component status:**
```bash
doctl apps get-component $APP_ID superset
```

### Issue: "Data lost after redeploy"

**Check volume configuration:**
```bash
doctl apps spec get $APP_ID --format yaml | grep -A 5 volumes
```

Should show:
```yaml
volumes:
  - name: superset-data
    mount_path: /app/superset_home
```

## Post-Initialization Checklist

- [ ] Can login to Superset UI
- [ ] Database connection tested
- [ ] No example data loaded
- [ ] Admin user password changed
- [ ] Custom domain configured (optional)
- [ ] ALLOWED_HOSTS updated
- [ ] Volume persistence verified
- [ ] Health checks passing
- [ ] Logs show no errors

## Common Initialization Mistakes

### ❌ Mistake 1: Using POST_DEPLOY Job
```yaml
jobs:
  - name: superset-init
    kind: POST_DEPLOY  # ❌ This will hang!
```

**Why it fails**: `doctl apps console` needs interactive TTY.

### ❌ Mistake 2: Missing Volume
```yaml
services:
  - name: superset
    # ... no volumes section
```

**Result**: Data lost on every redeploy.

### ❌ Mistake 3: Instance Too Small
```yaml
instance_size_slug: basic-xxs  # ❌ 512MB not enough
```

**Result**: Out of memory errors.

### ❌ Mistake 4: Using 'latest' Tag
```yaml
tag: latest  # ❌ Unpredictable behavior
```

**Result**: Breaking changes on redeploy.

## Monitoring and Maintenance

### Daily Health Check
```bash
# Check app status
doctl apps get $APP_ID --format ActiveDeployment.Phase

# Should output: ACTIVE
```

### View Logs
```bash
# Runtime logs
doctl apps logs $APP_ID --type RUN --follow

# Deployment logs
doctl apps logs $APP_ID --type DEPLOY
```

### Update Superset Version
```bash
# Edit spec to update tag
sed -i 's/tag: "3.1.0"/tag: "3.1.1"/' digitalocean-spec.yaml

# Apply update
doctl apps update $APP_ID --spec digitalocean-spec.yaml

# Volume ensures data persists!
```

## Next Steps

1. ✅ Configure row-level security in Supabase
2. ✅ Create datasets for BIR compliance
3. ✅ Build Finance SSC dashboards
4. ✅ Set up automated refresh schedules
5. ✅ Enable alerting for critical metrics

See `SKILL.md` for dashboard creation workflows!

## Support Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Apache Superset Docs](https://superset.apache.org/docs/intro)
- [Supabase Integration](../reference/supabase-integration.md)
- [Dashboard Templates](../reference/dashboard-templates.md)

---

**Your production-ready Superset deployment is complete!** 🎉

Login at: `https://superset.insightpulseai.net`
