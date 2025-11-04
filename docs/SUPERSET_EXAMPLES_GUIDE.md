# Loading Official Superset Examples

Complete guide to loading official Superset example dashboards on DigitalOcean App Platform.

---

## Quick Summary

**Created Custom Dashboards:** ✅ 8 production-ready dashboards in `superset/dashboards/`:
1. `executive-finance-overview.json` - High-level KPIs
2. `agency-operations.json` - Agency-specific metrics
3. `expense-management.json` - Expense tracking
4. `bir-compliance.json` - BIR form monitoring
5. `cash-flow.json` - Cash flow analysis
6. `ocr-processing.json` - OCR automation stats
7. `ai-agent-performance.json` - AI bot usage
8. `slack-metrics.json` - Slack integration tracking

**Official Examples:** Follow instructions below to load World Bank, Birth Names, Flights, etc.

---

## Method 1: Interactive Console (DigitalOcean App Platform)

### Step 1: Open Console Session

```bash
# Start interactive console
doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset-analytics

# Wait for shell prompt, then run:
superset db upgrade
superset load_examples
superset init
```

**Note:** Console sessions are ephemeral - changes persist in database but not in filesystem.

### Step 2: Verify Examples Loaded

1. Open https://superset.insightpulseai.net
2. Login: admin / SHWYXDMFAwXI1drT
3. Navigate to Dashboards
4. Look for:
   - World Bank's Data
   - Birth Names Dashboard
   - Misc Charts
   - Tabbed Dashboard
   - Flights

---

## Method 2: Import Custom Dashboards via UI

### Step 1: Export Dashboard JSON

All custom dashboard JSON files are ready in `superset/dashboards/`:

```bash
ls -1 superset/dashboards/
# executive-finance-overview.json
# agency-operations.json
# expense-management.json
# bir-compliance.json
# cash-flow.json
# ocr-processing.json
# ai-agent-performance.json
# slack-metrics.json
```

### Step 2: Import via Superset UI

1. **Login:** https://superset.insightpulseai.net
   - Username: `admin`
   - Password: `SHWYXDMFAwXI1drT`

2. **Import Dashboard:**
   - Settings → Import dashboards
   - Upload JSON file (e.g., `executive-finance-overview.json`)
   - Click "Import"

3. **Configure Data Sources:**
   - After import, go to Settings → Database Connections
   - Verify Supabase connection:
     ```
     postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=prefer
     ```

4. **Create Datasets:**
   - For each dashboard, create required datasets from SQL queries
   - SQL Lab → Run query → Save → Create Dataset
   - Example queries are in `docs/SUPERSET_DASHBOARD_EXAMPLES.md`

---

## Method 3: Database Migration (Alternative)

If you need examples for development/testing, you can load them locally:

### Step 1: Local Superset with Docker

```bash
# Pull official Superset image
docker pull apache/superset:latest

# Run Superset container
docker run -d \
  --name superset \
  -p 8088:8088 \
  -e "SUPERSET_SECRET_KEY=$(openssl rand -base64 42)" \
  apache/superset:latest

# Load examples in container
docker exec -it superset superset db upgrade
docker exec -it superset superset load_examples
docker exec -it superset superset init

# Create admin user
docker exec -it superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password admin

# Access: http://localhost:8088
```

### Step 2: Export from Local to Production

1. **Export from Local:**
   - Dashboards → Select dashboard → ⋮ → Export
   - Save JSON file

2. **Import to Production:**
   - Login to https://superset.insightpulseai.net
   - Settings → Import dashboards
   - Upload exported JSON

---

## What Official Examples Include

### 1. World Bank's Data
- **Charts:** GDP, Life Expectancy, Population
- **Data:** World development indicators
- **Format:** Line charts, scatter plots, bubble charts

### 2. Birth Names Dashboard
- **Charts:** Baby name trends over time
- **Data:** US Social Security baby names
- **Format:** Line charts, treemaps, word clouds

### 3. Misc Charts
- **Charts:** Various chart type examples
- **Data:** Sample datasets
- **Format:** Bar, pie, table, gauge, etc.

