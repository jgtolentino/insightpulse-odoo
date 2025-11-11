# Superset ↔ Supabase Integration

## Overview

Apache Superset configured to use **Supabase PostgreSQL** as the metadata store instead of SQLite.

### Benefits
✅ **Production-ready** - PostgreSQL metadata store instead of SQLite
✅ **Scalable** - Connection pooler handles high concurrency
✅ **Persistent** - Data survives container restarts
✅ **Backed up** - Supabase automatic backups
✅ **Secure** - Credentials via environment variables

## Configuration Summary

### Supabase Database
```
Project:  spdtwktxdalcfigzeqrz
Host:     aws-1-us-east-1.pooler.supabase.com
Port:     6543 (connection pooler)
Database: postgres
User:     postgres.spdtwktxdalcfigzeqrz
```

### Files Modified
1. **docker-compose.yaml** - Added Supabase environment variables
2. **superset_config.py** - Already configured for PostgreSQL
3. **.env** - Secrets file (do not commit!)
4. **.gitignore** - Protect secrets from git

### New Files
- `DEPLOYMENT.md` - Complete deployment guide
- `superset-app.yaml` - DigitalOcean App Platform spec
- `SUPABASE_INTEGRATION.md` - This file

## Quick Start

### 1. Get Supabase Password
Visit: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/database

Look for: **Database Password** (postgres user)

### 2. Configure Local Environment
```bash
cd superset

# Edit .env file
nano .env

# Set your Supabase password:
SUPABASE_DB_PASSWORD=your-actual-password-here
SUPERSET_SECRET_KEY=$(openssl rand -base64 42)
```

### 3. Start Superset
```bash
# Pull latest image
docker-compose pull

# Start with Supabase connection
docker-compose up -d

# Initialize database (first time only)
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init

# Create admin user (first time only)
docker-compose exec superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulseai.net \
  --password changeme123
```

### 4. Access Superset
http://localhost:8088

## Deploy to Production

### Option A: DigitalOcean App Platform (Recommended)

```bash
# Update existing app
doctl apps update <app-id> --spec superset/superset-app.yaml

# Set secrets in DO Console:
# 1. Go to https://cloud.digitalocean.com/apps/
# 2. Select "superset-analytics"
# 3. Settings > Environment Variables
# 4. Add SUPABASE_DB_PASSWORD (encrypted)
# 5. Add SUPERSET_SECRET_KEY (encrypted)
```

### Option B: Direct Docker Deployment

```bash
# SSH to production server
ssh root@superset.insightpulseai.net

# Clone/update repo
cd /opt
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/superset

# Set production secrets
nano .env

# Deploy
docker-compose up -d
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init
```

## Connecting Superset to Odoo Data

Once Superset is running:

1. **Login**: https://superset.insightpulseai.net

2. **Add Database**:
   - Settings > Database Connections > + Database
   - Display Name: **InsightPulse Odoo**
   - SQLAlchemy URI:
     ```
     postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres
     ```
   - Test Connection

3. **Create Datasets**:
   - Data > Datasets > + Dataset
   - Database: InsightPulse Odoo
   - Schema: Select Odoo schema (e.g., `public`)
   - Table: Choose Odoo tables

4. **Build Charts & Dashboards**:
   - Create visualizations from Odoo datasets
   - Combine into business intelligence dashboards

## Troubleshooting

### Cannot connect to Supabase
```bash
# Test connection
docker-compose exec superset bash
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
```

If connection fails:
- Check `.env` file has correct password
- Verify Supabase project is active
- Check connection pooler enabled in Supabase settings

### Database migration errors
```bash
# Reset migrations
docker-compose exec superset superset db downgrade
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init
```

### View logs
```bash
docker-compose logs -f superset
```

## Verification Checklist

- [ ] `.env` file created with secrets
- [ ] Superset starts without errors
- [ ] Database migrations completed
- [ ] Admin user created
- [ ] Can login at http://localhost:8088
- [ ] Sample dashboards visible
- [ ] Can connect to Supabase database
- [ ] Ready for production deployment

## Next Steps

1. **Test locally** - Verify Supabase connection works
2. **Deploy to production** - Use DigitalOcean App Platform spec
3. **Connect Odoo data** - Add Supabase as data source
4. **Build dashboards** - Create BI dashboards for business insights
5. **Set up monitoring** - Configure alerts and health checks
6. **Configure security** - Update passwords, enable HTTPS

## Resources

- **Superset Docs**: https://superset.apache.org/docs/
- **Supabase Dashboard**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
- **Production URL**: https://superset.insightpulseai.net
- **MCP Endpoint**: https://mcp.insightpulseai.net
