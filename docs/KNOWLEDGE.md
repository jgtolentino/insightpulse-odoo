# Knowledge Base: Odoo Development Agent

## Overview

This knowledge base documents the expertise, design principles, and implementation patterns for building robust data connectors between Odoo ERP and Business Intelligence tools, with a primary focus on Apache Superset integration.

## Core Competencies

### 1. Odoo Architecture & Development

#### Odoo Framework Understanding
- **ORM (Object-Relational Mapping)**: Deep understanding of Odoo's model layer, including:
  - Model inheritance patterns: `_inherit`, `_inherits`, delegation
  - Field types and their database representations
  - Computed fields, related fields, and constraints
  - Search domains and filtering
  
- **View Layer**: 
  - XML view definitions (form, tree, kanban, pivot, graph, calendar)
  - QWeb templating for reports and frontend
  - Client-side actions and widgets
  
- **Business Logic**:
  - Python methods and decorators (`@api.model`, `@api.depends`, etc.)
  - Recordsets and their operations
  - Transaction handling and security

#### Module Development Best Practices
1. **Module Structure**:
   ```
   my_module/
   ├── __init__.py
   ├── __manifest__.py
   ├── models/
   │   ├── __init__.py
   │   └── *.py
   ├── views/
   │   └── *.xml
   ├── security/
   │   ├── ir.model.access.csv
   │   └── security.xml
   ├── data/
   ├── static/
   └── tests/
   ```

2. **Dependency Management**:
   - Minimize external dependencies
   - Use OCA (Odoo Community Association) modules where possible
   - Document all dependencies in `__manifest__.py`

3. **Version Compatibility**:
   - Target Odoo 19.0 (current repository version)
   - Follow version-specific API changes
   - Use migration scripts when needed

### 2. Data Connector Design Principles

#### Connector Architecture Patterns

**Pattern 1: Direct Database Access (Read-Only)**
```python
# For BI tools that support PostgreSQL directly
# Advantages: Real-time data, simple setup
# Disadvantages: Requires database credentials, limited to SQL queries

CREATE VIEW vw_sales_kpi_day AS
SELECT 
    date_trunc('day', so.date_order) as order_date,
    so.company_id,
    COUNT(so.id) as order_count,
    SUM(so.amount_total) as total_revenue,
    AVG(so.amount_total) as avg_order_value
FROM sale_order so
WHERE so.state IN ('sale', 'done')
GROUP BY date_trunc('day', so.date_order), so.company_id;
```

**Pattern 2: JSON-RPC API Integration**
```python
# For tools requiring API-based access
# Advantages: Respects Odoo security, works remotely
# Disadvantages: Slower than direct DB, requires authentication

import xmlrpc.client

def odoo_rpc_call(url, db, username, password, model, method, args=None, kwargs=None):
    """
    Execute RPC call to Odoo
    
    Args:
        url: Odoo server URL (e.g., 'http://localhost:8069')
        db: Database name
        username: User login
        password: API key or password
        model: Model name (e.g., 'sale.order')
        method: Method to call (e.g., 'search_read')
        args: Positional arguments
        kwargs: Keyword arguments
    """
    args = args or []
    kwargs = kwargs or {}
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        raise ValueError("Authentication failed")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return models.execute_kw(
        db, uid, password,
        model, method,
        args, kwargs
    )
```

**Pattern 3: REST API with Custom Endpoints**
```python
# For complex integrations requiring custom logic
# Advantages: Full control, can aggregate/transform data
# Disadvantages: Requires custom Odoo module

from odoo import http
from odoo.http import request

class BIConnectorController(http.Controller):
    
    @http.route('/api/bi/sales_metrics', type='json', auth='api_key', methods=['POST'])
    def sales_metrics(self, start_date, end_date, company_ids=None):
        """
        Export sales metrics for BI tools
        """
        domain = [
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date),
            ('state', 'in', ['sale', 'done'])
        ]
        
        if company_ids:
            domain.append(('company_id', 'in', company_ids))
        
        orders = request.env['sale.order'].search(domain)
        
        return {
            'total_revenue': sum(orders.mapped('amount_total')),
            'order_count': len(orders),
            'avg_order_value': sum(orders.mapped('amount_total')) / len(orders) if orders else 0,
            'orders': orders.read(['id', 'name', 'date_order', 'amount_total', 'state'])
        }
```

#### Data Modeling for Analytics

**Star Schema Design**:
```sql
-- Fact Table: Sales Transactions
CREATE VIEW fact_sales AS
SELECT 
    so.id as sale_id,
    so.date_order::date as date_id,
    so.partner_id as customer_id,
    so.user_id as salesperson_id,
    so.company_id,
    sol.product_id,
    sol.product_uom_qty as quantity,
    sol.price_unit,
    sol.price_subtotal,
    sol.price_total,
    so.state
FROM sale_order_line sol
JOIN sale_order so ON sol.order_id = so.id;

-- Dimension: Date
CREATE VIEW dim_date AS
SELECT DISTINCT
    date_order::date as date_id,
    EXTRACT(YEAR FROM date_order) as year,
    EXTRACT(MONTH FROM date_order) as month,
    EXTRACT(DAY FROM date_order) as day,
    EXTRACT(QUARTER FROM date_order) as quarter,
    to_char(date_order, 'Day') as day_name,
    to_char(date_order, 'Month') as month_name
FROM sale_order;

-- Dimension: Customer
CREATE VIEW dim_customer AS
SELECT 
    id as customer_id,
    name,
    country_id,
    industry_id,
    is_company,
    parent_id
FROM res_partner
WHERE customer_rank > 0;
```

