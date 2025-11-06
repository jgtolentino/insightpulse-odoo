# Odoo Docker Setup - OCA Enhanced (16 & 17)

Complete Docker setup for Odoo 16 (maximum parity) and Odoo 17 (modern UI) with OCA module integration.

## Quick Start

### Option 1: Odoo 16 (Recommended - Maximum Parity)

**Best for**: Production stability, maximum OCA module coverage, near-Enterprise/SaaS parity

```bash
# 1. Clone OCA repositories (16.0 branch)
cd /Users/tbwa/Documents/GitHub/insightpulse-odoo
./scripts/clone-oca-repos.sh 16.0

# 2. Start Odoo 16 with PostgreSQL 14
docker-compose -f docker-compose.odoo16.yml up -d

# 3. Wait for services to be healthy
docker-compose -f docker-compose.odoo16.yml ps

# 4. Access Odoo
open http://localhost:8069
```

**Database Credentials**:
- Database: `odoo16`
- Master Password: `admin123`
- Admin Email: `admin@example.com`
- Admin Password: `admin123`

---

### Option 2: Odoo 17 (Modern UI)

**Best for**: New projects, modern UI, future-proofing (with some OCA gaps)

```bash
# 1. Clone OCA repositories (17.0 branch)
cd /Users/tbwa/Documents/GitHub/insightpulse-odoo
./scripts/clone-oca-repos.sh 17.0

# 2. Start Odoo 17 with PostgreSQL 15
docker-compose -f docker-compose.odoo17.yml up -d

# 3. Wait for services to be healthy
docker-compose -f docker-compose.odoo17.yml ps

# 4. Access Odoo
open http://localhost:8070
```

**Database Credentials**:
- Database: `odoo17`
- Master Password: `admin123`
- Admin Email: `admin@example.com`
- Admin Password: `admin123`

---

## Architecture

### Odoo 16 Stack
- **Odoo**: `odoo:16.0` (port 8069)
- **PostgreSQL**: `postgres:14` (port 5432)
- **OCA Modules**: 18 repositories on `16.0` branch
- **Custom Addons**: `./addons` (ip_expense_mvp)

### Odoo 17 Stack
- **Odoo**: `odoo:17.0` (port 8070)
- **PostgreSQL**: `postgres:15` (port 5433)
- **OCA Modules**: 18 repositories on `17.0` branch
- **Custom Addons**: `./addons` (ip_expense_mvp)

---

## OCA Modules Included

### Accounting & Financial
- `account-financial-tools` - Enhanced financial reporting
- `account-invoice-reporting` - Advanced invoice reports
- `account-reconcile` - Payment reconciliation

### Sales & Purchase
- `sale-workflow` - Sales approval workflows
- `purchase-workflow` - Purchase policies

### Stock/Logistics
- `stock-logistics-warehouse` - Warehouse management
- `stock-logistics-tracking` - Lot/serial tracking
- `stock-logistics-barcode` - Barcode scanning

### HR & Expenses
- `hr` - HR enhancements
- `hr-expense` - Expense management
- `hr-timesheet` - Timesheet tracking

### Reporting & Analytics
- `reporting-engine` - Report engine
- `mis-builder` - Management reports

### Server Tools
- `server-tools` - Technical glue
- `server-ux` - UX improvements
- `web` - Web interface enhancements
- `queue` - Async job processing

### Project Management
- `project` - Project enhancements
- `timesheet` - Timesheet integration

---

## Common Operations

### Start Services
```bash
# Odoo 16
docker-compose -f docker-compose.odoo16.yml up -d

# Odoo 17
docker-compose -f docker-compose.odoo17.yml up -d
```

### Stop Services
```bash
# Odoo 16
docker-compose -f docker-compose.odoo16.yml down

# Odoo 17
docker-compose -f docker-compose.odoo17.yml down
```

### View Logs
```bash
# Odoo 16
docker-compose -f docker-compose.odoo16.yml logs -f odoo16

# Odoo 17
docker-compose -f docker-compose.odoo17.yml logs -f odoo17
```

### Restart Services
```bash
# Odoo 16
docker-compose -f docker-compose.odoo16.yml restart

# Odoo 17
docker-compose -f docker-compose.odoo17.yml restart
```

