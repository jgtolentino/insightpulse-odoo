# Superset Service - T&E MVP Integration

## Overview

Apache Superset is a modern, open-source data exploration and visualization platform. This setup pre-loads official example datasets and dashboards, giving you a turnkey demo environment while you wire up real T&E data.

## Quick Start

### Start Superset

```bash
# From repo root
docker compose -f services/superset/docker-compose.superset.yml up -d
```

### Access Superset

```
URL: http://localhost:8088
Username: admin
Password: admin
```

**IMPORTANT**: Change the admin password in production! Update `services/superset/.env.superset`.

### What's Pre-loaded

1. **Official Example Datasets**:
   - World Bank indicators
   - Flight data
   - Birth names
   - Random time series
   - ...and more!

2. **Example Dashboards**:
   - World's Bank Data dashboard (renamed to **"T&E MVP — Examples Seed"**)
   - Multiple visualization types (charts, maps, tables)
   - Sample filters and drill-downs

3. **Published Demo Dashboard**:
   - **"T&E MVP — Examples Seed"** is ready to use
   - Tagged with: MVP, Examples, Demo
   - Shows Superset capabilities out-of-the-box

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│ services/superset/                               │
│ ├── docker-compose.superset.yml                  │
│ │   ├── superset (main service)                  │
│ │   └── superset-init (one-time setup)           │
│ ├── .env.superset (admin credentials)            │
│ ├── init.sh (setup script)                       │
│ ├── publish_examples.py (dashboard publisher)    │
│ └── README.md (this file)                        │
└──────────────────────────────────────────────────┘
```

### Containers

1. **superset**: Main Superset application
   - Port: 8088
   - Volume: `superset_home` (persistent storage)
   - Restart: unless-stopped

2. **superset-init**: One-time initialization container
   - Creates admin user
   - Loads official examples via `superset load_examples`
   - Initializes roles & permissions
   - Publishes demo dashboard
   - Auto-exits after setup

---

## Next Steps

### 1. Connect to Odoo Database

Once your Odoo expense MVP is running, connect Superset to the PostgreSQL database:

1. **Superset UI → Settings → Database Connections → + Database**
2. **Select**: PostgreSQL
3. **Configuration**:
   ```
   Host: db (Docker network) or localhost:5432
   Database: odoo
   Username: odoo
   Password: (from your .env)
   ```

### 2. Create T&E Datasets

Create datasets from these Odoo tables:
- `hr_expense`: Expenses with OCR data
- `ip_cash_advance`: Cash advances
- `ip_travel_request`: Travel requests
- `ip_liquidation`: Liquidation records

**Example SQL Dataset**:
```sql
SELECT
  e.name AS expense_name,
  e.employee_id,
  e.total_amount,
  e.date,
  e.ocr_merchant,
  e.ocr_confidence,
  e.state,
  ca.name AS cash_advance,
  ca.amount AS advance_amount
FROM hr_expense e
LEFT JOIN ip_cash_advance ca ON e.cash_advance_id = ca.id
WHERE e.state IN ('approved', 'done')
```

### 3. Build T&E Dashboards

**Suggested Charts**:
1. **Expense Trends**: Line chart (time series) of total expenses by month
2. **Top Merchants**: Bar chart of spending by `ocr_merchant`
3. **OCR Accuracy**: Gauge showing average `ocr_confidence`
4. **Cash Advance Status**: Pie chart of cash advance states
5. **Employee Spending**: Table with employee name, total amount, count
6. **Pending Approvals**: Big number KPI showing count of pending expenses
7. **Liquidation Status**: Sankey diagram showing cash advance → expenses → liquidation flow

### 4. Export & Version Control

Once you've built your T&E dashboards:

**Export Assets**:
```bash
# Export dashboard as ZIP (includes all dependencies)
curl -X POST \
  http://localhost:8088/api/v1/dashboard/export/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"dashboard_ids": [1,2,3]}' \
  -o te_dashboards.zip
```

**Import Assets**:
```bash
# Import dashboard ZIP (for CI/CD or new environments)
curl -X POST \
  http://localhost:8088/api/v1/assets/import/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "bundle=@te_dashboards.zip"
```

---

## Configuration

### Environment Variables

Edit `services/superset/.env.superset`:

```env
# Secret key for session encryption (REQUIRED - change in production!)
SUPERSET_SECRET_KEY=your-very-long-random-string-here

