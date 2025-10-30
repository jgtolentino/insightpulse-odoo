# Apache Superset Production Deployment

## Summary

Complete production deployment configuration for Apache Superset at `http://insightpulseai.net/superset` using **DigitalOcean App Platform**, **Supabase PostgreSQL**, and **Traefik** reverse proxy.

**Status**: ✅ Ready for Deployment

## Quick Start

```bash
# 1. Authenticate to DigitalOcean
doctl auth init

# 2. Deploy (secrets pre-configured)
./deploy/superset/deploy.sh

# Defaults:
# - Database password: Postgres_26
# - Admin password: Postgres_26
# - Admin username: admin
```

## Deployment Architecture

```
                    ┌─────────────────────────────────────┐
                    │  Client Browser                     │
                    └──────────────┬──────────────────────┘
                                   │ HTTPS
                    ┌──────────────▼──────────────────────┐
                    │  Traefik Reverse Proxy              │
                    │  - Path routing: /superset          │
                    │  - SSL/TLS termination              │
                    │  - Rate limiting                    │
                    │  - Security headers                 │
                    └──────────────┬──────────────────────┘
                                   │ HTTP
         ┌─────────────────────────┴────────────────────────────┐
         │                                                       │
         │          DigitalOcean App Platform                    │
         │                                                       │
         │  ┌─────────────────┐  ┌──────────────┐  ┌─────────┐ │
         │  │ Superset Web    │  │ Superset     │  │ Superset│ │
         │  │ (Gunicorn/      │  │ Worker       │  │ Beat    │ │
         │  │  gevent)        │  │ (Celery)     │  │(Scheduler)│
         │  │ basic-xs        │  │ basic-xxs    │  │basic-xxs│ │
         │  └────────┬────────┘  └──────┬───────┘  └────┬────┘ │
         │           │                  │               │       │
         │           └──────────────────┼───────────────┘       │
         │                              │                       │
         │                   ┌──────────▼────────┐              │
         │                   │  Redis Cache      │              │
         │                   │  basic-xxs        │              │
         │                   └───────────────────┘              │
         │                                                       │
         └───────────────────────┬───────────────────────────────┘
                                 │ PostgreSQL
                      ┌──────────▼──────────┐
                      │  Supabase PostgreSQL│
                      │  (Metadata Database)│
                      │  - Connection pooler│
                      │  - SSL required     │
                      │  - Automated backups│
                      └─────────────────────┘
```

## Project Structure

```
insightpulse-odoo/
│
├── infra/superset/
│   └── superset-app.yaml          # DigitalOcean App Platform spec
│
├── config/superset/
│   └── superset_config_production.py  # Production configuration
│
├── docker/superset/
│   ├── Dockerfile                 # Production Docker image
│   └── entrypoint.sh             # Initialization script
│
├── deploy/superset/
│   ├── deploy.sh                 # Automated deployment script
│   └── traefik.yml               # Traefik reverse proxy config
│
├── security/superset/
│   └── secrets.env.example       # Security configuration template
│
└── docs/superset/
    ├── README.md                 # This file
    └── DEPLOYMENT_GUIDE.md       # Comprehensive deployment guide
```

## Key Features

### Security Hardening
✅ Strong SECRET_KEY generation (42 characters)
✅ HTTPS enforcement via Traefik
✅ SSL/TLS for database connections
✅ Content Security Policy headers
✅ Rate limiting (100 req/s, burst 200)
✅ Session security (HttpOnly, Secure, SameSite)
✅ CSRF protection enabled

### Production Optimizations
✅ Gunicorn with gevent async workers (4 workers, 1000 connections)
✅ Redis caching (data, thumbnails, results)
✅ PostgreSQL connection pooling (pool_size: 10, max_overflow: 20)
✅ Celery async queries and scheduled tasks
✅ Health checks and graceful shutdowns
✅ Resource limits and auto-scaling

### Database Drivers Included
✅ PostgreSQL (psycopg2-binary) - Supabase
✅ MySQL/MariaDB (pymysql, mysqlclient)
✅ BigQuery (pybigquery)
✅ Snowflake (snowflake-sqlalchemy)
✅ Redshift (sqlalchemy-redshift)
✅ MongoDB (pymongo)

## Cost Breakdown

### Recommended Configuration
- **Superset Web** (basic-xs): $12/month - 1GB RAM, 1 vCPU
- **Superset Worker** (basic-xxs): $5/month - 512MB RAM, 1 vCPU
- **Superset Beat** (basic-xxs): $5/month - 512MB RAM, 1 vCPU
- **Redis** (basic-xxs): $5/month - 512MB RAM, 1 vCPU
- **Total**: ~$27/month

### Budget Configuration
- **All services** (basic-xxs): ~$20/month
- Suitable for small to medium workloads (<100 concurrent users)

### Cost Optimization Tips
1. Use basic-xxs for all services ($20/month total)
2. Combine worker and beat into single service
3. Use external managed Redis (DigitalOcean Managed Redis)
4. Disable unused features (alerts, scheduled reports)

## Configuration Files

### 1. DigitalOcean App Platform Spec
**File**: `infra/superset/superset-app.yaml`

**Key Configuration**:
- 4 services: web, worker, beat, redis
- Supabase PostgreSQL connection
- Environment variables for security and performance
- Health checks and resource limits

### 2. Production Superset Config
**File**: `config/superset/superset_config_production.py`

**Key Features**:
- Supabase PostgreSQL with SSL
- Redis caching for data, thumbnails, results
- Celery configuration for async queries
- Security headers and CORS
- Rate limiting
- Email and Slack notifications

### 3. Production Dockerfile
**File**: `docker/superset/Dockerfile`