### Clean Installation (Nuclear Option)
```bash
# Odoo 16 - WARNING: Deletes all data
docker-compose -f docker-compose.odoo16.yml down -v
rm -rf oca/16.0
./scripts/clone-oca-repos.sh 16.0
docker-compose -f docker-compose.odoo16.yml up -d

# Odoo 17 - WARNING: Deletes all data
docker-compose -f docker-compose.odoo17.yml down -v
rm -rf oca/17.0
./scripts/clone-oca-repos.sh 17.0
docker-compose -f docker-compose.odoo17.yml up -d
```

---

## Module Installation

### Via Web UI (Recommended)
1. Go to Apps menu
2. Remove "Apps" filter to show all modules
3. Search for module name
4. Click "Install"

### Key Modules to Install
- `hr_expense` - Expense management
- `account` - Accounting
- `sale_management` - Sales
- `purchase` - Purchases
- `stock` - Inventory
- `project` - Projects

### Custom Module (ip_expense_mvp)
Your custom module is automatically available in `/mnt/extra-addons`.

1. Update module list: Apps → Update Apps List
2. Search for "IP Expense MVP"
3. Install

---

## Environment Variables

Create `.env` file for custom configuration:

```env
# PostgreSQL passwords
POSTGRES_PASSWORD=your_secure_password_here

# Odoo admin password
ADMIN_PASSWD=your_admin_password_here
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker-compose.odoo16.yml logs

# Check container status
docker-compose -f docker-compose.odoo16.yml ps
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker exec odoo16_postgres pg_isready -U odoo16

# Connect to database
docker exec -it odoo16_postgres psql -U odoo16 -d odoo16
```

### Module not showing in Apps
```bash
# Update module list via CLI
docker exec -it odoo16_app odoo -d odoo16 -u all --stop-after-init

# Or via web UI: Apps → Update Apps List
```

### Permission issues
```bash
# Fix file permissions
sudo chown -R $(id -u):$(id -g) ./addons ./oca
```

---

## Performance Tuning

Edit `config/odoo16.conf` or `config/odoo17.conf`:

```ini
# Increase workers for better performance
workers = 8

# Adjust memory limits
limit_memory_hard = 4294967296
limit_memory_soft = 3221225472

# Increase database connections
db_maxconn = 128
```

Then restart:
```bash
docker-compose -f docker-compose.odoo16.yml restart odoo16
```

---

## Backup & Restore

### Backup Database
```bash
# Odoo 16
docker exec odoo16_postgres pg_dump -U odoo16 odoo16 > backup_odoo16_$(date +%Y%m%d).sql

# Odoo 17
docker exec odoo17_postgres pg_dump -U odoo17 odoo17 > backup_odoo17_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# Odoo 16
docker exec -i odoo16_postgres psql -U odoo16 odoo16 < backup_odoo16_20250106.sql

# Odoo 17
docker exec -i odoo17_postgres psql -U odoo17 odoo17 < backup_odoo17_20250106.sql
```

---

## Migration Path

### From Remote Server to Docker

**Current**: Odoo 16 running at erp.insightpulseai.net (bare-metal)

**Migration Options**:

1. **Database Export/Import**:
```bash
# Export from remote
ssh root@165.227.10.178 'sudo -u postgres pg_dump -U odoo16 odoo' > remote_backup.sql

# Import to Docker
docker exec -i odoo16_postgres psql -U odoo16 odoo16 < remote_backup.sql
```

2. **Filestore Migration**:
```bash
# Export filestore from remote
ssh root@165.227.10.178 'tar czf /tmp/filestore.tar.gz /var/lib/odoo/.local/share/Odoo/filestore/odoo'
scp root@165.227.10.178:/tmp/filestore.tar.gz .

# Import to Docker
docker cp filestore.tar.gz odoo16_app:/var/lib/odoo/
docker exec odoo16_app tar xzf /var/lib/odoo/filestore.tar.gz -C /var/lib/odoo/
```

---

## Next Steps

1. ✅ Choose version (16 or 17)
2. ✅ Clone OCA repositories
3. ✅ Start Docker stack
4. ⏳ Install required modules via web UI
5. ⏳ Deploy custom `ip_expense_mvp` module
6. ⏳ Configure OCR integration
7. ⏳ Test expense automation

---

## Support

- **Docker Hub**: https://hub.docker.com/_/odoo
- **OCA GitHub**: https://github.com/OCA
- **Odoo Documentation**: https://www.odoo.com/documentation/16.0
