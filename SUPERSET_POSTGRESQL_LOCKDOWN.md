# Superset PostgreSQL Lock-In Complete ✅

**Date**: 2025-11-04
**Status**: Production Ready
**Database**: PostgreSQL (Supabase) - **SQLite eliminated**

---

## What Was Accomplished

### 1. Database Infrastructure ✅

#### Schemas Created
- **`superset`**: Superset metadata (dashboards, users, permissions, charts)
- **`mcp`**: MCP tools, events, forum posts
- **`llm`**: LLM gateway, rate limits, usage logs
- **`ocr`**: OCR job logs (optional)

#### Connection String
```
postgresql+psycopg2://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&application_name=superset&options=-csearch_path%3Dsuperset
```

**Key Features**:
- ✅ Connection pooler (port 6543) for high concurrency
- ✅ SSL required for security
- ✅ `search_path=superset` forces metadata into correct schema
- ✅ Application name for monitoring and diagnostics

### 2. Superset Configuration ✅

**App Spec**: `infra/superset/superset-simple.yaml`

**Environment Variables**:
- `SQLALCHEMY_DATABASE_URI`: PostgreSQL connection with schema path
- `SUPERSET_SECRET_KEY`: Secure session encryption
- `SUPERSET_ADMIN_PASSWORD`: Admin account password
- `SUPERSET_LOAD_EXAMPLES`: Set to "no" (prevent sample data bloat)

**Run Command** (Automatic Migration):
```bash
superset db upgrade && \
superset fab create-admin --username admin --password ${SUPERSET_ADMIN_PASSWORD} --firstname Admin --lastname User --email admin@insightpulseai.net || true && \
superset init && \
gunicorn -b 0.0.0.0:8088 -w 4 --timeout 120 superset.app:create_app()
```

**Benefits**:
- ✅ Database migrations run automatically on every deployment
- ✅ Admin account created if not exists (idempotent)
- ✅ Superset initialization runs (registers default roles, permissions)
- ✅ Gunicorn serves with 4 workers, 120s timeout

### 3. CI/CD Guardrails ✅

#### Health Check Workflow
**File**: `.github/workflows/superset-health.yml`

**Schedule**: Daily at 2 AM UTC + manual dispatch

**Checks**:
1. **Anti-SQLite Guard**: Verifies `SQLALCHEMY_DATABASE_URI` contains `postgresql`
2. **Connection Pooler Check**: Warns if not using Supabase pooler
3. **Schema Path Check**: Warns if `search_path` not set to `superset`
4. **Health Endpoint**: Verifies `/health` returns OK
5. **Database Connection**: Tests connection to Supabase
6. **Schema Existence**: Verifies `superset` schema exists
7. **Metadata Tables**: Checks for key Superset tables

**Failure Handling**: Notifications on failure (can be extended to Slack/email)

#### Deployment Workflow
**File**: `.github/workflows/superset-deploy.yml`

**Trigger**: Push to `main` branch with changes to `infra/superset/`

**Steps**:
1. Update app spec on DigitalOcean
2. Create deployment with force rebuild
3. Wait for deployment (max 10 minutes)
4. Run database migration (via run_command)
5. Verify health endpoint
6. Verify PostgreSQL backend (check logs for SQLite references)
7. Deployment summary with URLs

### 4. MCP Forum Scraper ✅

#### Purpose
Scrape Odoo community forum posts for MCP knowledge base

#### Database Schema
**File**: `infra/sql/mcp_forum_posts.sql`

**Table**: `mcp.forum_posts`

**Columns**:
- `id` (text, PK): Forum post ID
- `topic` (text): Forum topic/category
- `title` (text): Post title
- `content` (text): Post body
- `author` (text): Post author
- `created_at` (timestamptz): Creation timestamp
- `updated_at` (timestamptz): Last update
- `views` (int): View count
- `replies` (int): Reply count
- `tags` (text[]): Post tags
- `url` (text): Direct URL
- `metadata` (jsonb): Additional metadata
- `scraped_at` (timestamptz): Scrape timestamp

**Indexes**:
- Topic, created_at, tags (GIN), author, scraped_at
- Full-text search on title + content

#### Scraper Script
**File**: `jobs/forum_scrape.py`

**Schedule**: Every 10 minutes via cron
```cron
*/10 * * * * /usr/local/bin/python3 /opt/stack/jobs/forum_scrape.py >> /var/log/forum_scrape.log 2>&1
```

**Topics Scraped**:
- help-1 (General Help)
- odoo-19 (Odoo 19.0)
- odoo-18 (Odoo 18.0)
- accounting-3 (Accounting)
- development-4 (Development)

**Features**:
- Upsert to prevent duplicates
- Normalized data schema
- Comprehensive logging
- Error handling and retry logic

#### Setup Documentation
**File**: `jobs/README.md`

**Includes**:
- Database setup instructions
- Environment variable configuration
- Cron setup (traditional and systemd timer)
- Manual testing steps
- Query examples
- Troubleshooting guide

---

## Verification Commands

### 1. Check Superset Health
```bash
curl -sf https://superset.insightpulseai.net/health
```

Expected: `{"status":"ok"}` or similar

### 2. Verify PostgreSQL Backend
```bash
doctl apps logs 73af11cb-dab2-4cb1-9770-291c536531e6 --type run --tail 100 | grep -E "(postgresql|sqlite)"
```

Expected: PostgreSQL connections, **NO** SQLite references

### 3. Check Database Schema
```bash
psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" \
  -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('superset', 'mcp', 'llm', 'ocr');"
```

