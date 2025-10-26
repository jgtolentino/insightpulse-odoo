# BI Architecture: Odoo-Superset Integration

## Overview

This document describes the Business Intelligence architecture for the Odoo-Superset integration, covering data flow, security layers, and best practices for scalable analytics.

## Architecture Principles

### 1. Separation of Concerns

- **OLTP (Odoo Database)**: Transactional data, write-heavy
- **Analytics Layer**: Read-only views, optimized for reporting
- **BI Tool (Superset)**: Visualization and user interaction

### 2. Data Security

- Read-only database access for BI tools
- Row-level security enforcement
- Multi-company data isolation
- Audit logging

### 3. Performance

- Pre-aggregated views
- Strategic indexing
- Materialized views for heavy queries
- Caching at multiple layers

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Odoo Web UI  │  │   Superset   │  │  Mobile App  │         │
│  │  (Embedded)  │  │   Web UI     │  │   (Future)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │ Guest Token      │ OAuth/JWT        │ API Token
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────┐
│                     AUTHENTICATION LAYER                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Odoo superset_connector Module                            │ │
│  │  - Token generation                                        │ │
│  │  - User authentication                                     │ │
│  │  - RLS filter application                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Apache Superset Security Manager                          │ │
│  │  - Guest token validation                                  │ │
│  │  - Session management                                      │ │
│  │  - RLS rule enforcement                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ SQL Queries (with RLS)
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                        DATA ACCESS LAYER                          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL Connection Pool                                 │ │
│  │  - Read-only user: superset_readonly                        │ │
│  │  - Connection pooling                                       │ │
│  │  - Query timeout limits                                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                    ANALYTICS LAYER (VIEWS)                        │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │  Sales Views   │  │ Inventory Views│  │ Financial Views│    │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤    │
│  │ vw_sales_kpi   │  │ vw_stock_level │  │ vw_ar_aging    │    │
│  │ vw_product_    │  │ vw_inventory_  │  │ vw_monthly_    │    │
│  │   performance  │  │   turnover     │  │   revenue      │    │
│  │ vw_customer_   │  └────────────────┘  └────────────────┘    │
│  │   ltv          │                                             │
│  └────────────────┘  ┌────────────────┐                        │
│                      │   HR Views     │                        │
│                      ├────────────────┤                        │
│                      │ vw_employee_   │                        │
│                      │   headcount    │                        │
│                      └────────────────┘                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                    DATA STORAGE LAYER (OLTP)                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL Database (Odoo)                                 │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ sale_order   │  │ stock_quant  │  │ account_move │    │ │
│  │  │ sale_order_  │  │ stock_move   │  │ account_move_│    │ │
│  │  │   line       │  │ stock_        │  │   line       │    │ │
│  │  │              │  │   picking     │  │              │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐                       │ │
│  │  │ res_partner  │  │ hr_employee  │                       │ │
│  │  │ res_company  │  │ hr_department│                       │ │
│  │  └──────────────┘  └──────────────┘                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Embedded Dashboard Access Flow

```
User Request → Odoo Controller → Token Generation → Superset API → 
Guest Token Created → Dashboard Rendered → SQL Query → 
RLS Applied → Data Filtered → Results Returned → Visualization
```

### 2. Direct Superset Access Flow

```
User Login → Superset Auth → Dashboard Request → SQL Query → 
RLS Applied (if configured) → Data Retrieved → Visualization
```

## Layers Explained

### Presentation Layer

**Components:**
- Odoo Web Interface (embedded dashboards)
- Superset Native UI (direct access)
- Future: Mobile apps, public portals

**Responsibilities:**
- User interaction
- Dashboard rendering
- Filter management
- Drill-down navigation

### Authentication Layer

**Odoo Side:**
- User authentication via Odoo session
- Guest token generation for Superset
- RLS filter construction based on user permissions
- Token lifecycle management

**Superset Side:**
- Guest token validation
- Session creation
- Permission checking
- RLS rule application

### Data Access Layer

**Components:**
- PostgreSQL connection pool
- Read-only database user (`superset_readonly`)
- Query execution engine
- Connection management

**Security Features:**
- Read-only access prevents data modification
- Connection pooling limits resource usage
- Query timeouts prevent long-running queries
- SSL encryption for data in transit

### Analytics Layer

**Purpose:**
- Denormalize data for BI queries
- Pre-aggregate metrics
- Provide consistent naming
- Optimize query performance

**View Types:**

1. **Simple Views**: Direct table joins, minimal transformation
   - Example: `vw_customer_ltv`
   - Use: Real-time data, simple queries

2. **Aggregated Views**: Pre-aggregated metrics
   - Example: `vw_sales_kpi_day`
   - Use: KPI dashboards, trend analysis

3. **Materialized Views** (optional): Cached aggregations
   - Example: `mv_monthly_sales`
   - Use: Large datasets, historical reports

