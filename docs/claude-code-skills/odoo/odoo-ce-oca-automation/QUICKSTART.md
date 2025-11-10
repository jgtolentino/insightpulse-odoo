# Quick Start: Odoo 18 CE + OCA Automation

Get started with Odoo 18 Community Edition + OCA modules in minutes.

## 🚀 Fastest Path

### One Command Setup

```bash
python3 docs/claude-code-skills/odoo/odoo-ce-oca-automation/scripts/init-odoo18-project.py \
  --name my-company-erp \
  --features accounting,helpdesk,project,hr \
  --domain mycompany.com \
  --provider digitalocean

cd my-company-erp
docker-compose up -d
```

**That's it!** Open http://localhost:8069 and start using Odoo 18 CE.

---

## 📋 Step-by-Step Guide

### 1. Initialize Project (2 minutes)

```bash
# Create new Odoo 18 project with your desired features
python3 docs/claude-code-skills/odoo/odoo-ce-oca-automation/scripts/init-odoo18-project.py \
  --name erp-production \
  --features accounting,helpdesk,project \
  --domain insightpulseai.net

# Navigate to project
cd erp-production
```

**What this creates**:
- ✅ Complete OCA-compliant repo structure
- ✅ Docker Compose for local development
- ✅ OCA modules vendoring configuration
- ✅ CI/CD pipelines (GitHub Actions)
- ✅ Terraform for DigitalOcean
- ✅ Pre-commit hooks and linters
- ✅ Documentation

### 2. Vendor OCA Modules (3 minutes)

```bash
# Install vendoring script dependencies
pip3 install requests pyyaml

# Vendor OCA modules
python3 ../scripts/vendor_oca_enhanced.py \
  --repos addons/oca/repos.yaml \
  --target addons/oca \
  --odoo-version 18.0 \
  --validate
```

**What this does**:
- Downloads OCA modules from GitHub
- Pins specific commits for stability
- Validates Odoo 18.0 compatibility
- Creates requirements.txt

### 3. Start Development Environment (1 minute)

```bash
# Start Odoo and PostgreSQL
docker-compose up -d

# Wait for services to start
sleep 10

# Check status
docker-compose ps
docker-compose logs web | grep "odoo.service.server: HTTP service"
```

**Access Odoo**:
- URL: http://localhost:8069
- Email: admin
- Password: admin

### 4. Set Up Development Tools (2 minutes)

```bash
# Install pre-commit hooks
pip3 install pre-commit
pre-commit install

# Run initial check
pre-commit run --all-files
```

**What you get**:
- Auto-formatting with Black and isort
- Linting with Pylint and Flake8
- OCA standards enforcement
- README generation

### 5. Create Your First Custom Module (5 minutes)

```bash
# Scaffold a custom module
mkdir -p addons/custom/my_custom_sales
cd addons/custom/my_custom_sales

# Create __manifest__.py
cat > __manifest__.py << 'EOF'
{
    'name': 'My Custom Sales',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'author': 'My Company',
    'website': 'https://mycompany.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF

# Create basic structure
mkdir -p models views security
touch models/__init__.py views/sale_order_views.xml security/ir.model.access.csv

# Restart Odoo to detect new module
cd ../../..
docker-compose restart web

# Install your module
docker-compose exec web odoo \
  -d erp-production_db \
  -i my_custom_sales \
  --stop-after-init
```

---

## 🌐 Production Deployment

### Deploy to DigitalOcean (10 minutes)

1. **Set up DigitalOcean credentials**:
   ```bash
   export DO_TOKEN="your_digitalocean_api_token"
   ```

2. **Configure Terraform**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars

   # Edit terraform.tfvars
   vim terraform.tfvars
   ```

3. **Deploy infrastructure**:
   ```bash
   terraform init
   terraform plan
   terraform apply -auto-approve
   ```

4. **Get deployment URL**:
   ```bash
   terraform output app_url
   # Output: https://erp.insightpulseai.net
   ```

5. **Verify deployment**:
   ```bash
   curl -f https://erp.insightpulseai.net/web/health
   # {"status": "pass"}
   ```

---

## 🔧 Common Tasks

### Add More OCA Modules

```bash
# Edit repos.yaml to add new modules
vim addons/oca/repos.yaml

# Example: Add inventory modules
cat >> addons/oca/repos.yaml << 'EOF'
stock-logistics-warehouse:
  url: https://github.com/OCA/stock-logistics-warehouse
  branch: "18.0"
  modules:
    - stock_available
    - stock_inventory_exclude_sublocation