Expected: All 4 schemas listed

### 4. Verify Superset Tables
```bash
psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" \
  -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'superset' ORDER BY tablename LIMIT 10;"
```

Expected: Superset metadata tables (dashboards, slices, ab_user, etc.)

### 5. Test Forum Posts Table
```bash
psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" \
  -c "SELECT COUNT(*) FROM mcp.forum_posts;"
```

Expected: 0 (initially, will populate after scraper runs)

---

## Access Points

### Superset Web UI
**URL**: https://superset.insightpulseai.net

**Credentials**:
- Username: `admin`
- Password: `SHWYXDMFAwXI1drT`

### DigitalOcean App Platform
**App ID**: `73af11cb-dab2-4cb1-9770-291c536531e6`

**Quick Commands**:
```bash
# View logs
doctl apps logs 73af11cb-dab2-4cb1-9770-291c536531e6 --type run --tail 100

# List deployments
doctl apps list-deployments 73af11cb-dab2-4cb1-9770-291c536531e6

# Create new deployment
doctl apps create-deployment 73af11cb-dab2-4cb1-9770-291c536531e6 --force-rebuild
```

### Supabase Database
**Project**: spdtwktxdalcfigzeqrz
**Region**: AWS us-east-1
**Pooler**: aws-1-us-east-1.pooler.supabase.com:6543

---

## Maintenance

### Manual Migration Run
If needed (normally automatic via run_command):
```bash
doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset
# Then inside container:
superset db upgrade
superset init
```

### Clear SQLite Artifacts (Precautionary)
```bash
# Inside Superset container (if you ever need to manually remove SQLite files)
rm -f $SUPERSET_HOME/superset.db
```

**Note**: With PostgreSQL configured, SQLite should never be created.

### Backup Superset Metadata
```bash
# Export Superset schema
pg_dump --no-owner --schema=superset "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" | gzip > superset_backup_$(date +%F).sql.gz
```

### Restore from Backup
```bash
# Decompress and restore
gunzip < superset_backup_2025-11-04.sql.gz | psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

---

## Performance Optimization (Optional)

### Add Redis for Caching
**Environment Variables** (add to app spec):
```yaml
- key: RATELIMIT_STORAGE_URI
  value: redis://:<REDIS_PASSWORD>@<REDIS_HOST>:6379/0
  scope: RUN_TIME
  type: SECRET

- key: CACHE_CONFIG
  value: '{"CACHE_TYPE":"RedisCache","CACHE_DEFAULT_TIMEOUT":300,"CACHE_KEY_PREFIX":"superset","CACHE_REDIS_URL":"redis://:<REDIS_PASSWORD>@<REDIS_HOST>:6379/1"}'
  scope: RUN_TIME
  type: SECRET
```

**Benefits**:
- Faster dashboard loading
- Reduced database queries
- Better rate limiting

---

## Troubleshooting

### Issue: Health check failing
**Check**:
```bash
curl -v https://superset.insightpulseai.net/health
doctl apps logs 73af11cb-dab2-4cb1-9770-291c536531e6 --type run --tail 50
```

**Solutions**:
- Verify deployment is ACTIVE
- Check for errors in logs
- Verify database connection

### Issue: Can't log in
**Check**:
- Verify admin account created: Check logs for "create-admin" output
- Try password reset via Superset UI
- Recreate admin account:
  ```bash
  doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset
  superset fab create-admin --username admin --password <NEW_PASSWORD> --firstname Admin --lastname User --email admin@insightpulseai.net
  ```

### Issue: Dashboard not loading
**Check**:
- Check browser console for errors
- Verify database connection
- Check for CORS issues (if accessing from different domain)
- Check Superset logs for Python exceptions

### Issue: Database connection errors
**Check**:
```bash
# Test connection from outside
psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" -c "SELECT version();"

# Check Superset environment
doctl apps logs 73af11cb-dab2-4cb1-9770-291c536531e6 --type run | grep -i "database\|connection"
```

**Solutions**:
- Verify SQLALCHEMY_DATABASE_URI is correct
- Check Supabase project status
- Verify network connectivity

---

## Next Steps

### 1. Load Sample Dashboards (Optional)
```bash
doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset
superset load_examples
superset init
```

### 2. Connect Odoo Data Source
In Superset UI:
1. Navigate to **Data → Databases → +**
2. Database Name: `Odoo ERP`
3. SQLAlchemy URI: `postgresql://odoo_read:<PASSWORD>@<ODOO_DB_HOST>:5432/odoo?sslmode=require`
4. Test Connection
5. Save

### 3. Create First Dashboard
1. Create dataset from Odoo table
2. Create chart from dataset
3. Add chart to dashboard
4. Share dashboard URL

### 4. Setup Forum Scraper
Follow instructions in `jobs/README.md`:
1. Apply schema: `psql "$POSTGRES_URL" -f infra/sql/mcp_forum_posts.sql`
2. Setup cron or systemd timer
3. Test manually: `python3 jobs/forum_scrape.py`
4. Monitor logs: `tail -f /var/log/forum_scrape.log`

---

## Summary

✅ **PostgreSQL**: Superset metadata on Supabase
✅ **Schemas**: Segregated (superset, mcp, llm, ocr)
✅ **CI/CD**: Health checks and deployment automation
✅ **SQLite**: Completely eliminated with guardrails
✅ **Forum Scraper**: Ready to deploy for MCP knowledge base
✅ **Production Ready**: Health endpoint responding, migrations automatic

**No more SQLite. Ever.** 🎉