### Data Storage Layer (OLTP)

**Odoo Database:**
- Normalized relational structure
- Write-optimized
- Transaction-safe
- Odoo ORM managed

## Multi-Company Architecture

### Challenge

Odoo supports multiple companies in a single database. BI tools must:
1. Show only authorized data per user
2. Enable cross-company reporting for admins
3. Maintain data isolation for security

### Solution

```
┌──────────────────────────────────────────────────────────┐
│                    User Access Matrix                     │
├────────────────┬─────────────┬─────────────┬─────────────┤
│ User           │ Company A   │ Company B   │ Company C   │
├────────────────┼─────────────┼─────────────┼─────────────┤
│ user_a@co.com  │ ✓ Full      │ ✗ None      │ ✗ None      │
│ user_b@co.com  │ ✗ None      │ ✓ Full      │ ✗ None      │
│ admin@co.com   │ ✓ Full      │ ✓ Full      │ ✓ Full      │
│ manager@co.com │ ✓ Read-only │ ✓ Read-only │ ✗ None      │
└────────────────┴─────────────┴─────────────┴─────────────┘
```

### Implementation

**Database Table:**
```sql
CREATE TABLE user_company_access (
    user_email VARCHAR(255),
    company_id INTEGER,
    access_level VARCHAR(20),  -- 'full', 'read', 'none'
    UNIQUE(user_email, company_id)
);
```

**RLS Filter:**
```sql
company_id IN (
    SELECT company_id 
    FROM user_company_access 
    WHERE user_email = '{{ current_username() }}'
      AND access_level IN ('full', 'read')
)
```

## Data Mirroring (Optional Advanced Pattern)

For very large Odoo installations, consider data mirroring:

```
┌─────────────────────────────────────────────────────────┐
│                  Odoo OLTP Database                      │
│                  (Write Operations)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Logical Replication or CDC
                       │ (Debezium, pglogical, etc.)
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Analytics Database (Mirror)                 │
│              (Read-Only, Optimized for BI)               │
│                                                          │
│  - Separate from OLTP workload                          │
│  - Can have different indexing strategy                 │
│  - Can use columnar storage (TimescaleDB, Citus)        │
│  - No impact on Odoo performance                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Analytics queries
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Apache Superset                         │
└──────────────────────────────────────────────────────────┘
```

**When to Use Mirroring:**
- Odoo database > 100GB
- > 1000 concurrent users
- Complex analytics queries affecting OLTP performance
- Compliance requirements for data separation

## Security Architecture

### Defense in Depth

```
Layer 1: Network Security
├─ Firewall rules
├─ VPN for database access
└─ SSL/TLS encryption

Layer 2: Authentication
├─ Odoo session authentication
├─ Superset OAuth/JWT
└─ Guest token validation

Layer 3: Authorization
├─ Odoo user permissions
├─ Superset role-based access
└─ RLS SQL filters

Layer 4: Data Security
├─ Read-only database user
├─ Column-level permissions
└─ Audit logging

Layer 5: Application Security
├─ CSP headers
├─ CORS configuration
└─ XSS prevention
```

### RLS Implementation Details

**Superset RLS Table:**
```python
# superset/models/core.py
class RowLevelSecurityFilter(Model):
    __tablename__ = 'row_level_security_filters'
    
    name = Column(String(255))
    filter_type = Column(Enum('Regular', 'Base'))
    tables = relationship('SqlaTable', secondary='rls_filter_tables')
    clause = Column(Text)  # SQL WHERE clause
    group_key = Column(String(255))  # Optional user group
```

**Filter Application:**
```sql
-- Original query
SELECT * FROM vw_sales_kpi_day WHERE sale_date >= '2025-01-01'

-- With RLS applied
SELECT * FROM vw_sales_kpi_day 
WHERE sale_date >= '2025-01-01'
  AND (company_id IN (
      SELECT company_id FROM user_company_access 
      WHERE user_email = 'user@example.com'
  ))
```

## Performance Optimization Strategy

### 1. Database Level

**Indexes:**
```sql
-- Time-series queries
CREATE INDEX idx_sale_order_date_company 
    ON sale_order(date_order, company_id);

-- Foreign key lookups
CREATE INDEX idx_sale_order_line_product 
    ON sale_order_line(product_id);

-- Full-text search (if needed)
CREATE INDEX idx_partner_name_gin 
    ON res_partner USING gin(to_tsvector('english', name));
```

**Partitioning:**
```sql
-- For very large tables
CREATE TABLE sale_order_partitioned (
    LIKE sale_order INCLUDING ALL
) PARTITION BY RANGE (date_order);

CREATE TABLE sale_order_2024 
    PARTITION OF sale_order_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 2. View Level

**Materialized Views:**
```sql
CREATE MATERIALIZED VIEW mv_sales_monthly AS
SELECT 
    date_trunc('month', date_order) as month,
    company_id,
    SUM(amount_total) as revenue
