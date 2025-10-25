# MindsDB integration

## Local run
```bash
docker compose -f docker/mindsdb.compose.yml up -d
open http://localhost:47334
```

## Connect to Postgres (example)
```sql
CREATE DATABASE IF NOT EXISTS odoo;
-- in MindsDB SQL console
CREATE DATABASE odoo_conn
WITH ENGINE = 'postgres',
PARAMETERS = {
  'user':'odoo','password':'change_me','host':'db','port':5432,'database':'odoo'
};
```

## Create agent over Odoo views
```sql
CREATE AGENT erp_agent USING
 data = {
   'tables': ['vw_sales_kpi_day','vw_vendor_spend_90d']
 };
```