# Admin user credentials
ADMIN_USERNAME=admin
ADMIN_FIRSTNAME=Superset
ADMIN_LASTNAME=Admin
ADMIN_EMAIL=admin@insightpulseai.net
ADMIN_PASSWORD=your-secure-password-here
```

**Generate Secret Key**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(42))"
```

### Production Hardening

1. **Change Admin Password**: Update `.env.superset` before deployment
2. **Secret Key**: Generate a strong random key (see above)
3. **Database**: Use external PostgreSQL for metadata (not SQLite)
4. **Redis**: Add Redis for caching and async queries
5. **SSL**: Enable HTTPS via reverse proxy (Caddy/nginx)
6. **Auth**: Integrate with OAuth/LDAP/SAML

---

## Troubleshooting

### Container Fails to Start

**Check logs**:
```bash
docker compose -f services/superset/docker-compose.superset.yml logs superset
```

**Common issues**:
- Port 8088 already in use: Change port mapping in `docker-compose.superset.yml`
- Volume permission errors: Check Docker volume permissions

### Admin Login Fails

**Reset admin password**:
```bash
docker exec -it superset superset fab reset-password \
  --username admin \
  --password NewPassword123
```

### Examples Not Loading

**Manually trigger load**:
```bash
docker exec -it superset superset load_examples
docker exec -it superset superset init
```

### Dashboard Not Published

**Manually publish via API**:
```bash
# Get access token
TOKEN=$(curl -X POST \
  http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin","provider":"db","refresh":true}' \
  | jq -r '.access_token')

# Publish dashboard (ID = 1)
curl -X PUT \
  http://localhost:8088/api/v1/dashboard/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"published":true}'
```

---

## Integration with T&E MVP

### OCR Accuracy Dashboard

**Dataset SQL**:
```sql
SELECT
  date_trunc('day', create_date) AS date,
  AVG(ocr_confidence) AS avg_confidence,
  COUNT(*) AS total_receipts,
  COUNT(*) FILTER (WHERE ocr_status = 'parsed') AS successful,
  COUNT(*) FILTER (WHERE ocr_status = 'error') AS failed
FROM hr_expense
WHERE ocr_status IS NOT NULL
GROUP BY date_trunc('day', create_date)
ORDER BY date DESC
```

**Charts**:
1. Line chart: `avg_confidence` over time
2. Area chart: `total_receipts`, `successful`, `failed` stacked
3. Big number: Latest `avg_confidence`

### Cash Advance Utilization

**Dataset SQL**:
```sql
SELECT
  ca.name,
  ca.employee_id,
  ca.amount AS advance_amount,
  COALESCE(SUM(e.total_amount), 0) AS spent_amount,
  ca.amount - COALESCE(SUM(e.total_amount), 0) AS balance,
  ca.state
FROM ip_cash_advance ca
LEFT JOIN hr_expense e ON e.cash_advance_id = ca.id
GROUP BY ca.id, ca.name, ca.employee_id, ca.amount, ca.state
HAVING ca.state IN ('approved', 'released')
```

**Charts**:
1. Bar chart: `balance` by employee (negative = overspent)
2. Table: Employee, Advance, Spent, Balance, State
3. Gauge: `SUM(balance) / SUM(advance_amount)` (utilization %)

---

## Resources

- **Official Docs**: https://superset.apache.org/docs/
- **API Reference**: https://superset.apache.org/docs/api/
- **Docker Deployment**: https://superset.apache.org/docs/installation/docker-compose
- **Example Datasets**: Built into `superset load_examples` command

---

## Maintenance

### Upgrade Superset

```bash
# Pull latest image
docker pull apache/superset:latest

# Restart services
docker compose -f services/superset/docker-compose.superset.yml down
docker compose -f services/superset/docker-compose.superset.yml up -d

# Run database migrations
docker exec -it superset superset db upgrade
```

### Backup Metadata

```bash
# Backup Superset metadata DB
docker exec superset sh -c 'tar czf - /app/superset_home' > superset_backup.tar.gz
```

### Restore Metadata

```bash
# Restore Superset metadata DB
docker exec -i superset sh -c 'tar xzf - -C /' < superset_backup.tar.gz
docker compose -f services/superset/docker-compose.superset.yml restart superset
```

---

## License

Apache Superset is licensed under Apache 2.0.

InsightPulse T&E MVP integration is licensed under LGPL-3.

---

## Support

**Issues**: Report at [github.com/jgtolentino/insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)

**Superset Community**: https://github.com/apache/superset/discussions