FROM sale_order
WHERE state IN ('sale', 'done')
GROUP BY 1, 2;

-- Refresh schedule (via cron)
-- Daily: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_monthly;
```

### 3. Superset Level

**Caching Configuration:**
```python
# superset_config.py

# Metadata cache (dashboard structure)
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
}

# Data cache (query results)
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/1'
}

# Screenshot cache (dashboard thumbnails)
THUMBNAIL_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 604800,  # 1 week
    'CACHE_KEY_PREFIX': 'superset_thumb_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/2'
}
```

### 4. Query Optimization

**Best Practices:**
- Limit result sets (use TOP N, LIMIT)
- Filter early in the query
- Use appropriate JOIN types
- Avoid SELECT *
- Pre-aggregate in views

**Example:**
```sql
-- Bad: Large result set, late filtering
SELECT * FROM sale_order_line
WHERE order_id IN (
    SELECT id FROM sale_order WHERE date_order >= '2025-01-01'
);

-- Good: Early filtering, specific columns
SELECT 
    sol.product_id,
    SUM(sol.price_subtotal) as revenue
FROM sale_order so
JOIN sale_order_line sol ON sol.order_id = so.id
WHERE so.date_order >= '2025-01-01'
  AND so.state IN ('sale', 'done')
GROUP BY sol.product_id;
```

## Monitoring and Observability

### Metrics to Track

1. **Query Performance**
   - Average query time
   - Slow query count (> 5s)
   - Cache hit rate

2. **System Resources**
   - Database connections
   - CPU usage
   - Memory usage
   - Disk I/O

3. **User Activity**
   - Active users
   - Dashboard views
   - Token generation rate

### Logging

**Superset Logs:**
```python
# superset_config.py
import logging

# Query logging
QUERY_LOGGER = logging.getLogger('superset.query')
QUERY_LOGGER.setLevel(logging.INFO)

# Enable SQL query logging
SQLALCHEMY_ECHO = False  # Set True for debugging
```

**Odoo Logs:**
```python
# In Odoo module
import logging
_logger = logging.getLogger(__name__)

_logger.info(f"Generated token for user {user.login}")
_logger.warning(f"Token expired for dashboard {dashboard_id}")
_logger.error(f"Failed to generate token: {error}")
```

## Scalability Considerations

### Horizontal Scaling

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Superset 1  │  │  Superset 2  │  │  Superset 3  │
│  (Worker)    │  │  (Worker)    │  │  (Worker)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
               ┌─────────▼──────────┐
               │  Load Balancer     │
               │  (Nginx/HAProxy)   │
               └─────────┬──────────┘
                         │
               ┌─────────▼──────────┐
               │  Shared Redis      │
               │  (Cache & Celery)  │
               └─────────┬──────────┘
                         │
               ┌─────────▼──────────┐
               │  PostgreSQL        │
               │  (Read Replicas)   │
               └────────────────────┘
```

### Vertical Scaling

- Increase database server resources
- Add more Redis cache memory
- Optimize query performance
- Use connection pooling

## Disaster Recovery

### Backup Strategy

1. **Database Backups**
   - Daily full backups
   - Hourly incremental backups
   - 30-day retention

2. **Configuration Backups**
   - Superset metadata database
   - Odoo configuration
   - Analytics view definitions

3. **Recovery Testing**
   - Monthly recovery drills
   - Documented recovery procedures
   - RTO: 4 hours, RPO: 1 hour

## Compliance and Auditing

### Data Privacy (GDPR, CCPA)

- Customer data anonymization options
- Right to be forgotten implementation
- Data access audit logs
- Consent management

### Audit Logging

```sql
-- Audit table for sensitive data access
CREATE TABLE analytics_audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_email VARCHAR(255),
    dashboard_id VARCHAR(255),
    query_text TEXT,
    row_count INTEGER,
    execution_time FLOAT
);

-- Trigger on analytics views
CREATE OR REPLACE FUNCTION log_analytics_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO analytics_audit_log (user_email, dashboard_id, query_text)
    VALUES (current_user, TG_TABLE_NAME, current_query());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Best Practices Summary

1. **Security First**
   - Use read-only database users
   - Enable RLS
   - Implement CSP
   - Encrypt data in transit

2. **Performance Optimization**
   - Create appropriate indexes
   - Use materialized views for heavy queries
   - Enable caching at all layers
   - Monitor and optimize slow queries

3. **Maintainability**
   - Document all custom views
   - Version control SQL scripts
   - Automate view refresh
   - Regular performance reviews

4. **User Experience**
   - Consistent naming conventions
   - Clear documentation
   - Training materials
   - Responsive dashboards

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-26  
**Author**: InsightPulseAI Team