### 3. Apache Superset Integration

#### Setup and Configuration

**1. Database Connection**:
```python
# SQLAlchemy URI for PostgreSQL connection
postgresql+psycopg2://odoo_readonly:password@db-host:5432/odoo
```

**2. Dataset Configuration**:
- Create datasets from Odoo views (not direct tables)
- Use virtual datasets for complex queries
- Enable caching for performance

**3. Dashboard Design Principles**:
- **Clarity**: One metric per visualization
- **Context**: Always include time ranges and filters
- **Actionability**: Link to Odoo records where possible
- **Performance**: Pre-aggregate data in views

#### Row-Level Security (RLS) Implementation

```python
# Superset SQL filter for multi-company access
# This ensures users only see data for their authorized companies

# In Superset Dataset Settings > Row Level Security:
company_id IN (
    SELECT company_id 
    FROM user_company_access 
    WHERE user_email = '{{ current_username() }}'
)
```

#### Sample Dashboard Components

**1. Sales Overview Dashboard**:
```yaml
Dashboard: Executive Sales Overview
Filters:
  - Date Range (last 30 days default)
  - Company (multi-select)
  - Sales Team

Charts:
  - KPI Cards:
      - Total Revenue (vs. previous period)
      - Order Count
      - Average Order Value
      - Conversion Rate
  
  - Line Chart: Revenue Trend (daily/weekly/monthly)
  - Bar Chart: Top 10 Products by Revenue
  - Pie Chart: Revenue by Sales Team
  - Table: Recent Orders (Top 20)
  - Heatmap: Sales by Day of Week & Hour
```

**2. Financial Dashboard**:
```yaml
Dashboard: Financial Performance
Filters:
  - Fiscal Year/Quarter
  - Company
  - Account Type

Charts:
  - KPI Cards:
      - Cash Flow
      - Accounts Receivable
      - Accounts Payable
      - Profit Margin
  
  - Waterfall Chart: Income Statement
  - Funnel Chart: Sales Pipeline
  - Pivot Table: P&L by Department
  - Line Chart: Cash Flow Forecast
```

#### Advanced Superset Features

**Custom SQL Metrics**:
```sql
-- Month-over-Month Growth
SELECT 
    date_trunc('month', date_order) as month,
    SUM(amount_total) as current_month,
    LAG(SUM(amount_total)) OVER (ORDER BY date_trunc('month', date_order)) as previous_month,
    ((SUM(amount_total) - LAG(SUM(amount_total)) OVER (ORDER BY date_trunc('month', date_order))) 
     / LAG(SUM(amount_total)) OVER (ORDER BY date_trunc('month', date_order)) * 100) as growth_pct
FROM sale_order
WHERE state IN ('sale', 'done')
GROUP BY date_trunc('month', date_order);
```

**Embedded Analytics**:
```python
# Odoo module for embedded Superset dashboards
from odoo import models, fields, api

class SupersetDashboard(models.Model):
    _name = 'superset.dashboard'
    _description = 'Superset Dashboard Embedding'
    
    name = fields.Char(required=True)
    dashboard_id = fields.Char(required=True)
    allowed_group_ids = fields.Many2many('res.groups', string='Allowed Groups')
    embed_url = fields.Char(compute='_compute_embed_url')
    
    @api.depends('dashboard_id')
    def _compute_embed_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('superset.base_url')
        for record in self:
            record.embed_url = f"{base_url}/superset/dashboard/{record.dashboard_id}/"
```

### 4. Security Best Practices

#### Database Access Security
1. **Read-Only User**: Create dedicated DB user with SELECT-only permissions
   ```sql
   CREATE USER odoo_readonly WITH PASSWORD 'strong_password';
   GRANT CONNECT ON DATABASE odoo TO odoo_readonly;
   GRANT USAGE ON SCHEMA public TO odoo_readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO odoo_readonly;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO odoo_readonly;
   ```

2. **Network Security**: Restrict database access by IP
   ```
   # pg_hba.conf
   host    odoo    odoo_readonly    10.0.1.0/24    md5
   ```

3. **Credential Management**: Use environment variables or secret managers
   ```bash
   export SUPERSET_DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id odoo/superset --query SecretString --output text)
   ```

#### API Security
1. **API Keys**: Use Odoo API keys instead of passwords
2. **Rate Limiting**: Implement rate limiting on custom endpoints
3. **HTTPS Only**: Force SSL for all API communications
4. **CORS Configuration**: Properly configure allowed origins

