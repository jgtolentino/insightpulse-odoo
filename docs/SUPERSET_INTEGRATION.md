# Superset Integration Guide

Complete guide for integrating Apache Superset with Odoo for advanced Business Intelligence and data visualization.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Security Setup](#security-setup)
7. [Creating Dashboards](#creating-dashboards)
8. [Embedding in Odoo](#embedding-in-odoo)
9. [Row-Level Security (RLS)](#row-level-security-rls)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)

## Overview

This integration enables Odoo to use Apache Superset as a powerful BI platform with:

- **Secure Dashboard Embedding**: Guest token authentication for iframe embedding
- **Row-Level Security**: Data filtering based on Odoo user permissions
- **Multi-Company Support**: Automatic data isolation by company
- **Pre-built Analytics**: SQL views for common Odoo metrics
- **SSO Integration**: Single sign-on with automatic token management

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Odoo Users                        │
└─────────────┬───────────────────────────────────────┘
              │
              │ 1. Request Dashboard
              ▼
┌─────────────────────────────────────────────────────┐
│           Odoo (superset_connector module)          │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Controller: /superset/dashboard/<uuid>      │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
│                 │ 2. Get/Generate Token              │
│                 ▼                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  Model: superset.token                       │  │
│  │  - Generate guest token                      │  │
│  │  - Apply RLS filters (company_id)            │  │
│  └──────────────┬───────────────────────────────┘  │
└─────────────────┼───────────────────────────────────┘
                  │
                  │ 3. API Call (with credentials)
                  ▼
┌─────────────────────────────────────────────────────┐
│              Apache Superset                         │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  API: /api/v1/security/guest_token/          │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
│                 │ 4. Return Token                    │
│                 ▼                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  Dashboard with RLS applied                  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ 5. Query Data (with RLS)
                  ▼
┌─────────────────────────────────────────────────────┐
│           PostgreSQL (Odoo Database)                 │
│                                                      │
│  - Analytics Views (vw_sales_kpi_day, etc.)         │
│  - RLS enforcement via SQL clauses                   │
│  - Read-only user (superset_readonly)               │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

### Software Requirements

- **Odoo**: 19.0 or higher
- **Apache Superset**: 3.0 or higher
- **PostgreSQL**: 15 or higher
- **Python**: 3.11+ with `requests` library
- **Redis**: 7+ (for Superset caching)

### Network Requirements

- Odoo must be able to reach Superset API (HTTP/HTTPS)
- Superset must be able to connect to PostgreSQL database
- HTTPS recommended for production deployments

### Access Requirements

- PostgreSQL superuser or database owner (for view creation)
- Superset admin credentials
- Odoo administrator access

## Installation

### Step 1: Install Odoo Module

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r addons/custom/superset_connector /path/to/odoo/addons/
   ```

2. Update Odoo apps list:
   ```bash
   odoo-bin -u all -d your_database
   ```
   Or via UI: Apps > Update Apps List

3. Install the module:
   - Go to Apps
   - Search for "Superset Connector"
   - Click Install

### Step 2: Install Python Dependencies

```bash
pip install requests
```

### Step 3: Create Analytics Views

Execute the SQL script in your Odoo PostgreSQL database:

```bash
psql -U odoo -d your_database -f addons/custom/superset_connector/sql/erp_analytics_views.sql
```

This creates the following views:
- `vw_sales_kpi_day` - Daily sales metrics
- `vw_product_performance` - Product sales and profitability
- `vw_customer_ltv` - Customer lifetime value
- `vw_stock_level_summary` - Current inventory levels
- `vw_inventory_turnover` - Inventory turnover metrics
- `vw_ar_aging` - Accounts receivable aging
- `vw_monthly_revenue` - Monthly revenue by account
- `vw_employee_headcount` - Employee headcount metrics

### Step 4: Create Read-Only Database User

Create a dedicated read-only user for Superset:

```sql
-- Create user
CREATE USER superset_readonly WITH PASSWORD 'your_secure_password';

-- Grant connection
GRANT CONNECT ON DATABASE your_odoo_db TO superset_readonly;
GRANT USAGE ON SCHEMA public TO superset_readonly;

-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO superset_readonly;

-- Grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO superset_readonly;

-- Grant SELECT on analytics views specifically
GRANT SELECT ON vw_sales_kpi_day TO superset_readonly;
GRANT SELECT ON vw_product_performance TO superset_readonly;
GRANT SELECT ON vw_customer_ltv TO superset_readonly;
GRANT SELECT ON vw_stock_level_summary TO superset_readonly;
GRANT SELECT ON vw_inventory_turnover TO superset_readonly;
GRANT SELECT ON vw_ar_aging TO superset_readonly;
GRANT SELECT ON vw_monthly_revenue TO superset_readonly;
GRANT SELECT ON vw_employee_headcount TO superset_readonly;
```

## Configuration

### Odoo Configuration

1. Navigate to **Settings > General Settings**
2. Scroll to **Superset Integration** section
3. Configure the following:

   | Setting | Description | Example |
   |---------|-------------|---------|
   | Superset URL | Base URL of Superset instance | `https://superset.example.com` |
   | Username | Superset admin username | `admin` |
   | Password | Superset admin password | `your_password` |
   | Database ID | Superset database ID for Odoo | `1` |
   | Enable RLS | Enable row-level security | ✓ (Recommended) |
   | Token Expiry | Token lifetime in seconds | `3600` (1 hour) |
   | CSP Enabled | Enable Content Security Policy | ✓ (Recommended) |

4. Click **Save**

### Superset Configuration

#### 1. Add Database Connection

In Apache Superset:

1. Go to **Data > Databases**
2. Click **+ Database**
3. Select **PostgreSQL**
4. Configure connection:
   
   **SQLAlchemy URI:**
   ```
   postgresql://superset_readonly:your_password@your_host:5432/your_odoo_db
   ```

5. Test connection
6. Click **Connect**

#### 2. Add Datasets

For each analytics view:

1. Go to **Data > Datasets**
2. Click **+ Dataset**
3. Select:
   - **Database**: Your Odoo database
   - **Schema**: `public`
   - **Table**: View name (e.g., `vw_sales_kpi_day`)
4. Click **Add**
5. Configure columns:
   - Set data types
   - Mark temporal columns
   - Configure grouping

#### 3. Enable Guest Token Authentication

In `superset_config.py`:

```python
# Enable guest token authentication
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = "your-secret-key"
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"
GUEST_TOKEN_JWT_EXP_SECONDS = 3600  # 1 hour
```

Restart Superset after configuration changes.

## Security Setup

### Row-Level Security (RLS)

#### 1. Create User-Company Mapping Table

In PostgreSQL:

```sql
-- Create mapping table
CREATE TABLE user_company_access (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    company_id INTEGER NOT NULL,
    FOREIGN KEY (company_id) REFERENCES res_company(id),
    UNIQUE(user_email, company_id)
);

CREATE INDEX idx_user_company_email ON user_company_access(user_email);

-- Populate from Odoo data
INSERT INTO user_company_access (user_email, company_id)
SELECT 
    u.login as user_email,
    rc.company_id
FROM res_users u
JOIN res_company_users_rel rc ON u.id = rc.user_id
WHERE u.active = true;
```

#### 2. Configure RLS in Superset

1. In Superset, go to **Data > Row Level Security**
2. Click **+ Row Level Security**
3. Configure:

   **Filter Name:** `Multi-Company Filter`
   
   **Tables:** Select all analytics views:
   - `vw_sales_kpi_day`
   - `vw_product_performance`
   - `vw_customer_ltv`
   - etc.
   
   **Clause:**
   ```sql
   company_id IN (
       SELECT company_id 
       FROM user_company_access 
       WHERE user_email = '{{ current_username() }}'
   )
   ```
   
   **Group Key:** Leave empty for all users
   
   **Clause:** Select "Regular"

4. Click **Save**

### Content Security Policy (CSP)

The module automatically adds CSP headers when enabled:

```http
Content-Security-Policy: frame-src 'self' https://your-superset-url;
```

This restricts iframe embedding to only your Superset instance.

### SSL/TLS Configuration

**Recommended for production:**

1. Use HTTPS for both Odoo and Superset
2. Configure SSL certificates
3. Enforce HTTPS redirects
4. Update Superset URL in Odoo to use `https://`

## Creating Dashboards

### 1. Create Charts in Superset

Example: Daily Revenue Chart

1. Go to **Charts > + Chart**
2. Select dataset: `vw_sales_kpi_day`
3. Choose chart type: **Line Chart**
4. Configure:
   - **X-axis**: `sale_date`
   - **Metrics**: `SUM(total_revenue)`
   - **Time Grain**: Day
   - **Filters**: Add filters as needed
5. **Run Query**
6. **Save** with a descriptive name

### 2. Create Dashboard

1. Go to **Dashboards > + Dashboard**
2. Name your dashboard (e.g., "Sales Executive Overview")
3. Add charts:
   - Drag charts from left panel
   - Resize and position
4. Add filters:
   - Date range filter
   - Company filter (multi-select)
5. **Save**

### 3. Get Dashboard UUID

1. Open the dashboard in Superset
2. Check the URL: `https://superset.example.com/superset/dashboard/1234abcd-5678-...`
3. Copy the UUID: `1234abcd-5678-...`

## Embedding in Odoo

### Method 1: Direct URL Access

Users can access dashboards via:

```
https://your-odoo.com/superset/dashboard/<dashboard-uuid>
```

The module will:
1. Authenticate the user
2. Generate a guest token
3. Apply RLS filters
4. Embed the dashboard in an iframe

### Method 2: Create Token Records

For managed access:

1. Go to **Superset > Tokens**
2. Click **Create**
3. Fill in:
   - **Name**: Dashboard description
   - **Dashboard ID**: UUID from Superset
   - **User**: Target user (default: current user)
   - **Company**: Target company (default: current company)
   - **RLS Filter**: Optional custom filter
4. Click **Generate Token**

### Method 3: Custom Menu Items

Create menu items for specific dashboards:

```xml
<record id="menu_sales_dashboard" model="ir.ui.menu">
    <field name="name">Sales Dashboard</field>
    <field name="parent_id" ref="superset_connector.menu_superset_dashboards"/>
    <field name="action" ref="action_sales_dashboard"/>
    <field name="sequence">10</field>
</record>

<record id="action_sales_dashboard" model="ir.actions.act_url">
    <field name="name">Sales Dashboard</field>
    <field name="url">/superset/dashboard/your-dashboard-uuid</field>
    <field name="target">self</field>
</record>
```

## Row-Level Security (RLS)

### How RLS Works

1. **Odoo Side**:
   - User logs into Odoo
   - Requests dashboard
   - Module generates guest token with RLS clause

2. **Superset Side**:
   - Receives guest token with RLS rules
   - Applies SQL filters to all queries
   - Returns filtered data

3. **Database Side**:
   - RLS clause added to WHERE conditions
   - Only authorized data returned

### Custom RLS Filters

You can add custom RLS filters per token:

```python
# In Odoo Python code
token = self.env['superset.token'].create({
    'name': 'Department Dashboard',
    'dashboard_id': 'uuid-here',
    'rls_filter': 'department_id = 5 AND active = TRUE'
})
token.generate_token()
```

### Testing RLS

1. Create test users with different company access
2. Log in as each user
3. Access same dashboard
4. Verify data is filtered correctly

## Performance Optimization

### 1. Database Indexes

Indexes are created automatically by the SQL script:

```sql
CREATE INDEX idx_sale_order_date_company 
    ON sale_order(date_order, company_id) 
    WHERE state IN ('sale', 'done');
```

### 2. Materialized Views

For large datasets, use materialized views:

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW mv_sales_kpi_day AS 
SELECT * FROM vw_sales_kpi_day;

CREATE UNIQUE INDEX ON mv_sales_kpi_day (sale_date, company_id);

-- Refresh periodically (via cron)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_kpi_day;
```

### 3. Superset Caching

Configure Redis caching in `superset_config.py`:

```python
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/1'
}
```

### 4. Query Optimization

- Use EXPLAIN ANALYZE to identify slow queries
- Add appropriate indexes
- Limit data ranges in filters
- Pre-aggregate data in views

## Troubleshooting

### Token Generation Fails

**Symptoms**: Error when accessing dashboard

**Solutions**:
1. Check Superset URL in Odoo settings
2. Verify Superset credentials
3. Check network connectivity
4. Review Odoo logs: `odoo-bin --log-level=debug`

### Dashboard Not Loading

**Symptoms**: Blank iframe or error message

**Solutions**:
1. Check CSP headers (browser console)
2. Verify dashboard UUID is correct
3. Check Superset is accessible
4. Review browser console for errors

### RLS Not Working

**Symptoms**: Users see data from other companies

**Solutions**:
1. Verify RLS is enabled in Odoo settings
2. Check RLS rules in Superset
3. Verify user_company_access table is populated
4. Test SQL clause directly in Superset SQL Lab

### Performance Issues

**Symptoms**: Slow dashboard loading

**Solutions**:
1. Enable caching in Superset
2. Create materialized views for large datasets
3. Add database indexes
4. Optimize SQL queries in charts
5. Reduce number of charts per dashboard

### Authentication Errors

**Symptoms**: "Unauthorized" or "Invalid token" errors

**Solutions**:
1. Check token expiry time
2. Verify Superset credentials in Odoo
3. Check GUEST_TOKEN_JWT_SECRET in Superset config
4. Regenerate token manually

## Best Practices

1. **Security**:
   - Always use HTTPS in production
   - Enable RLS for multi-tenant deployments
   - Use strong passwords for database users
   - Rotate credentials regularly

2. **Performance**:
   - Use materialized views for large datasets
   - Enable caching in Superset
   - Create appropriate indexes
   - Limit dashboard complexity

3. **Maintenance**:
   - Monitor token usage
   - Clean up expired tokens regularly
   - Refresh materialized views on schedule
   - Review and optimize slow queries

4. **User Experience**:
   - Create dedicated menu items for dashboards
   - Add filters for date ranges and companies
   - Use consistent color schemes
   - Provide dashboard documentation

## Support

For issues and questions:

- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Documentation**: See module README.rst
- **Superset Docs**: https://superset.apache.org/docs/intro

---

**Last Updated**: 2025-10-26  
**Module Version**: 19.0.1.0.0  
**Odoo Version**: 19.0  
**Superset Version**: 3.0+
