# Superset Production Deployment Guide

## Configuration Overview

Superset is configured to use **Supabase PostgreSQL** as the metadata store instead of SQLite.

### Supabase Connection Details
- **Project**: spdtwktxdalcfigzeqrz
- **Host**: aws-1-us-east-1.pooler.supabase.com
- **Port**: 6543 (connection pooler)
- **Database**: postgres
- **User**: postgres.spdtwktxdalcfigzeqrz

## Local Development

1. **Set environment variables**:
   ```bash
   # Edit .env file
   nano superset/.env

   # Add your Supabase password:
   SUPABASE_DB_PASSWORD=your-actual-password
   SUPERSET_SECRET_KEY=$(openssl rand -base64 42)
   ```

2. **Start Superset**:
   ```bash
   cd superset
   docker-compose up -d
   ```

3. **Initialize database** (first time only):
   ```bash
   # Run database migrations
   docker-compose exec superset superset db upgrade

   # Create admin user
   docker-compose exec superset superset fab create-admin \
     --username admin \
     --firstname Admin \
     --lastname User \
     --email admin@insightpulseai.net \
     --password admin

   # Initialize roles
   docker-compose exec superset superset init
   ```

4. **Access Superset**:
   - URL: http://localhost:8088
   - Username: admin
   - Password: admin (change in production!)

## Production Deployment (DigitalOcean)

### Option 1: Deploy to existing `superset-analytics` app

1. **Update app environment variables**:
   ```bash
   doctl apps update <app-id> --spec superset-app.yaml
   ```

2. **Set secrets via DigitalOcean Console**:
   - Go to: https://cloud.digitalocean.com/apps/
   - Select: `superset-analytics`
   - Settings > Environment Variables
   - Add:
     - `SUPABASE_DB_PASSWORD` (encrypted)
     - `SUPERSET_SECRET_KEY` (encrypted)

### Option 2: Manual Docker deployment

1. **On production server**:
   ```bash
   cd /opt/superset
   git pull

   # Update .env with production values
   nano .env

   # Restart with new configuration
   docker-compose down
   docker-compose up -d

   # Run migrations
   docker-compose exec superset superset db upgrade
   docker-compose exec superset superset init
   ```

## Database Migration from SQLite to Supabase

If you have existing data in SQLite:

```bash
# Export from SQLite
docker-compose exec superset superset export-dashboards -f /tmp/dashboards.zip

# Update docker-compose.yaml to use Supabase (already done)
docker-compose down
docker-compose up -d

# Initialize new Supabase database
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init

# Import dashboards
docker-compose exec superset superset import-dashboards -p /tmp/dashboards.zip
```

## Connecting to Odoo Data

Once Superset is running, connect to Odoo data:

1. **Login to Superset**: https://superset.insightpulseai.net

2. **Add Database Connection**:
   - Settings > Database Connections > + Database
   - Supported Databases: PostgreSQL
   - SQLAlchemy URI:
     ```
     postgresql://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres
     ```
   - Display Name: "InsightPulse Odoo Data"
   - Test Connection

3. **Create Datasets**:
   - Data > Datasets > + Dataset
   - Select: "InsightPulse Odoo Data"
   - Choose tables from Odoo schemas

4. **Build Dashboards**:
   - Create charts from datasets
   - Combine into dashboards
   - Set permissions and sharing

## Monitoring

Check Superset health:
```bash
curl https://superset.insightpulseai.net/health
```

Check logs:
```bash
docker-compose logs -f superset
```

## Troubleshooting

### Connection refused to Supabase
- Check `.env` file has correct password
- Verify Supabase project is active
- Check connection pooler is enabled (port 6543)

### Database migration errors
```bash
# Reset and reinitialize
docker-compose exec superset superset db downgrade
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init
```

### Permission errors
```bash
# Fix volume permissions
sudo chown -R 1000:1000 superset_home/
```

## Security Checklist

- [ ] Changed default admin password
- [ ] Set strong `SUPERSET_SECRET_KEY`
- [ ] Stored `SUPABASE_DB_PASSWORD` securely
- [ ] Enabled HTTPS (`SESSION_COOKIE_SECURE = True`)
- [ ] Configured firewall rules
- [ ] Set up regular backups
- [ ] Enabled audit logging
- [ ] Configured CORS properly

## Backup Strategy

Superset metadata is in Supabase, which has automatic backups. For additional safety:

```bash
# Export all dashboards
docker-compose exec superset superset export-dashboards -f /backup/dashboards-$(date +%Y%m%d).zip

# Export database
pg_dump -h aws-1-us-east-1.pooler.supabase.com -p 6543 \
  -U postgres.spdtwktxdalcfigzeqrz postgres > backup.sql
```

## Resources

- Superset Docs: https://superset.apache.org/docs/
- Supabase Dashboard: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
- DigitalOcean Apps: https://cloud.digitalocean.com/apps/