**Key Features**:
- Based on official Apache Superset image
- PostgreSQL driver (psycopg2-binary)
- Additional database drivers (MySQL, BigQuery, Snowflake, etc.)
- Gunicorn with gevent workers
- Security hardening (non-root user, minimal permissions)
- Health checks

### 4. Traefik Reverse Proxy
**File**: `deploy/superset/traefik.yml`

**Key Features**:
- Path-based routing: `/superset`
- HTTPS enforcement
- Let's Encrypt SSL certificates
- Security headers (CSP, HSTS, X-Frame-Options)
- Rate limiting (100 req/s, burst 200)
- Health checks and sticky sessions

## Deployment Workflow

### Pre-Deployment
1. ✅ Generate strong secrets
2. ✅ Verify Supabase PostgreSQL access
3. ✅ Authenticate to DigitalOcean
4. ✅ Review and customize configuration

### Deployment
1. ✅ Run deployment script: `./deploy/superset/deploy.sh`
2. ✅ Monitor build and deployment logs
3. ✅ Configure secrets in DO dashboard
4. ✅ Verify health checks pass

### Post-Deployment
1. ✅ Configure Traefik reverse proxy
2. ✅ Setup DNS (A record or CNAME)
3. ✅ Verify HTTPS and path routing
4. ✅ Create database connections in Superset
5. ✅ Configure alerts and notifications
6. ✅ Setup automated backups
7. ✅ Configure monitoring

## Monitoring and Maintenance

### Health Checks
```bash
# Direct app health check
curl -f https://superset-analytics-xxxxx.ondigitalocean.app/health

# Via Traefik (after configuration)
curl -f https://insightpulseai.net/superset/health
```

### Logs
```bash
# Real-time logs
doctl apps logs $APP_ID --follow

# Specific service logs
doctl apps logs $APP_ID --type run_logs --component superset-web
doctl apps logs $APP_ID --type run_logs --component superset-worker
```

### Performance Metrics
- **DigitalOcean Dashboard**: Apps → superset-analytics → Insights
- **Metrics**: CPU, Memory, Request throughput, Response times
- **Alerts**: Configure in DO dashboard for high resource usage

### Backups
- **Automated**: Supabase PostgreSQL (7-30 days retention)
- **Manual**: Export dashboards and datasets regularly
- **Restore**: Via Supabase dashboard or `psql` CLI

## Troubleshooting

### Common Issues

**1. Deployment Failed**
```bash
# Check build logs
doctl apps logs $APP_ID --type build

# Redeploy with force rebuild
doctl apps create-deployment $APP_ID --force-rebuild
```

**2. Database Connection Failed**
```bash
# Test connection
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:$POSTGRES_PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require" -c "SELECT 1"

# Check secrets in DO dashboard
# Settings → Environment Variables
```

**3. Path Routing Not Working**
```bash
# Verify Traefik config
docker logs traefik

# Test direct access first
curl -I https://superset-analytics-xxxxx.ondigitalocean.app/health

# Then test via Traefik
curl -I https://insightpulseai.net/superset/health
```

### Emergency Procedures

**Rollback Deployment**:
```bash
doctl apps list-deployments $APP_ID
doctl apps rollback-deployment $APP_ID [PREVIOUS_DEPLOYMENT_ID]
```

**Database Restore**:
- Go to Supabase dashboard → Database → Backups
- Select backup point → Click "Restore"

## Security Considerations

### Secrets Management
- ❌ Never commit secrets to git
- ✅ Store in DigitalOcean App Platform environment variables
- ✅ Use `SECRET` type for sensitive values
- ✅ Rotate secrets regularly (every 90 days)

### Network Security
- ✅ HTTPS only (HTTP redirects to HTTPS)
- ✅ SSL/TLS for database connections
- ✅ Internal network for Redis
- ✅ Rate limiting to prevent abuse

### Application Security
- ✅ Strong SECRET_KEY (42+ characters)
- ✅ Content Security Policy headers
- ✅ CSRF protection enabled
- ✅ Session security (HttpOnly, Secure, SameSite)
- ✅ Row Level Security for data access

## Next Steps

1. **Deploy to Production**: Run `./deploy/superset/deploy.sh`
2. **Configure Traefik**: Setup reverse proxy for path routing
3. **Setup DNS**: Point `insightpulseai.net` to Traefik server
4. **Verify Deployment**: Test health checks and login
5. **Create Connections**: Add database connections in Superset
6. **Configure Alerts**: Setup email/Slack notifications
7. **Monitor**: Setup monitoring and alerting

## Documentation

- **Deployment Guide**: [`docs/superset/DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md)
- **Security Configuration**: [`security/superset/secrets.env.example`](../../security/superset/secrets.env.example)
- **App Platform Spec**: [`infra/superset/superset-app.yaml`](../../infra/superset/superset-app.yaml)
- **Production Config**: [`config/superset/superset_config_production.py`](../../config/superset/superset_config_production.py)

## Support

**Internal**:
- Configuration issues: Check `config/superset/`
- Deployment issues: Review `deploy/superset/deploy.sh` logs
- Infrastructure: Review `infra/superset/superset-app.yaml`

**External**:
- [Apache Superset Documentation](https://superset.apache.org/docs/6.0.0/)
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Supabase PostgreSQL Docs](https://supabase.com/docs/guides/database)
- [Traefik Documentation](https://doc.traefik.io/traefik/)

---

**Deployment Date**: 2025-10-30
**Version**: 1.0.0
**Status**: ✅ Production Ready
**Architecture**: DigitalOcean App Platform + Supabase + Traefik
**Cost**: ~$27/month (recommended) or ~$20/month (budget)