### 4. Tabbed Dashboard
- **Charts:** Multi-tab dashboard example
- **Data:** Various metrics
- **Format:** Tab layout demonstration

### 5. Flights Dashboard
- **Charts:** Flight delays and performance
- **Data:** US domestic flights
- **Format:** Sunburst, sankey, heatmaps

---

## Custom Dashboard Features

All 8 custom dashboards include:

### Common Features
- ✅ Native filters (Agency, Date Range)
- ✅ Auto-refresh (5-30 minutes)
- ✅ Color schemes optimized for Finance
- ✅ Philippine Peso formatting (₱)
- ✅ Responsive layouts
- ✅ Conditional formatting
- ✅ Interactive drill-downs

### Data Sources
- **Odoo PostgreSQL:** Sale orders, expenses, invoices
- **Supabase:** OCR tasks, AI agent logs, Slack metrics
- **Custom Tables:** BIR compliance, automation stats

### Chart Types Used
- Big Number KPIs
- Line/Area/Bar charts
- Pie/Donut charts
- Tables with conditional formatting
- Treemaps
- Gauges
- Funnels
- Heatmaps
- Word clouds
- Bullet charts

---

## Troubleshooting

### Issue: Console Session Times Out

**Solution:**
- Console sessions are ephemeral and time out after inactivity
- Re-run: `doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset-analytics`
- Database changes persist across sessions

### Issue: Examples Already Loaded

**Check:**
```bash
# In console
superset db shell
> SELECT COUNT(*) FROM dashboards;
> SELECT dashboard_title FROM dashboards;
```

If examples exist, no need to reload.

### Issue: Import Fails with "Dataset Not Found"

**Solution:**
1. Create required datasets first from SQL Lab
2. Each dashboard needs corresponding datasets (sale_order, hr_expense, etc.)
3. Reference SQL queries in `docs/SUPERSET_DASHBOARD_EXAMPLES.md`

### Issue: Database Connection Error

**Verify connection string:**
```
postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=prefer
```

**Test connection:**
```bash
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=prefer" -c "SELECT 1"
```

---

## Production Checklist

Before deploying dashboards to production:

- [ ] Database connection tested and working
- [ ] All required datasets created
- [ ] SQL queries return data (not empty results)
- [ ] Filters configured (agency, date range)
- [ ] Color schemes applied
- [ ] Refresh intervals set appropriately
- [ ] Permissions configured (if using RLS)
- [ ] Dashboard published and certified
- [ ] Email reports scheduled (optional)

---

## Next Steps

1. **Load Official Examples** (optional):
   ```bash
   doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset-analytics
   # Then in console:
   superset db upgrade && superset load_examples && superset init
   ```

2. **Import Custom Dashboards**:
   - Start with `executive-finance-overview.json`
   - Create required Odoo datasets
   - Test with sample data
   - Import remaining 7 dashboards

3. **Connect to Odoo Data**:
   - Verify Odoo PostgreSQL access
   - Create datasets for: sale_order, hr_expense, account_move
   - Test queries from `docs/SUPERSET_DASHBOARD_EXAMPLES.md`

4. **Schedule Reports**:
   - Dashboard → ⋮ → Email Reports
   - Set recipients: jgtolentino_rn@yahoo.com
   - Choose frequency: Daily/Weekly/Monthly
   - Select format: PNG or PDF

---

## Resources

- **Superset URL:** https://superset.insightpulseai.net
- **Login:** admin / SHWYXDMFAwXI1drT
- **App ID:** 73af11cb-dab2-4cb1-9770-291c536531e6
- **Database:** Supabase (project: spdtwktxdalcfigzeqrz)

**Documentation:**
- Custom Dashboards: `superset/dashboards/*.json`
- SQL Queries: `docs/SUPERSET_DASHBOARD_EXAMPLES.md`
- Deployment Guide: `DEPLOYMENT_GUIDE.md`

**Support:**
- Email: jgtolentino_rn@yahoo.com
- Superset Docs: https://superset.apache.org/docs/intro

---

**Status:** ✅ 8 custom dashboards created and ready to import
**Last Updated:** 2025-11-04
**Version:** 1.0.0
