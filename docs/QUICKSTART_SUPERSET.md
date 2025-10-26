# Quick Start Guide: Superset Integration

Get up and running with Odoo-Superset integration in 15 minutes.

## Prerequisites

- Odoo 19.0 running
- PostgreSQL 15+ accessible
- Apache Superset 3.0+ instance (or ability to deploy one)
- Python `requests` library: `pip install requests`

## 1. Install the Module (5 minutes)

### Option A: Via Odoo UI

1. Copy module to addons directory:
   ```bash
   cp -r addons/custom/superset_connector /path/to/odoo/addons/
   ```

2. Restart Odoo:
   ```bash
   systemctl restart odoo
   # or
   docker compose restart odoo
   ```

3. Update apps list:
   - Go to **Apps** in Odoo
   - Click **Update Apps List**
   - Search for "Superset Connector"
   - Click **Install**

### Option B: Via Command Line

```bash
odoo-bin -i superset_connector -d your_database
```

## 2. Configure Database Access (3 minutes)

Create read-only user for Superset:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create user
CREATE USER superset_readonly WITH PASSWORD 'SecurePassword123!';

# Grant permissions
GRANT CONNECT ON DATABASE your_odoo_db TO superset_readonly;
GRANT USAGE ON SCHEMA public TO superset_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_readonly;

# Exit
\q
```

## 3. Create Analytics Views (2 minutes)

```bash
# Execute SQL script
psql -U odoo -d your_odoo_db -f addons/custom/superset_connector/sql/erp_analytics_views.sql

# Verify views created
psql -U odoo -d your_odoo_db -c "\dv vw_*"
```

Expected output:
```
 vw_ar_aging
 vw_customer_ltv
 vw_employee_headcount
 vw_inventory_turnover
 vw_monthly_revenue
 vw_product_performance
 vw_sales_kpi_day
 vw_stock_level_summary
```

## 4. Configure Superset (3 minutes)

### Connect to Odoo Database

1. Log into Superset
2. Go to **Data > Databases**
3. Click **+ Database**
4. Select **PostgreSQL**
5. Enter connection details:
   ```
   Host: your-postgres-host
   Port: 5432
   Database: your_odoo_db
   Username: superset_readonly
   Password: SecurePassword123!
   ```
6. Click **Test Connection**
7. Click **Connect**

### Add Datasets

1. Go to **Data > Datasets**
2. Click **+ Dataset**
3. Select:
   - **Database**: Your Odoo database
   - **Schema**: `public`
   - **Table**: `vw_sales_kpi_day`
4. Click **Add**
5. Repeat for other views

## 5. Configure Odoo Settings (2 minutes)

1. Log into Odoo as Administrator
2. Go to **Settings > General Settings**
3. Scroll to **Superset Integration**
4. Configure:
   - **Superset URL**: `https://your-superset-url.com`
   - **Username**: Your Superset admin username
   - **Password**: Your Superset admin password
   - **Database ID**: `1` (or your database ID from Superset)
   - **Enable RLS**: ✓ (checked)
   - **Token Expiry**: `3600`
   - **CSP Enabled**: ✓ (checked)
5. Click **Save**

## 6. Test the Integration (5 minutes)

### Create a Simple Chart in Superset

1. Go to **Charts > + Chart**
2. Select dataset: `vw_sales_kpi_day`
3. Choose **Big Number**
4. Configure:
   - **Metric**: `SUM(total_revenue)`
   - **Time Range**: Last 30 days
5. Click **Run Query**
6. Click **Save** as "Total Revenue"

### Create a Dashboard

1. Go to **Dashboards > + Dashboard**
2. Name: "Sales KPI"
3. Drag "Total Revenue" chart onto dashboard
4. Click **Save**
5. Copy the dashboard UUID from URL

### Embed in Odoo

1. In Odoo, go to **Superset > Tokens**
2. Click **Create**
3. Fill in:
   - **Name**: Sales KPI Dashboard
   - **Dashboard ID**: [paste UUID from Superset]
4. Click **Generate Token**
5. Open in new tab: `/superset/dashboard/[UUID]`

You should see the Superset dashboard embedded in Odoo! 🎉

## Troubleshooting

### "Failed to generate token"

**Check:**
- Superset URL is correct
- Superset credentials are valid
- Superset is accessible from Odoo server
- Check Odoo logs: `tail -f /var/log/odoo/odoo.log`

### "Dashboard not loading"

**Check:**
- Dashboard UUID is correct
- User has access to the dashboard in Superset
- CSP settings allow iframe from Superset URL
- Check browser console for errors

### "No data in dashboard"

**Check:**
- Analytics views have data: `SELECT COUNT(*) FROM vw_sales_kpi_day;`
- Database user has SELECT permissions
- RLS filters are not too restrictive
- Check Superset SQL Lab for query errors

## Next Steps

1. **Create more dashboards**: See [SUPERSET_DASHBOARDS.md](docs/SUPERSET_DASHBOARDS.md)
2. **Configure RLS**: See [SUPERSET_INTEGRATION.md](docs/SUPERSET_INTEGRATION.md#row-level-security-rls)
3. **Optimize performance**: See [BI_ARCHITECTURE.md](docs/BI_ARCHITECTURE.md#performance-optimization-strategy)
4. **Production deployment**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Support

- **Module README**: `addons/custom/superset_connector/README.rst`
- **Full Documentation**: `docs/SUPERSET_INTEGRATION.md`
- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues

---

**Estimated Time**: 15-20 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Odoo, PostgreSQL, Superset access