### 5. Performance Optimization

#### Database Query Optimization
```sql
-- Create indexes on frequently filtered columns
CREATE INDEX idx_sale_order_date_order ON sale_order(date_order);
CREATE INDEX idx_sale_order_company_state ON sale_order(company_id, state);
CREATE INDEX idx_sale_order_line_product ON sale_order_line(product_id);

-- Materialized views for heavy aggregations
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT 
    date_trunc('day', so.date_order) as sale_date,
    so.company_id,
    COUNT(*) as order_count,
    SUM(so.amount_total) as total_revenue
FROM sale_order so
WHERE so.state IN ('sale', 'done')
GROUP BY date_trunc('day', so.date_order), so.company_id;

-- Refresh materialized view (run via cron)
REFRESH MATERIALIZED VIEW mv_daily_sales;
```

#### Caching Strategy
1. **Superset Cache**: Configure Redis for query caching
2. **View Materialization**: Use materialized views for complex aggregations
3. **CDN**: Use CDN for static dashboard assets

### 6. Monitoring and Troubleshooting

#### Logging
```python
import logging
_logger = logging.getLogger(__name__)

def fetch_data_for_bi(self):
    _logger.info('Starting BI data fetch: %s records', len(self))
    try:
        # Data processing
        pass
    except Exception as e:
        _logger.error('BI data fetch failed: %s', str(e), exc_info=True)
        raise
```

#### Metrics to Monitor
- Query execution time
- Data freshness (last update timestamp)
- API response times
- Dashboard load times
- User access patterns
- Error rates

#### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow dashboard loading | Large dataset, no indexes | Add indexes, use materialized views, implement pagination |
| Authentication failures | Expired credentials, wrong permissions | Verify API keys, check user permissions in Odoo |
| Missing data | Filters too restrictive, RLS issues | Check filter values, verify RLS configuration |
| Permission denied | Database user lacks privileges | Grant necessary permissions to readonly user |
| Stale data | Cache not invalidated | Clear Superset cache, refresh materialized views |

## Implementation Checklist

### Odoo Side
- [ ] Create read-only database user
- [ ] Create analytical views (fact and dimension tables)
- [ ] Add indexes for common query patterns
- [ ] Set up materialized views for aggregations
- [ ] Configure scheduled actions for view refresh
- [ ] Implement custom API endpoints (if needed)
- [ ] Set up API key authentication
- [ ] Configure CORS for BI tool access
- [ ] Document data model and business logic

### Superset Side
- [ ] Install and configure Superset
- [ ] Set up database connection with read-only user
- [ ] Create datasets from Odoo views
- [ ] Configure Row-Level Security rules
- [ ] Design dashboard layouts
- [ ] Create visualizations following best practices
- [ ] Set up caching (Redis)
- [ ] Configure user authentication (LDAP/OAuth)
- [ ] Implement embedded analytics (if needed)
- [ ] Set up monitoring and alerts

### DevOps
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Implement backup strategy
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Document deployment procedures
- [ ] Create disaster recovery plan
- [ ] Implement CI/CD for dashboard deployments

## Extension Points

### Adding New BI Tools

To add support for new BI tools (e.g., Metabase, Tableau, Power BI):

1. **Evaluate Connection Methods**:
   - Direct database connection (preferred for simplicity)
   - REST API integration
   - ODBC/JDBC drivers

2. **Create Tool-Specific Views**:
   ```sql
   -- Example: Tableau-optimized view
   CREATE VIEW tableau_sales_data AS
   SELECT 
       so.id::text as "Sale Order ID",
       so.name as "Order Number",
       so.date_order as "Order Date",
       -- Tableau prefers text for categorical data
       c.name::text as "Customer",
       p.name::text as "Product",
       -- Use explicit type casting
       sol.product_uom_qty::numeric as "Quantity",
       sol.price_total::numeric as "Total"
   FROM sale_order so
   JOIN sale_order_line sol ON sol.order_id = so.id
   JOIN res_partner c ON so.partner_id = c.id
   JOIN product_product pp ON sol.product_id = pp.id
   JOIN product_template p ON pp.product_tmpl_id = p.id;
   ```

3. **Document Integration Steps**:
   - Connection parameters
   - Authentication setup
   - Security considerations
   - Performance optimization tips

### Custom Data Transformations

For complex business logic not easily expressed in SQL:

```python
# Odoo scheduled action for ETL
from odoo import models, api

class BIDataETL(models.Model):
    _name = 'bi.data.etl'
    _description = 'BI Data ETL Process'
    
    @api.model
    def run_daily_aggregation(self):
        """
        Daily ETL job to prepare data for BI tools
        Schedule this via Odoo cron
        """
        self._aggregate_sales_data()
        self._calculate_kpis()
        self._refresh_materialized_views()
    
    def _aggregate_sales_data(self):
        # Complex business logic here
        pass
```

## References

- [Odoo Developer Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

## Changelog

- **2025-10-26**: Initial knowledge base creation
- Focus areas: Odoo 19.0, Superset integration, security best practices