EOF

# Re-vendor modules
python3 ../scripts/vendor_oca_enhanced.py \
  --repos addons/oca/repos.yaml \
  --target addons/oca
```

### Run Tests

```bash
# Run all tests
docker-compose exec web odoo \
  -d erp-production_db \
  --test-enable \
  --stop-after-init \
  --log-level=test

# Run tests for specific module
docker-compose exec web odoo \
  -d erp-production_db \
  --test-enable \
  --stop-after-init \
  -u my_custom_sales
```

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U odoo erp-production_db > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U odoo erp-production_db < backup_20251110.sql
```

### Update OCA Modules

```bash
# Pull latest OCA module versions
cd addons/oca
git -C account-financial-reporting pull origin 18.0
git -C helpdesk pull origin 18.0

# Update modules in Odoo
docker-compose exec web odoo \
  -d erp-production_db \
  -u all \
  --stop-after-init
```

---

## 🎯 Features Available

### Accounting (`--features accounting`)
- Financial reports and analysis
- Budget management
- Asset management
- Multi-currency support
- Advanced invoicing

### Helpdesk (`--features helpdesk`)
- Ticket management
- SLA tracking
- Customer portal
- Team management
- Automated routing

### Project Management (`--features project`)
- Task management
- Gantt charts
- Timeline views
- Resource allocation
- Time tracking

### HR Management (`--features hr`)
- Employee management
- Expense tracking
- Timesheet management
- Leave management
- Attendance tracking

### CRM (`--features crm`)
- Lead management
- Opportunity tracking
- Phone calls logging
- Claims management

### Inventory (`--features inventory`)
- Stock management
- Warehouse operations
- Picking workflows
- Inventory valuation

### Manufacturing (`--features manufacturing`)
- Bill of Materials
- Production orders
- Work centers
- Quality control

### E-Commerce (`--features ecommerce`)
- Online store
- Product catalog
- Shopping cart
- Payment integration

---

## 💰 Cost Breakdown

### Monthly Costs

| Item | Cost | Notes |
|------|------|-------|
| **DigitalOcean App Platform** | $24/month | 2x Professional XS instances |
| **Database** | Free | Using Supabase free tier |
| **Storage** | Included | 10GB included with App Platform |
| **Bandwidth** | Included | 1TB included |
| **SSL Certificate** | Free | Let's Encrypt auto-renewal |
| **Total** | **$24/month** | **$288/year** |

### vs. Odoo Enterprise

| Plan | Users | Annual Cost | Savings |
|------|-------|-------------|---------|
| **Odoo Enterprise** | 10 | $4,320 | - |
| **Odoo.sh Hosting** | - | $720 | - |
| **OCA + Self-Host** | Unlimited | $288 | **$4,752 (94%)** |

---

## 🆘 Troubleshooting

### Odoo won't start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Port 8069 already in use
lsof -i :8069
# Kill conflicting process or change port in docker-compose.yml

# 2. Database connection failed
docker-compose exec db pg_isready
# Restart database: docker-compose restart db

# 3. Module not found
# Check addons_path in config/odoo.conf
docker-compose exec web odoo --addons-path
```

### Pre-commit hooks failing

```bash
# Update hooks
pre-commit autoupdate

# Skip hooks temporarily (not recommended)
git commit --no-verify

# Fix issues automatically
pre-commit run --all-files
```

### OCA modules not installing

```bash
# Verify module compatibility
grep "'version'" addons/oca/*/manifest.py | grep -v "18.0"

# Check dependencies
python3 ../scripts/check-module-versions.sh

# Force reinstall
docker-compose exec web odoo \
  -d erp-production_db \
  -i module_name \
  --stop-after-init \
  --log-level=debug
```

---

## 📚 Next Steps

1. ✅ **Customize**: Add your custom modules
2. ✅ **Configure**: Set up company info, users, permissions
3. ✅ **Integrate**: Connect to external services (email, payment gateways)
4. ✅ **Deploy**: Push to production via CI/CD
5. ✅ **Monitor**: Set up logging and alerts
6. ✅ **Backup**: Schedule automated backups

## 🔗 Resources

- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Python OCA Tools](https://github.com/OCA/maintainer-tools)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)

---

**Questions?** Open an issue or check the main [SKILL.md](SKILL.md) for detailed workflows.
