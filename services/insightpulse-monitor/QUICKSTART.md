# InsightPulse Monitor MCP - Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Local Development

### 1. Clone & Navigate
```bash
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/services/insightpulse-monitor
```

### 2. Set Up Environment
```bash
cp .env.example .env
# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_SERVICE_KEY
# - ODOO_URL
# - ODOO_API_KEY
```

### 3. Run with Docker
```bash
docker-compose up --build
```

### 4. Test
```bash
# Health check
curl http://localhost:8000/health

# Run full test suite
./test_mcp.sh
```

## 🌐 Production Deployment

### Prerequisites
- GitHub account
- DigitalOcean account
- doctl CLI installed

### 1. Set GitHub Secrets
Go to **Settings → Secrets → Actions**, add:
- `DO_ACCESS_TOKEN`
- `DO_MONITOR_APP_ID`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `ODOO_URL`
- `ODOO_API_KEY`

### 2. Deploy
```bash
# Option A: Push to main (automatic)
git push origin main

# Option B: Manual via GitHub Actions
# Go to Actions → InsightPulse Monitor - Deploy → Run workflow

# Option C: Via CLI
doctl apps create --spec app.yaml
```

### 3. Verify
```bash
# Get app URL
APP_URL=$(doctl apps get $DO_MONITOR_APP_ID --format DefaultIngress --no-header)

# Test health
curl https://$APP_URL/health
```

## 📊 Database Setup

Run this SQL in your Supabase SQL editor:

```sql
-- Copy SQL from DEPLOYMENT.md Part 1, Step 3
-- Or use the migration script:
psql $DATABASE_URL < migrations/001_initial_schema.sql
```

## 🔧 Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_system_health` | Check Odoo, Supabase, infrastructure health |
| `track_bir_filing_deadlines` | Monitor BIR filing deadlines by agency |
| `get_month_end_status` | Real-time month-end closing status |
| `list_failed_jobs` | List failed background jobs |
| `get_error_traces` | Retrieve error logs and stack traces |
| `monitor_compliance_status` | ATP validity, certificates, compliance |
| `check_database_performance` | Slow queries, performance metrics |
| `get_agency_metrics` | KPIs by agency (financial, operational) |

## 📖 Full Documentation

- **README.md**: Complete feature documentation
- **DEPLOYMENT.md**: Step-by-step deployment guide
- **SECRETS.md**: Security and secrets configuration
- **test_mcp.sh**: Automated testing script

## 🆘 Troubleshooting

### Server won't start
```bash
# Check logs
docker-compose logs

# Common issues:
# - Invalid Supabase URL
# - Wrong service key (use service_role, not anon)
# - Missing environment variables
```

### Health check fails
```bash
# Test connection to Supabase
curl $SUPABASE_URL/rest/v1/

# Test connection to Odoo
curl $ODOO_URL/web/database/list
```

### Tests fail
```bash
# Ensure database tables exist
# Check DATABASE SCHEMA in DEPLOYMENT.md

# Verify environment variables
cat .env
```

## 💡 Next Steps

1. ✅ Deploy to DigitalOcean
2. ✅ Set up monitoring alerts
3. ✅ Configure custom domain
4. ✅ Enable OAuth (optional)
5. ✅ Add custom metrics

## 📞 Support

- **Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Docs**: See README.md and DEPLOYMENT.md
- **DigitalOcean**: https://docs.digitalocean.com/products/app-platform/

---

**Time to deploy**: ~15 minutes
**Cost**: Starting at $5/month
**Monitoring**: 9 enterprise-grade tools included
