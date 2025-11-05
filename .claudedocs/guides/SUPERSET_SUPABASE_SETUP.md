# Superset + Supabase Connection Setup

## Problem
Current Superset configuration cannot connect to Supabase database. Error: "Tenant or user not found"

## Root Cause
Wrong connection parameters or database password expired/changed.

## Solution

### Step 1: Get Correct Database Credentials

1. **Go to Supabase Dashboard:**
   ```
   https://supabase.com/dashboard/project/xkxyvboeubffxxbebsll/settings/database
   ```

2. **Locate Connection Info Section:**
   - Find "Database password" (the one you set during project creation)
   - Note: This is NOT the same as API keys

3. **Find Connection Details:**
   - **Host:** `db.xkxyvboeubffxxbebsll.supabase.co` (direct)
   - **Port:** `5432` (direct) or `6543` (pooler)
   - **Database:** `postgres`
   - **Username:** `postgres`
   - **Password:** [Your database password]

### Step 2: Test Connection Locally

```bash
# Set your actual password
export DB_PASSWORD="your_actual_password_here"

# Test direct connection
psql "postgresql://postgres:${DB_PASSWORD}@db.xkxyvboeubffxxbebsll.supabase.co:5432/postgres" -c "SELECT version();"
```

### Step 3: Update Superset App Configuration

Edit your Superset app spec (`infra/superset/superset-minimal.yaml`):

```yaml
envs:
  - key: DATABASE_DIALECT
    value: postgresql
    scope: RUN_TIME

  - key: DATABASE_HOST
    value: db.xkxyvboeubffxxbebsll.supabase.co  # Changed from pooler
    scope: RUN_TIME

  - key: DATABASE_PORT
    value: "5432"  # Changed from 6543
    scope: RUN_TIME

  - key: DATABASE_DB
    value: postgres
    scope: RUN_TIME

  - key: DATABASE_USER
    value: postgres  # NOT postgres.xkxyvboeubffxxbebsll
    scope: RUN_TIME

  - key: DATABASE_PASSWORD
    value: YOUR_ACTUAL_PASSWORD  # From Supabase dashboard
    scope: RUN_TIME
    type: SECRET
```

### Step 4: Deploy Updated Configuration

```bash
# Update Superset app
doctl apps update 73af11cb-dab2-4cb1-9770-291c536531e6 --spec infra/superset/superset-minimal.yaml

# Create new deployment
doctl apps create-deployment 73af11cb-dab2-4cb1-9770-291c536531e6
```

### Step 5: Verify Connection

After deployment:

```bash
# Check Superset logs
doctl apps logs 73af11cb-dab2-4cb1-9770-291c536531e6 --follow

# Login to Superset
# URL: https://superset-6ktpx.ondigitalocean.app
# Username: admin
# Password: SHWYXDMFAwXI1drT
```

## Alternative: Use Connection Pooler (If Direct Fails)

If direct connection doesn't work, try the pooler with session mode:

```yaml
DATABASE_HOST: aws-0-us-east-1.pooler.supabase.com
DATABASE_PORT: "6543"
DATABASE_USER: postgres.xkxyvboeubffxxbebsll  # Note the project ref
```

Add to connection string:
```
?pgbouncer=true&connection_limit=10
```

## Troubleshooting

### Error: "Tenant or user not found"

**Causes:**
1. Wrong database password
2. Wrong username format (should be just `postgres` for direct, `postgres.PROJECT_REF` for pooler)
3. Database paused/inactive
4. IP not allowlisted

**Solution:**
1. Reset database password in Supabase dashboard
2. Check connection pooler vs direct connection requirements
3. Verify project is active (not paused)
4. Add `0.0.0.0/0` to IP allowlist (or specific IPs)

### Error: Connection timeout

**Causes:**
1. Wrong host/port
2. Firewall blocking connection
3. Network issue

**Solution:**
1. Use `db.PROJECT_REF.supabase.co:5432` for direct
2. Use `aws-0-us-east-1.pooler.supabase.com:6543` for pooler
3. Check if Supabase is having service issues

### Superset Shows "Database Error"

**Causes:**
1. SQLAlchemy connection string incorrect
2. Missing psycopg2 driver
3. Permissions issue

**Solution:**
```
# Superset connection format:
postgresql://postgres:PASSWORD@db.xkxyvboeubffxxbebsll.supabase.co:5432/postgres
```

## Quick Reference

### Connection String Formats

**Direct (Recommended for Superset):**
```
postgresql://postgres:PASSWORD@db.xkxyvboeubffxxbebsll.supabase.co:5432/postgres
```

**Pooler (Session Mode):**
```
postgresql://postgres.xkxyvboeubffxxbebsll:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

**Pooler (Transaction Mode - Not recommended for Superset):**
```
postgresql://postgres.xkxyvboeubffxxbebsll:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Environment Variables

Add to `~/.zshrc`:
```bash
export SUPABASE_PROJECT_REF="xkxyvboeubffxxbebsll"
export SUPABASE_DB_HOST="db.xkxyvboeubffxxbebsll.supabase.co"
export SUPABASE_DB_PORT="5432"
export SUPABASE_DB_PASSWORD="your_actual_password"
```

## Support

**Supabase Dashboard:**
https://supabase.com/dashboard/project/xkxyvboeubffxxbebsll

**Superset App:**
https://cloud.digitalocean.com/apps/73af11cb-dab2-4cb1-9770-291c536531e6

**Documentation:**
- Supabase Database Settings: https://supabase.com/docs/guides/database/connecting-to-postgres
- Superset Database Drivers: https://superset.apache.org/docs/databases/installing-database-drivers
