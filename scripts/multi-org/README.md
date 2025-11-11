# Multi-Organization Database Setup

Scripts for creating and seeding multiple Philippine organization databases in Odoo.

---

## Overview

Creates **8 separate databases** for Philippine Finance SSC agencies:

| Database | Agency | TIN |
|----------|--------|-----|
| `db_rim` | Refugee International Mission | 123-456-789-000 |
| `db_ckvc` | CKVC Foundation | 234-567-890-000 |
| `db_bom` | BOM Organization | 345-678-901-000 |
| `db_jpal` | J-PAL Philippines | 456-789-012-000 |
| `db_jli` | JLI Institute | 567-890-123-000 |
| `db_jap` | JAP Association | 678-901-234-000 |
| `db_las` | LAS Services | 789-012-345-000 |
| `db_rmqb` | RMQB Corporation | 890-123-456-000 |

---

## Prerequisites

1. **Docker Compose running**
   ```bash
   docker-compose up -d
   ```

2. **Environment variable**
   ```bash
   export ODOO_ADMIN_PASSWORD=admin
   ```

3. **Python dependencies** (for seeding)
   ```bash
   pip install odoorpc
   ```

---

## Quick Start

### 1. Create Databases

```bash
cd scripts/multi-org
./create-multi-org-dbs.sh
```

**What it does**:
- Creates 8 PostgreSQL databases
- Initializes each with Odoo base modules
- Installs Philippine localization (`l10n_ph`)

**Expected output**:
```
[INFO] Creating database: db_rim
✓ Database db_rim created
[INFO] Initializing Odoo in database: db_rim
✓ Odoo initialized for db_rim
...
✓ Multi-Org Database Setup Complete!
```

**Time**: ~10 minutes

---

### 2. Seed Demo Data

```bash
python seed-demo-data.py
```

**What it does**:
- Configures each company with agency details
- Creates 5 sample customers per organization
- Creates 5 sample vendors per organization
- Creates 5 sample products/services
- Generates 100 GL transactions (invoices) per organization

**Expected output**:
```
Seeding agency: Refugee International Mission (RIM)
✓ Connected to database: db_rim
✓ Company configured: Refugee International Mission
✓ Created 5 customers
✓ Created 5 vendors
✓ Created 5 products
✓ Created 100 GL transactions
✓ Successfully seeded Refugee International Mission
...
✓ All agencies seeded successfully!
```

**Time**: ~15 minutes (all 8 agencies)

---

### 3. Verify Installation

```bash
# List databases
docker-compose exec postgres psql -U odoo -c "\l" | grep db_

# Check transaction count for one agency
docker-compose exec postgres psql -U odoo -d db_rim -c "SELECT COUNT(*) FROM account_move;"
```

Expected: 100+ transactions per database

---

## Usage

### Seed All Agencies

```bash
python seed-demo-data.py
```

### Seed Specific Agency

```bash
python seed-demo-data.py --agency rim
python seed-demo-data.py --agency ckvc
```

### Access Databases

1. Open: http://localhost:8069
2. Select database from dropdown
3. Login: `admin` / `admin` (or your `ODOO_ADMIN_PASSWORD`)

---

## Configuration

### Agency Details

Edit `agencies.json` to customize agency information:

```json
{
  "code": "rim",
  "name": "Refugee International Mission",
  "tin": "123-456-789-000",
  "address": "Quezon City, Metro Manila, Philippines",
  "email": "info@rim.org.ph",
  "phone": "+63 2 8123 4567"
}
```

### Sample Data Counts

Edit `seed-demo-data.py` to adjust:

```python
create_customers(odoo, count=5)       # Number of customers
create_vendors(odoo, count=5)         # Number of vendors
create_gl_transactions(odoo, count=100)  # Number of transactions
```

---

## Troubleshooting

### Error: "PostgreSQL container not running"

**Solution**:
```bash
cd /path/to/insightpulse-odoo
docker-compose up -d
```

### Error: "Database already exists"

**Solution**: Script will skip existing databases. To recreate:
```bash
docker-compose exec postgres psql -U odoo -c "DROP DATABASE db_rim;"
./create-multi-org-dbs.sh
```

### Error: "Failed to connect to database"

**Solution**: Check Odoo is accessible:
```bash
curl http://localhost:8069/web/health
```

If not, restart:
```bash
docker-compose restart odoo
```

### Error: "odoorpc not installed"

**Solution**:
```bash
pip install odoorpc
```

---

## Architecture

### Multi-Database vs Single Database

**We use multi-database (8 separate databases) because**:

✅ **Better data isolation** - Each agency's data is completely separated
✅ **BIR compliance** - Easier per-entity reporting and auditing
✅ **Security** - One compromised database doesn't affect others
✅ **Performance** - Smaller databases, faster queries
✅ **Backup/restore** - Can backup/restore individual agencies

**Trade-offs**:
❌ More complex backup procedures
❌ Cross-database queries require custom SQL
❌ Higher disk usage

### Consolidation Approach

For consolidated financial reporting across all 8 agencies, we use:

1. **Python scripts** - Query all 8 databases and merge results
2. **Superset dashboards** - Connect to multiple data sources
3. **SQL views** - Create views in a separate "consolidation" database

See: `/scripts/multi-org/consolidate-financials.py` (to be implemented in M2)

---

## Next Steps

After seeding:

1. **Install BIR Compliance Module**
   ```bash
   # In Odoo UI for each database:
   # Apps > Update Apps List > Search "BIR" > Install
   ```

2. **Generate Sample BIR Forms**
   ```bash
   # In Odoo UI:
   # BIR Compliance > Tax Forms > 1601-C > Create
   # Month: 1, Year: 2025
   # Generate XML > Validate
   ```

3. **Test Consolidation** (M2)
   ```bash
   python consolidate-financials.py --period 2025-01
   ```

---

## Related Documentation

- [PRD Implementation Roadmap](../../docs/PRD_IMPLEMENTATION_ROADMAP.md)
- [BIR Compliance Module](../../odoo_addons/ipai_bir_compliance/README.md)
- [Docker Setup](../../README-DOCKER-SETUP.md)

---

**Author**: InsightPulse AI
**Last Updated**: 2025-11-11
**License**: LGPL-3
